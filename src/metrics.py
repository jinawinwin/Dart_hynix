from __future__ import annotations

from typing import Any


def number(value: str | None) -> int | None:
    if value is None:
        return None
    cleaned = str(value).replace(",", "").strip()
    if cleaned in {"", "-"}:
        return None
    try:
        return int(cleaned)
    except ValueError:
        return None


ACCOUNT_ALIASES = {
    "revenue": ["매출액", "수익(매출액)", "영업수익"],
    "operating_profit": ["영업이익", "영업이익(손실)"],
    "net_income": ["당기순이익", "당기순이익(손실)"],
    "assets": ["자산총계"],
    "liabilities": ["부채총계"],
    "equity": ["자본총계"],
    "cash": ["현금및현금성자산"],
    "operating_cash_flow": ["영업활동현금흐름"],
}


def _find_amount(rows: list[dict[str, Any]], aliases: list[str]) -> int | None:
    for row in rows:
        name = str(row.get("account_nm", "")).replace(" ", "")
        if any(alias.replace(" ", "") == name for alias in aliases):
            amount = number(row.get("thstrm_amount"))
            if amount is not None:
                return amount
    return None


def _ratio(numerator: int | None, denominator: int | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(numerator / denominator * 100, 2)


def calculate_headline_metrics(payload: dict[str, Any]) -> dict[str, Any]:
    rows = payload.get("list", [])
    result = {key: _find_amount(rows, aliases) for key, aliases in ACCOUNT_ALIASES.items()}
    result["operating_margin_pct"] = _ratio(
        result["operating_profit"], result["revenue"]
    )
    result["net_margin_pct"] = _ratio(result["net_income"], result["revenue"])
    result["debt_ratio_pct"] = _ratio(result["liabilities"], result["equity"])
    result["data_quality_note"] = (
        "본 스타터는 대표 계정명 기준 요약입니다. 운영 환경에서는 account_id 기반 "
        "매핑, 누적 분기 조정, 평균잔액 및 정정공시 처리가 필요합니다."
    )
    return result

