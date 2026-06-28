import numpy as np
import pandas as pd


def simulate_price_data(
    symbols,
    years: int = 4,
    trading_days_per_year: int = 252,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Simulate daily prices for each symbol using a simple geometric Brownian motion.
    This is our 'market model' with realistic-looking random walk prices.
    """
    np.random.seed(seed)
    n_days = years * trading_days_per_year

    # Use business days as index
    dates = pd.bdate_range(end=pd.Timestamp.today(), periods=n_days)
    prices = pd.DataFrame(index=dates)

    for sym in symbols:
        # Simple assumptions for all assets (can customize later)
        mu_annual = 0.08      # 8% expected annual return
        sigma_annual = 0.15   # 15% annual volatility
        dt = 1.0 / trading_days_per_year

        mu = mu_annual
        sigma = sigma_annual

        # Geometric Brownian motion
        shocks = np.random.normal(
            (mu - 0.5 * sigma**2) * dt,
            sigma * np.sqrt(dt),
            n_days,
        )
        s0 = 100.0  # starting price
        price_path = s0 * np.exp(np.cumsum(shocks))

        prices[sym] = price_path

    return prices
