# ネットワークに依存しない純粋なスクリーニングロジック（フィルタ・ソート）。
# yfinanceの通信部分（data.py）から切り離してあるので、単体テストしやすい。

SORT_OPTIONS = {
    "dividend_desc": ("dividend_yield", True),
    "per_asc": ("per", False),
    "pbr_asc": ("pbr", False),
    "market_cap_desc": ("market_cap", True),
    "roe_desc": ("roe", True),
    "volume_ratio_desc": ("volume_ratio", True),
}

DEFAULT_SORT = "dividend_desc"


def passes_criteria(row, criteria):
    """rowが指定された条件をすべて満たすか判定する。指標が取得できない(None)銘柄は除外する。"""
    if criteria.get("per_max") is not None:
        if row.get("per") is None or row["per"] > criteria["per_max"]:
            return False
    if criteria.get("pbr_max") is not None:
        if row.get("pbr") is None or row["pbr"] > criteria["pbr_max"]:
            return False
    if criteria.get("dividend_min") is not None:
        if row.get("dividend_yield") is None or row["dividend_yield"] < criteria["dividend_min"]:
            return False
    if criteria.get("market_cap_min") is not None:
        if row.get("market_cap") is None or row["market_cap"] < criteria["market_cap_min"]:
            return False
    if criteria.get("roe_min") is not None:
        if row.get("roe") is None or row["roe"] < criteria["roe_min"]:
            return False
    if criteria.get("volume_ratio_min") is not None:
        if row.get("volume_ratio") is None or row["volume_ratio"] < criteria["volume_ratio_min"]:
            return False
    if criteria.get("sector"):
        if row.get("sector") != criteria["sector"]:
            return False
    return True


def filter_rows(rows, criteria):
    return [row for row in rows if passes_criteria(row, criteria)]


def sort_rows(rows, sort_key=DEFAULT_SORT):
    """指標がNoneの銘柄は並び順に関わらず常に末尾に置く。"""
    field, higher_is_better = SORT_OPTIONS.get(sort_key, SORT_OPTIONS[DEFAULT_SORT])

    def key_fn(row):
        val = row.get(field)
        if val is None:
            return (1, 0)
        return (0, -val if higher_is_better else val)

    return sorted(rows, key=key_fn)
