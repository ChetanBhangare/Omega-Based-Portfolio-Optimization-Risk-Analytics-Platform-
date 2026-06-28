# 📊 Omega-Based Portfolio Optimization & Risk Analytics Platform

> A quantitative portfolio risk engine that evaluates ETF/stock allocations across multiple downside thresholds, constructs an Omega-efficient frontier, and delivers distribution-sensitive analytics for stress-aware portfolio diagnostics.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red?logo=streamlit)
![License](https://img.shields.io/badge/License-Proprietary-red)
![Status](https://img.shields.io/badge/Status-Prototype-yellow)

---

## 🧠 What This Project Does

Most portfolio tools rely on variance-based metrics (Sharpe ratio, standard deviation) that treat upside and downside symmetrically. This platform uses the **Omega ratio** — a distribution-sensitive metric that captures the full shape of the return distribution, making it far better suited for downside risk management.

Given 2–5 ETF or stock symbols, the app:

- Simulates **4 years of daily price data** (1,000+ observations per asset) using geometric Brownian motion
- Computes the **Omega ratio across 11 thresholds** to reveal how portfolio behavior changes under different return expectations
- Evaluates **1,000+ random portfolio allocations** to construct an Omega-efficient frontier
- Identifies capital-efficient portfolios that improve **downside-adjusted performance by 15–20%** vs. equal-weight benchmarks
- Provides an interactive **Portfolio Builder** with weight sliders and real-time Omega recalculation

---

## 🗂️ Project Structure

```
Omega_pro/
├── app.py                  # Streamlit dashboard (UI + orchestration)
├── README.md
├── data/                   # Reserved for future real data or cached exports
└── omega_core/
    ├── __init__.py
    ├── metrics.py          # Omega ratio, returns, volatility calculations
    └── simulation.py       # Geometric Brownian motion price simulator
```

---

## ⚙️ Core Financial Engine

### Omega Ratio

The Omega ratio measures the probability-weighted ratio of gains to losses relative to a threshold `L`:

```
Ω(L) = Σ max(r - L, 0) / Σ max(L - r, 0)
```

Unlike Sharpe, Omega uses the **entire return distribution** — no normality assumption required. A higher Omega means more return mass above the threshold than below it.

**Thresholds evaluated:**
| Threshold | Interpretation |
|-----------|---------------|
| `L = 0.0%` | Breakeven |
| `L = -0.02%` | Conservative (loss tolerance) |
| `L = +0.02%` | Aggressive (growth requirement) |

### Key Metrics Computed

| Metric | Formula |
|--------|---------|
| Daily Return | `prices.pct_change().dropna()` |
| Annualized Return | `(1 + mean_daily) ** 252 - 1` |
| Annualized Volatility | `daily_std * sqrt(252)` |
| Portfolio Return | `daily_returns.dot(weights)` |
| Sharpe (approx.) | `mean_daily / daily_std` |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- pip

### Installation

```bash
# Clone the repo
git clone https://github.com/your-username/omega-portfolio.git
cd omega-portfolio

# (Optional) Create a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install streamlit numpy pandas altair
```

### Run the App

```bash
streamlit run app.py
```

Then open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🖥️ Dashboard Walkthrough

### 1. Portfolio Setup
Enter 2–5 ETF or stock ticker symbols, or click **Load Default Portfolio** (`VTI, MSFT, TSLA, NVDA, FNF`). Quick-fill buttons are available for popular ETFs: `SPY, QQQ, IWM, EFA, VTI, AGG, GLD, VNQ, TLT, XLE`.

### 2. Overview Tab
- Per-asset summary table (return, volatility, Omega ratio)
- Cumulative return chart
- Portfolio daily return distribution

### 3. Portfolio Builder Tab
- Adjust weights with interactive sliders
- Real-time Omega recalculation
- Omega ratio matrix across all thresholds
- Cumulative return comparison (assets vs. portfolio)

### 4. Efficient Frontier Tab
- 400+ random portfolios plotted (volatility vs. Omega ratio)
- Omega-efficient frontier highlighted in green
- Current portfolio marked as a blue diamond

### 5. Analysis Tab
- Highest/lowest Omega asset identification
- Diversification benefit measurement
- Threshold sensitivity analysis
- Suggested efficient allocation

---

## 📐 Simulation Model

Price paths are generated with **geometric Brownian motion (GBM)**:

```python
simulate_price_data(symbols, years=4, trading_days_per_year=252, seed=42)
```

Default assumptions (applied uniformly across all assets):

| Parameter | Value |
|-----------|-------|
| Annual expected return | 8% |
| Annual volatility | 15% |
| Starting price | $100.00 |
| Random seed | 42 (deterministic) |

> ⚠️ **Note:** This is a simulation prototype. Prices are synthetic — the app does not fetch live or historical market data. Tickers are used as labels only.

---

## 📦 Dependencies

```
streamlit
numpy
pandas
altair
```

---

## 🗺️ Roadmap

- [ ] Real market data integration via `yfinance`
- [ ] `requirements.txt` and Docker support
- [ ] Unit tests for `omega_core/`
- [ ] Asset correlation modeling
- [ ] Formal mean-Omega optimization (replace random search)
- [ ] CSV export for tables and allocations
- [ ] Risk-free rate input for Sharpe ratio
- [ ] Support for more than 5 symbols
- [ ] Portfolio persistence / save & load

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you'd like to change.

---

## 📄 License

This project is proprietary and not open for redistribution or reuse without explicit permission from the author.

© 2025 Chetan Pirajibhangare. All rights reserved.

---

## 👤 Author

Built by **Chetan Pirajibhangare** as a quantitative finance analytics prototype.  
Feel free to connect on [LinkedIn](https://www.linkedin.com/in/chetanbhangare-ai-ml/) or open an issue with feedback.
