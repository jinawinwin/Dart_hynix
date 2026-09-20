from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from .dart_client import DartAPIError, DartClient, write_json
from .metrics import calculate_headline_metrics


REPORT_NAMES = {
    "11011": "사업보고서",
    "11012": "반기보고서",
    "11013": "1분기보고서",
    "11014": "3분기보고서",
}


def default_business_year() -> str:
    now = datetime.now()
    return str(now.year - 1 if now.month <= 3 else now.year)


def comma(value: object) -> str:
    return "-" if value is None else f"{value:,}" if isinstance(value, int) else str(value)


def render_report(company: dict, metadata: dict, metrics: dict) -> str:
    lines = [
        f"# {company['name']} 재무분석",
        "",
        f"- 종목코드: `{company['stock_code']}`",
        f"- DART 고유번호: `{metadata['corp_code']}`",
        f"- 사업연도: {metadata['business_year']}",
        f"- 보고서: {REPORT_NAMES[metadata['report_code']]} (`{metadata['report_code']}`)",
        f"- 재무제표: {'연결' if metadata['fs_div'] == 'CFS' else '별도'}",
        f"- 생성시각(UTC): {metadata['generated_at']}",
        "",
        "## 핵심 수치",
        "",
        "| 지표 | 값 |",
        "|---|---:|",
        f"| 매출액 | {comma(metrics['revenue'])} |",
        f"| 영업이익 | {comma(metrics['operating_profit'])} |",
        f"| 당기순이익 | {comma(metrics['net_income'])} |",
        f"| 영업현금흐름 | {comma(metrics['operating_cash_flow'])} |",
        f"| 자산총계 | {comma(metrics['assets'])} |",
        f"| 부채총계 | {comma(metrics['liabilities'])} |",
        f"| 자본총계 | {comma(metrics['equity'])} |",
        "",
        "## 핵심 비율",
        "",
        "| 지표 | 값 |",
        "|---|---:|",
        f"| 영업이익률 | {comma(metrics['operating_margin_pct'])}% |",
        f"| 순이익률 | {comma(metrics['net_margin_pct'])}% |",
        f"| 부채비율 | {comma(metrics['debt_ratio_pct'])}% |",
        "",
        f"> {metrics['data_quality_note']}",
        "",
    ]
    return "\n".join(lines)


def run(config_path: Path, business_year: str, report_code: str, fs_div: str) -> None:
    api_key = os.environ.get("DART_API_KEY", "")
    client = DartClient(api_key)
    config = json.loads(config_path.read_text(encoding="utf-8"))
    root = config_path.parent.parent

    for company in config.get("companies", []):
        if not company.get("enabled", True):
            continue
        stock_code = company["stock_code"]
        corp_code = client.corp_code_for_stock(stock_code)
        payload = client.full_financial_statements(
            corp_code, business_year, report_code, fs_div
        )
        metadata = {
            "company": company["name"],
            "stock_code": stock_code,
            "corp_code": corp_code,
            "business_year": business_year,
            "report_code": report_code,
            "fs_div": fs_div,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        raw_path = root / "data" / "raw" / stock_code / business_year / f"{report_code}-{fs_div}.json"
        write_json(raw_path, payload)

        metrics = calculate_headline_metrics(payload)
        processed = {"metadata": metadata, "metrics": metrics}
        processed_path = root / "data" / "processed" / stock_code / f"{business_year}-{report_code}-{fs_div}.json"
        write_json(processed_path, processed)

        report_path = root / "reports" / stock_code / f"{business_year}-{report_code}-{fs_div}.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(render_report(company, metadata, metrics), encoding="utf-8")
        print(json.dumps({"company": company["name"], "report": str(report_path)}, ensure_ascii=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="OpenDART 재무제표 수집 스타터")
    parser.add_argument("--config", default="config/companies.json")
    parser.add_argument("--year", default=default_business_year())
    parser.add_argument("--report-code", choices=REPORT_NAMES, default="11011")
    parser.add_argument("--fs-div", choices=["CFS", "OFS"], default="CFS")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    try:
        run(Path(args.config), args.year, args.report_code, args.fs_div)
    except (DartAPIError, ValueError) as exc:
        raise SystemExit(f"실행 실패: {exc}") from exc
