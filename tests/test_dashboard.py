from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.build_dashboard import build, load_rows


class DashboardTests(unittest.TestCase):
    def test_prefers_consolidated_and_groups_quarters(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "processed" / "000660"
            source.mkdir(parents=True)
            base = {
                "metadata": {
                    "company": "SK하이닉스", "stock_code": "000660",
                    "business_year": "2025", "report_code": "11013",
                    "generated_at": "2026-01-01T00:00:00+00:00",
                },
                "metrics": {"revenue": 1},
            }
            for fs_div in ("OFS", "CFS"):
                payload = json.loads(json.dumps(base))
                payload["metadata"]["fs_div"] = fs_div
                (source / f"2025-11013-{fs_div}.json").write_text(
                    json.dumps(payload, ensure_ascii=False), encoding="utf-8"
                )
            rows = load_rows(root / "processed")
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["fs_div"], "CFS")
            self.assertEqual(rows[0]["category"], "quarterly")

            output = root / "dashboard-data.js"
            result = build(root / "processed", output)
            self.assertEqual(len(result["rows"]), 1)
            self.assertTrue(output.read_text(encoding="utf-8").startswith("window.DASHBOARD_DATA = "))


if __name__ == "__main__":
    unittest.main()
