from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from risk_engine.config import Config
from risk_engine.data.market_data import DataRequest, compute_log_returns, get_prices
from risk_engine.reporting.artifacts import plot_drawdown, save_metrics_json, save_series_csv
from risk_engine.risk.core import (
    covariance_matrix,
    drawdown,
    historical_expected_shortfall,
    historical_var,
    max_drawdown,
    parametric_var,
    portfolio_returns,
    portfolio_volatility,
)

# Take a config and run all the risk metrics, and save them into a folder.

def run_analysis(cfg: Config, run_dir: Path) -> dict:
    req = DataRequest(
        tickers=cfg.tickers,
        start=cfg.start,
        end=cfg.end,
        interval=cfg.data_interval,
        auto_adjust=cfg.data_auto_adjust,
    )

    prices = get_prices(Path(cfg.data_cache_dir), req, force_refresh=cfg.data_force_refresh)
    rets = compute_log_returns(prices)

    w = pd.Series(1 / len(cfg.tickers), index=cfg.tickers)

    cov = covariance_matrix(rets)
    vol_daily = portfolio_volatility(w, cov)
    vol_annual = float(vol_daily * np.sqrt(252))

    port_ret = portfolio_returns(w, rets)
    dd = drawdown(port_ret)
    mdd = max_drawdown(port_ret)

    var_95 = historical_var(port_ret, 0.95)
    es_95 = historical_expected_shortfall(port_ret, 0.95)
    pvar_95 = parametric_var(port_ret, 0.95)

    metrics = {
        "tickers": cfg.tickers,
        "start": cfg.start,
        "end": cfg.end,
        "vol_daily": vol_daily,
        "vol_annual": vol_annual,
        "max_drawdown": mdd,
        "var_95": var_95,
        "es_95": es_95,
        "parametric_var_95": pvar_95,
    }

    out_dir = run_dir / "outputs"
    out_dir.mkdir(exist_ok=True)

    save_metrics_json(out_dir / "metrics.json", metrics)
    save_series_csv(out_dir / "portfolio_returns.csv", port_ret, "portfolio_return")
    save_series_csv(out_dir / "drawdown.csv", dd, "drawdown")
    plot_drawdown(out_dir / "drawdown.png", dd)

    return metrics
