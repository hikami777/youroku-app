import os

from flask import Flask, render_template, request

from tickers import TSE_TICKERS
from data import fetch_all
from logic import filter_rows, sort_rows, SORT_OPTIONS, DEFAULT_SORT

app = Flask(__name__)

TICKERS_BY_CODE = {t["code"]: t for t in TSE_TICKERS}
SECTORS = sorted({t["sector"] for t in TSE_TICKERS})

SORT_LABELS = {
    "dividend_desc": "配当利回り（高い順）",
    "per_asc": "PER（低い順）",
    "pbr_asc": "PBR（低い順）",
    "market_cap_desc": "時価総額（大きい順）",
    "roe_desc": "ROE（高い順）",
    "volume_ratio_desc": "出来高急増（平均比が大きい順）",
}


def _to_float(value):
    if value is None or value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


@app.route("/")
def index():
    return render_template(
        "index.html",
        sectors=SECTORS,
        sort_options=SORT_LABELS,
        default_sort=DEFAULT_SORT,
    )


@app.route("/screen", methods=["POST"])
def screen():
    criteria = {
        "per_max": _to_float(request.form.get("per_max")),
        "pbr_max": _to_float(request.form.get("pbr_max")),
        "dividend_min": _to_float(request.form.get("dividend_min")),
        "market_cap_min": _to_float(request.form.get("market_cap_min")),
        "roe_min": _to_float(request.form.get("roe_min")),
        "volume_ratio_min": _to_float(request.form.get("volume_ratio_min")),
        "sector": request.form.get("sector") or None,
    }
    sort_key = request.form.get("sort") or DEFAULT_SORT
    if sort_key not in SORT_OPTIONS:
        sort_key = DEFAULT_SORT

    target_codes = [
        t["code"] for t in TSE_TICKERS if not criteria["sector"] or t["sector"] == criteria["sector"]
    ]

    fetched = fetch_all(target_codes)
    rows = []
    for data in fetched:
        meta = TICKERS_BY_CODE.get(data["code"])
        if not meta:
            continue
        rows.append({**data, "name": meta["name"], "sector": meta["sector"]})

    matched = sort_rows(filter_rows(rows, criteria), sort_key)

    return render_template(
        "results.html",
        rows=matched,
        criteria=criteria,
        sort_key=sort_key,
        sort_label=SORT_LABELS.get(sort_key, sort_key),
        total_targets=len(target_codes),
        fetched_count=len(fetched),
        matched_count=len(matched),
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(debug=True, host="0.0.0.0", port=port)
