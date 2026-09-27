from __future__ import annotations

import unittest

from src.dart_client import DartAPIError
from src.main import _fetch_statement


class FakeClient:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def full_financial_statements(
        self, corp_code: str, business_year: str, report_code: str, fs_div: str
    ) -> dict:
        self.calls.append(fs_div)
        if fs_div == "CFS":
            raise DartAPIError("자료 없음", status="013")
        return {"status": "000", "list": []}


class CollectionTests(unittest.TestCase):
    def test_auto_falls_back_to_separate_statement(self) -> None:
        client = FakeClient()
        payload, fs_div = _fetch_statement(client, "00164779", "2010", "11011", "AUTO")
        self.assertEqual(payload["status"], "000")
        self.assertEqual(fs_div, "OFS")
        self.assertEqual(client.calls, ["CFS", "OFS"])


if __name__ == "__main__":
    unittest.main()
