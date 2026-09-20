from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen
from xml.etree import ElementTree


BASE_URL = "https://opendart.fss.or.kr/api"


class DartAPIError(RuntimeError):
    pass


class DartClient:
    def __init__(self, api_key: str, timeout: int = 30) -> None:
        if not api_key:
            raise ValueError("DART_API_KEY가 비어 있습니다.")
        self.api_key = api_key
        self.timeout = timeout

    def _get_bytes(self, endpoint: str, **params: str) -> bytes:
        query = urlencode({"crtfc_key": self.api_key, **params})
        try:
            with urlopen(f"{BASE_URL}/{endpoint}?{query}", timeout=self.timeout) as response:
                return response.read()
        except (HTTPError, URLError) as exc:
            raise DartAPIError(f"OpenDART 연결 실패: {exc}") from exc

    def _get_json(self, endpoint: str, **params: str) -> dict[str, Any]:
        payload = json.loads(self._get_bytes(endpoint, **params).decode("utf-8"))
        status = payload.get("status")
        if status != "000":
            raise DartAPIError(
                f"OpenDART 오류 status={status}: {payload.get('message', '알 수 없는 오류')}"
            )
        return payload

    def corporation_codes(self) -> list[dict[str, str]]:
        content = self._get_bytes("corpCode.xml")
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            xml_bytes = archive.read("CORPCODE.xml")
        root = ElementTree.fromstring(xml_bytes)
        rows: list[dict[str, str]] = []
        for item in root.findall("list"):
            rows.append({child.tag: (child.text or "").strip() for child in item})
        return rows

    def corp_code_for_stock(self, stock_code: str) -> str:
        for item in self.corporation_codes():
            if item.get("stock_code") == stock_code:
                return item["corp_code"]
        raise DartAPIError(f"종목코드 {stock_code}의 DART 고유번호를 찾지 못했습니다.")

    def full_financial_statements(
        self,
        corp_code: str,
        business_year: str,
        report_code: str,
        fs_div: str = "CFS",
    ) -> dict[str, Any]:
        return self._get_json(
            "fnlttSinglAcntAll.json",
            corp_code=corp_code,
            bsns_year=business_year,
            reprt_code=report_code,
            fs_div=fs_div,
        )


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
