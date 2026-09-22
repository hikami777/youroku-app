# yfinance経由で東証銘柄の指標を取得する。ネットワークI/Oはここに閉じ込め、
# フィルタ・ソートのロジック（logic.py）とは分離してある。

import logging
import time
import concurrent.futures

import yfinance as yf

CACHE_TTL_SECONDS = 30 * 60  # 30分キャッシュ（同じ銘柄への再問い合わせを減らす）
# Yahoo! Finance側のレート制限に引っかかりやすいため、並列数は控えめにする
MAX_WORKERS = 4
RETRY_COUNT = 2
RETRY_BACKOFF_SECONDS = 1.5

logger = logging.getLogger(__name__)

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
    volume = info.get("volume") or info.get("regularMarketVolume")
    average_volume = info.get("averageVolume") or info.get("averageVolume10days")

    return {
        "code": code,
        "price": info.get("currentPrice") or info.get("regularMarketPrice"),
        "per": info.get("trailingPE"),
        "pbr": info.get("priceToBook"),
        "dividend_yield": _normalize_percent(info.get("dividendYield")),
        "market_cap": market_cap / 1e8 if market_cap else None,  # 億円換算
        "roe": _normalize_percent(info.get("returnOnEquity")),
        # 直近出来高が平均出来高の何倍か（出来高急増の目安。1.0なら平均並み）
        "volume_ratio": volume / average_volume if volume and average_volume else None,
    }


def get_stock_data(code, force_refresh=False):
    """1銘柄分のデータをキャッシュ経由で取得する。取得に失敗した場合はNoneを返す。"""
    now = time.time()
    cached = _cache.get(code)
    if not force_refresh and cached and now - cached[1] < CACHE_TTL_SECONDS:
        return cached[0]

    data = None
    last_error = None
    for attempt in range(1, RETRY_COUNT + 1):
        try:
            data = _fetch_from_source(code)
            break
        except Exception as exc:  # yfinance/Yahoo側のレート制限やタイムアウトなど
            last_error = exc
            if attempt < RETRY_COUNT:
                time.sleep(RETRY_BACKOFF_SECONDS)

    if data is None and last_error is not None:
        logger.warning("stock_screener: failed to fetch %s: %s: %s", code, type(last_error).__name__, last_error)

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
