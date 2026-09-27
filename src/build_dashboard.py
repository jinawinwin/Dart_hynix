from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = ROOT / "data" / "processed"
OUTPUT = ROOT / "docs" / "dashboard-data.js"

REPORT_META = {
    "11011": ("annual", "사업보고서", 4),
    "11012": ("half-year", "반기보고서", 2),
    "11013": ("quarterly", "1분기보고서", 1),
    "11014": ("quarterly", "3분기보고서", 3),
}


def load_rows(processed_dir: Path = PROCESSED_DIR) -> list[dict[str, Any]]:
    selected: dict[tuple[str, str, str], dict[str, Any]] = {}
    for path in sorted(processed_dir.glob("*/*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        metadata = payload.get("metadata", {})
        report_code = metadata.get("report_code")
        if report_code not in REPORT_META:
            continue
        category, report_name, period_order = REPORT_META[report_code]
        metrics = payload.get("metrics", {})
        row = {
            "company": metadata.get("company"),
            "stock_code": metadata.get("stock_code"),
            "year": int(metadata["business_year"]),
            "report_code": report_code,
            "report_name": report_name,
            "period_order": period_order,
            "category": category,
            "fs_div": metadata.get("fs_div"),
            "generated_at": metadata.get("generated_at"),
            **{key: metrics.get(key) for key in (
                "revenue", "operating_profit", "net_income",
                "operating_cash_flow", "assets", "liabilities", "equity",
                "operating_margin_pct", "net_margin_pct", "debt_ratio_pct",
            )},
        }
        key = (str(row["stock_code"]), str(row["year"]), report_code)
        current = selected.get(key)
        if current is None or (current.get("fs_div") == "OFS" and row["fs_div"] == "CFS"):
            selected[key] = row
    return sorted(
        selected.values(),
        key=lambda row: (row["year"], row["period_order"]),
        reverse=True,
    )


def build(processed_dir: Path = PROCESSED_DIR, output: Path = OUTPUT) -> dict[str, Any]:
    rows = load_rows(processed_dir)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "OpenDART",
        "currency": "KRW",
        "rows": rows,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    output.write_text(f"window.DASHBOARD_DATA = {serialized};\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "rows": len(rows)}, ensure_ascii=False))
    return payload


if __name__ == "__main__":
    build()
