import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logic import filter_rows, sort_rows, passes_criteria


def make_row(code, per=None, pbr=None, dividend_yield=None, market_cap=None, roe=None, sector="電気機器"):
    return {
        "code": code,
        "per": per,
        "pbr": pbr,
        "dividend_yield": dividend_yield,
        "market_cap": market_cap,
        "roe": roe,
        "sector": sector,
    }


def test_passes_criteria_with_no_filters():
    row = make_row("0001")
    assert passes_criteria(row, {}) is True


def test_passes_criteria_per_max():
    row = make_row("0001", per=12.0)
    assert passes_criteria(row, {"per_max": 15.0}) is True
    assert passes_criteria(row, {"per_max": 10.0}) is False


def test_passes_criteria_excludes_missing_metric():
    row = make_row("0001", per=None)
    assert passes_criteria(row, {"per_max": 15.0}) is False


def test_passes_criteria_sector_filter():
    row = make_row("0001", sector="銀行")
    assert passes_criteria(row, {"sector": "銀行"}) is True
    assert passes_criteria(row, {"sector": "自動車"}) is False


def test_filter_rows_combines_multiple_conditions():
    rows = [
        make_row("A", per=10, pbr=1.0, dividend_yield=4.0),
        make_row("B", per=25, pbr=1.0, dividend_yield=4.0),
        make_row("C", per=10, pbr=3.0, dividend_yield=4.0),
        make_row("D", per=10, pbr=1.0, dividend_yield=1.0),
    ]
    criteria = {"per_max": 15, "pbr_max": 2.0, "dividend_min": 3.0}
    matched = filter_rows(rows, criteria)
    assert [r["code"] for r in matched] == ["A"]


def test_sort_rows_dividend_desc_puts_none_last():
    rows = [
        make_row("A", dividend_yield=2.0),
        make_row("B", dividend_yield=None),
        make_row("C", dividend_yield=5.0),
    ]
    sorted_rows = sort_rows(rows, "dividend_desc")
    assert [r["code"] for r in sorted_rows] == ["C", "A", "B"]


def test_sort_rows_per_asc_puts_none_last():
    rows = [
        make_row("A", per=20.0),
        make_row("B", per=None),
        make_row("C", per=8.0),
    ]
    sorted_rows = sort_rows(rows, "per_asc")
    assert [r["code"] for r in sorted_rows] == ["C", "A", "B"]


def test_sort_rows_unknown_key_falls_back_to_default():
    rows = [
        make_row("A", dividend_yield=1.0),
        make_row("C", dividend_yield=5.0),
    ]
    sorted_rows = sort_rows(rows, "not_a_real_key")
    assert [r["code"] for r in sorted_rows] == ["C", "A"]
