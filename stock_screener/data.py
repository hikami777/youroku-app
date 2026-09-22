# yfinance経由で東証銘柄の指標を取得する。ネットワークI/Oはここに閉じ込め、
# フィルタ・ソートのロジック（logic.py）とは分離してある。

import time
import concurrent.futures

import yfinance as yf

CACHE_TTL_SECONDS = 30 * 60  # 30分キャッシュ（同じ銘柄への再問い合わせを減らす）
MAX_WORKERS = 10

_cache = {}


def _normalize_percent(value):
    """yfinanceのdividendYield等は小数(0.025)で返る場合とパーセント値で返る場合があるため正規化する。"""
    if value is None:
        return None
    return value * 100 if value < 1 else value


def _fetch_from_source(code):
    symbol = f"{code}.T"
    ticker = yf.Ticker(symbol)
    info = ticker.info
    if not info or info.get("regularMarketPrice") is None and info.get("currentPrice") is None:
        return None

    market_cap = info.get("marketCap")
    return {
        "code": code,
        "price": info.get("currentPrice") or info.get("regularMarketPrice"),
        "per": info.get("trailingPE"),
        "pbr": info.get("priceToBook"),
        "dividend_yield": _normalize_percent(info.get("dividendYield")),
        "market_cap": market_cap / 1e8 if market_cap else None,  # 億円換算
        "roe": _normalize_percent(info.get("returnOnEquity")),
    }


def get_stock_data(code, force_refresh=False):
    """1銘柄分のデータをキャッシュ経由で取得する。取得に失敗した場合はNoneを返す。"""
    now = time.time()
    cached = _cache.get(code)
    if not force_refresh and cached and now - cached[1] < CACHE_TTL_SECONDS:
        return cached[0]

    try:
        data = _fetch_from_source(code)
    except Exception:
        data = None

    if data:
        _cache[code] = (data, now)
    return data


def fetch_all(codes, max_workers=MAX_WORKERS):
    """複数銘柄を並列取得する。取得できなかった銘柄は結果に含まれない。"""
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_code = {executor.submit(get_stock_data, code): code for code in codes}
        for future in concurrent.futures.as_completed(future_to_code):
            data = future.result()
            if data:
                results.append(data)
    return results
