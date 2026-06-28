import numpy as np
import pandas as pd


def compute_daily_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Convert price DataFrame into daily returns."""
    return prices.pct_change().dropna()


def omega_ratio(returns: pd.Series, L: float = 0.0) -> float:
    """
    Omega ratio at threshold L.
    L is in simple return space (e.g. 0.0 for breakeven, 0.0005 for 0.05%).
    """
    x = returns - L
    gains = np.clip(x, 0, None).sum()
    losses = np.clip(-x, 0, None).sum()
    return gains / losses if losses > 0 else float("nan")


def asset_summary(prices: pd.DataFrame, L: float = 0.0) -> pd.DataFrame:
    """
    Build a summary table similar to your UI:
    symbol, latest price, daily avg, annual return, daily stddev,
    annual volatility, Omega(L).
    """
    rets = compute_daily_returns(prices)
    ann_factor = 252  # trading days per year

    rows = []
    for sym in prices.columns:
        r = rets[sym]
        latest_price = prices[sym].iloc[-1]
        daily_avg = r.mean()
        ann_return = (1 + daily_avg) ** ann_factor - 1
        daily_std = r.std()
        ann_vol = daily_std * np.sqrt(ann_factor)
        om = omega_ratio(r, L=L)

        rows.append(
            dict(
                Symbol=sym,
                Latest_Price=latest_price,
                Daily_Avg=daily_avg,
                Ann_Return=ann_return,
                Daily_StdDev=daily_std,
                Ann_Volatility=ann_vol,
                Omega_L0=om,
            )
        )

    return pd.DataFrame(rows)
