from __future__ import annotations

"""
Core risk math for the MVP risk engine.

This file focuses on:
1) Covariance matrix of returns (Σ)
2) Portfolio variance:     wᵀ Σ w
3) Portfolio volatility:   sqrt(wᵀ Σ w)

"""

from pathlib import Path

import numpy as np
import pandas as pd

from risk_engine.data.market_data import DataRequest, compute_log_returns, get_prices

from scipy.stats import norm

def covariance_matrix(returns: pd.DataFrame) -> pd.DataFrame:
    return returns.cov()


def portfolio_variance(weights: pd.Series, cov: pd.DataFrame) -> float:
    w = weights.reindex(cov.columns).to_numpy()
    sigma = cov.to_numpy()
    return float(w.T @ sigma @ w)


def portfolio_volatility(weights: pd.Series, cov: pd.DataFrame) -> float:
    return float(np.sqrt(portfolio_variance(weights, cov)))


def portfolio_returns(weights: pd.Series, returns: pd.DataFrame) -> pd.Series:
    w = weights.reindex(returns.columns).to_numpy()
    r = returns.to_numpy()
    port_ret = r @ w
    return pd.Series(port_ret, index=returns.index)

def cumulative_wealth(returns: pd.Series) -> pd.Series:
    return (1 + returns).cumprod()

def drawdown(returns: pd.Series) -> pd.Series:
    wealth = cumulative_wealth(returns)
    running_max = wealth.cummax()
    dd = wealth / running_max - 1
    return dd

def max_drawdown(returns: pd.Series) -> float:
    dd = drawdown(returns)
    return float(dd.min())

def historical_var(returns: pd.Series, level: float = 0.95) -> float:
    """
    Historical Value at Risk (VaR).

    level=0.95 means 95% VaR (5% left tail).
    """
    alpha = 1 - level
    return float(np.percentile(returns, alpha * 100))

def historical_expected_shortfall(returns: pd.Series, level: float = 0.95) -> float:
    """
    Historical Expected Shortfall (Conditional VaR).
    Average of returns worse than the VaR threshold.
    """
    var = historical_var(returns, level)
    tail_losses = returns[returns <= var]
    return float(tail_losses.mean())

def parametric_var(returns: pd.Series, level: float = 0.95) -> float:
    """
    Parametric (Normal) VaR assuming returns are normally distributed.
    """
    mu = returns.mean()
    sigma = returns.std()
    alpha = 1 - level
    z = norm.ppf(alpha)
    return float(mu + z * sigma)


if __name__ == "__main__":
    req = DataRequest(
        tickers=["AAPL", "MSFT", "NVDA"],
        start="2022-01-01",
        end="2023-01-01",
        interval="1d",
        auto_adjust=True,
    )

    prices = get_prices(Path("data/cache"), req, force_refresh=False)
    rets = compute_log_returns(prices)
    cov = covariance_matrix(rets)

    w = pd.Series(1 / len(req.tickers), index=req.tickers)

    vol_daily = portfolio_volatility(w, cov)
    vol_annual = vol_daily * np.sqrt(252)

    port_ret = portfolio_returns(w, rets)
    dd_series = drawdown(port_ret)
    mdd = max_drawdown(port_ret)

    var_95 = historical_var(port_ret, 0.95)
    es_95 = historical_expected_shortfall(port_ret, 0.95)
    param_var_95 = parametric_var(port_ret, 0.95)

    print("Prices shape:", prices.shape)
    print("Returns shape:", rets.shape)
    print("Daily volatility:", vol_daily)
    print("Annualised volatility:", vol_annual)
    print("Max drawdown:", mdd)
    
    print("95% VaR:", var_95)
    print("95% Expected Shortfall:", es_95)
    print("95% Parametric VaR:", param_var_95)