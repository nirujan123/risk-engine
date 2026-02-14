from __future__ import annotations

import hashlib
import pickle
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import yfinance as yf
import numpy as np

#Note: When requesting market prices, this file makes sure I get a clean and consistent price matrix

@dataclass(frozen=True)
class DataRequest:
    tickers: list[str]
    start: str
    end: str
    interval: str
    auto_adjust: bool

#If downloaded, reuse.
def cache_path(cache_dir: Path, req: DataRequest) -> Path:
    """
    Create a deterministic cache filename for a given data request.
    Same request -> same filename.
    """
    cache_dir.mkdir(parents=True, exist_ok=True)

    
    tickers_sorted = ",".join(sorted(req.tickers))
    raw_key = f"{tickers_sorted}|{req.start}|{req.end}|{req.interval}|{req.auto_adjust}"

    
    key_hash = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()[:16]
    return cache_dir / f"prices_{key_hash}.pkl"


def save_cache(path: Path, df: pd.DataFrame) -> None:
    """Save a pandas DataFrame to disk using pickle."""
    with path.open("wb") as f:
        pickle.dump(df, f)


def load_cache(path: Path) -> pd.DataFrame | None:
    """Load cached DataFrame if it exists, otherwise return None."""
    if not path.exists():
        return None
    with path.open("rb") as f:
        return pickle.load(f)

#Standardisation as yfinance returns different formats
def _extract_close_matrix(raw: pd.DataFrame, tickers: list[str]) -> pd.DataFrame:
    """
    Convert yfinance output into a clean price matrix:
    index = Date
    columns = tickers
    values = Close (already adjusted if auto_adjust=True)
    """
    if raw is None or raw.empty:
        raise ValueError("yfinance returned no data (empty DataFrame). Check tickers/date range.")


    if isinstance(raw.columns, pd.MultiIndex):
        if "Close" not in raw.columns.get_level_values(0):
            raise ValueError("Expected 'Close' in yfinance MultiIndex columns.")
        close = raw["Close"].copy()  
    else:
        
        if "Close" not in raw.columns:
            raise ValueError("Expected 'Close' column in yfinance output.")
        if len(tickers) != 1:
            raise ValueError("Unexpected format: single-level columns but multiple tickers requested.")
        close = raw[["Close"]].copy()
        close.columns = tickers

    
    close = close.sort_index()
    close.index = pd.to_datetime(close.index)

    close = close.reindex(columns=tickers)

    return close


def download_prices(req: DataRequest) -> pd.DataFrame:
    """
    Download OHLCV data using yfinance and return a clean Close price matrix.

    """
    tickers_str = " ".join(req.tickers)

    raw = yf.download(
        tickers=tickers_str,
        start=req.start,
        end=req.end,
        interval=req.interval,
        auto_adjust=req.auto_adjust,
        actions=False,
        progress=False,
        group_by="column",
        threads=True,
    )

    return _extract_close_matrix(raw, req.tickers)


def get_prices(cache_dir: Path, req: DataRequest, force_refresh: bool = False) -> pd.DataFrame:
    """
    Main entry point:
    - if cached file exists and force_refresh=False -> load it
    - otherwise -> download, save, return
    """
    path = cache_path(cache_dir, req)

    if not force_refresh:
        cached = load_cache(path)
        if cached is not None:
            return cached

    prices = download_prices(req)
    save_cache(path, prices)
    return prices

def compute_simple_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """
    Compute simple percentage returns:
    R_t = P_t / P_{t-1} - 1
    """
    returns = np.log(prices / prices.shift(1))
    return returns.dropna()

def compute_log_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """
    Compute log returns:
    r_t = ln(P_t / P_{t-1})
    """
    returns = np.log(prices / prices.shift(1))
    return returns.dropna()


if __name__ == "__main__":
    req = DataRequest(
        tickers=["AAPL", "MSFT"],
        start="2022-01-01",
        end="2023-01-01",
        interval="1d",
        auto_adjust=True,
    )

    prices = get_prices(Path("data/cache"), req)
    simple = compute_simple_returns(prices)
    log_ret = compute_log_returns(prices)

    print("Prices shape:", prices.shape)
    print("Simple returns shape:", simple.shape)
    print(simple.head())
