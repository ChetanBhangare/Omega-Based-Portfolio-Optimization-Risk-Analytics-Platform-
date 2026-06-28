import numpy as np
import pandas as pd
import streamlit as st

from omega_core.simulation import simulate_price_data
from omega_core.metrics import (
    compute_daily_returns,
    omega_ratio,
    asset_summary,
)

# ---------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------
st.set_page_config(
    page_title="Omega Ratio Portfolio Analysis",
    layout="wide",
)

# ---------------------------------------------------------------------
# Helpers & initial session state
# ---------------------------------------------------------------------
DEFAULT_SYMBOLS = ["VTI", "MSFT", "TSLA", "NVDA", "FNF"]
POPULAR_ETFS = ["SPY", "QQQ", "IWM", "EFA", "VTI", "AGG", "GLD", "VNQ", "TLT", "XLE"]

if "prices" not in st.session_state:
    st.session_state.prices = None

if "analysis_ready" not in st.session_state:
    st.session_state.analysis_ready = False

# ensure 5 symbol slots exist in state
for i in range(5):
    key = f"sym_{i}"
    if key not in st.session_state:
        st.session_state[key] = ""


def fill_defaults():
    for i, sym in enumerate(DEFAULT_SYMBOLS):
        st.session_state[f"sym_{i}"] = sym
    st.session_state.analysis_ready = False


def clear_all():
    for i in range(5):
        st.session_state[f"sym_{i}"] = ""
    st.session_state.prices = None
    st.session_state.analysis_ready = False


def add_popular_symbol(sym: str):
    """Put popular ETF into the next empty slot."""
    for i in range(5):
        key = f"sym_{i}"
        if st.session_state[key] == "":
            st.session_state[key] = sym
            break


# ---------------------------------------------------------------------
# Layout: Portfolio Setup
# ---------------------------------------------------------------------
st.title("Omega Ratio Portfolio Analysis")

st.markdown("### 📊 Portfolio Setup")
st.caption("Enter 2–5 ETF or stock symbols for Omega ratio analysis.")

# Top action buttons
btn_col1, btn_col2, info_col = st.columns([1, 1, 3])
with btn_col1:
    if st.button("Load Default Portfolio"):
        fill_defaults()
        st.rerun()
with btn_col2:
    if st.button("Clear All"):
        clear_all()
        st.rerun()
with info_col:
    filled = sum(1 for i in range(5) if st.session_state[f"sym_{i}"].strip())
    st.markdown(f"**{filled} of 5 filled**")

st.write("---")

# Symbol input rows
for i in range(5):
    left, mid, right = st.columns([0.4, 2, 2])
    with left:
        st.markdown(f"**{i+1}**")
    with mid:
        st.text_input(
            label="Symbol *",
            placeholder="E.g., SPY, AAPL",
            key=f"sym_{i}",
        )
    with right:
        st.text_input(
            label="Name (Optional)",
            placeholder="e.g., S&P 500 ETF",
            key=f"name_{i}",
        )

st.write("+" + " Add Another ETF (coming soon – currently 5 slots fixed)")

# Popular ETFs chips
st.markdown("**Popular ETFs:**")
chip_cols = st.columns(len(POPULAR_ETFS))
for col, sym in zip(chip_cols, POPULAR_ETFS):
    with col:
        if st.button(sym):
            add_popular_symbol(sym)
            st.rerun()

# Note box
st.info(
    "Historical price data will be simulated for analysis. "
    "Each symbol will have 4 years of daily returns generated with realistic market characteristics."
)

# Continue button
continue_clicked = st.button("Continue to Analysis 🚀")

if continue_clicked:
    symbols = [
        st.session_state[f"sym_{i}"].upper().strip()
        for i in range(5)
        if st.session_state[f"sym_{i}"].strip()
    ]
    symbols = list(dict.fromkeys(symbols))  # remove duplicates, keep order

    if len(symbols) < 2:
        st.error("Please enter at least **2** symbols before continuing.")
        st.session_state.analysis_ready = False
    else:
        prices = simulate_price_data(symbols, years=4)
        st.session_state.prices = prices
        st.session_state.analysis_ready = True

# ---------------------------------------------------------------------
# Analysis section (only shown after Continue)
# ---------------------------------------------------------------------
prices = st.session_state.prices

if st.session_state.analysis_ready and prices is not None:
    st.write("---")

    symbols = list(prices.columns)
    n_assets = len(symbols)

    # --- base returns & equal-weight fallback ---
    rets = compute_daily_returns(prices)

    # keep weights in session state
    if "weights" not in st.session_state or len(st.session_state.weights) != n_assets:
        st.session_state.weights = np.full(n_assets, 1.0 / n_assets)

    weights = np.array(st.session_state.weights, dtype=float)
    if weights.sum() == 0:
        weights[:] = 1.0 / n_assets
    weights_norm = weights / weights.sum()

    # portfolio returns & stats (for cards + all tabs)
    port_rets = rets.dot(weights_norm)
    ann_factor = 252
    mean_daily = port_rets.mean()
    mean_ann = (1 + mean_daily) ** ann_factor - 1
    vol_daily = port_rets.std()
    vol_ann = vol_daily * np.sqrt(ann_factor)
    omega_L0 = omega_ratio(port_rets, L=0.0)
    omega_conservative = omega_ratio(port_rets, L=-0.0002)  # -0.02%
    omega_aggressive = omega_ratio(port_rets, L=0.0002)     # +0.02%
    sharpe_approx = mean_daily / vol_daily if vol_daily > 0 else float("nan")

    # asset summary (also used in Analysis tab)
    summary_df = asset_summary(prices, L=0.0)
    best_row = summary_df.loc[summary_df["Omega_L0"].idxmax()]
    worst_row = summary_df.loc[summary_df["Omega_L0"].idxmin()]

    st.markdown("### Omega Ratio Portfolio Analysis")
    st.caption(
        f"Analyzing {n_assets} assets: " + ", ".join(symbols)
    )

    # ---------- KPI CARDS (top row) ----------
    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.metric(
            "Portfolio Mean Return",
            f"{mean_daily*100:.4f}%",
            help=f"Daily average. Annualized: {mean_ann*100:.2f}%",
        )
        st.caption(f"Ann: {mean_ann*100:.2f}%")

    with c2:
        st.metric(
            "Portfolio Volatility",
            f"{vol_daily*100:.4f}%",
            help=f"Daily standard deviation. Annualized: {vol_ann*100:.2f}%",
        )
        st.caption(f"Ann: {vol_ann*100:.2f}%")

    with c3:
        st.metric(
            "Omega (L = 0.0%)",
            f"{omega_L0:.3f}",
            help="Risk-adjusted performance relative to breakeven.",
        )
        st.caption(f"Best ETF: {best_row['Symbol']} ({best_row['Omega_L0']:.3f})")

    with c4:
        st.metric(
            "Omega (L = −0.02%)",
            f"{omega_conservative:.3f}",
            help="Conservative loss threshold (easier to beat).",
        )
        st.caption("Conservative threshold")

    with c5:
        st.metric(
            "Omega (L = +0.02%)",
            f"{omega_aggressive:.3f}",
            help="Aggressive loss threshold (harder to beat).",
        )
        st.caption(f"Sharpe Approx: {sharpe_approx:.3f}")

    # ---------- pre-compute efficient frontier at L = 0 for analysis tab ----------
    n_ports_L0 = 400
    results_L0 = []
    for _ in range(n_ports_L0):
        w = np.random.rand(n_assets)
        w /= w.sum()
        p_rets = rets.dot(w)
        std = p_rets.std()
        om = omega_ratio(p_rets, L=0.0)
        results_L0.append((std, om, w))

    frontier_L0 = pd.DataFrame(results_L0, columns=["std", "omega", "weights"])
    frontier_L0 = frontier_L0.sort_values("std").reset_index(drop=True)

    best = -np.inf
    is_frontier_L0 = []
    for _, row in frontier_L0.iterrows():
        if row["omega"] >= best:
            best = row["omega"]
            is_frontier_L0.append(True)
        else:
            is_frontier_L0.append(False)
    frontier_L0["is_frontier"] = is_frontier_L0

    # ---------- TABS ----------
    tab_overview, tab_builder, tab_frontier, tab_analysis = st.tabs(
        ["Overview", "Portfolio Builder", "Efficient Frontier", "Analysis"]
    )

    # ================================================================
    # OVERVIEW TAB
    # ================================================================
    with tab_overview:
        st.subheader("ETF Performance Summary")
        st.caption("Historical data based on simulated daily prices.")

        st.dataframe(
            summary_df.style.format(
                {
                    "Latest_Price": "${:,.2f}",
                    "Daily_Avg": "{:.4%}",
                    "Ann_Return": "{:.2%}",
                    "Daily_StdDev": "{:.4%}",
                    "Ann_Volatility": "{:.2%}",
                    "Omega_L0": "{:.3f}",
                }
            ),
            use_container_width=True,
        )

        st.subheader("Returns Analysis – Cumulative")
        cum_rets = (1 + rets).cumprod() - 1
        st.line_chart(cum_rets, use_container_width=True)

        st.subheader("Portfolio Daily Returns")
        st.line_chart(pd.DataFrame({"Portfolio": port_rets}), use_container_width=True)

    # ================================================================
    # PORTFOLIO BUILDER TAB
    # ================================================================
    with tab_builder:
        left, right = st.columns([1, 2])

        # ---- left: sliders for weights ----
        with left:
            st.subheader("Portfolio Weights")
            st.caption("Adjust allocation for each ETF (Total should be 100%).")

            new_weights = []
            for i, sym in enumerate(symbols):
                w_pct = weights_norm[i] * 100
                new_w = st.slider(
                    sym,
                    min_value=0,
                    max_value=100,
                    value=int(round(w_pct)),
                    key=f"slider_{sym}",
                )
                new_weights.append(new_w)

            new_weights = np.array(new_weights, dtype=float)
            total = new_weights.sum()
            st.markdown(f"**Total: {total:.1f}%**")

            col_eq, col_norm = st.columns(2)
            with col_eq:
                if st.button("Equal Weight"):
                    new_weights = np.full(n_assets, 100.0 / n_assets)
                    total = new_weights.sum()
            with col_norm:
                if st.button("Normalize to 100%"):
                    if total > 0:
                        new_weights = new_weights / total * 100.0
                        total = new_weights.sum()

            # save back to session state (normalized 0–1)
            if new_weights.sum() > 0:
                st.session_state.weights = new_weights / 100.0
                weights_norm = st.session_state.weights
                port_rets = rets.dot(weights_norm)
                mean_daily = port_rets.mean()
                vol_daily = port_rets.std()
                omega_L0 = omega_ratio(port_rets, L=0.0)

            st.markdown(
                f"**Omega (L = 0%) for this portfolio:** `{omega_L0:.3f}`"
            )

        # ---- right: Omega ratio matrix + chart ----
        with right:
            st.subheader("Omega Ratios by Threshold")
            st.caption(
                "Compare ETFs and your portfolio across different loss thresholds L."
            )

            thresholds = np.linspace(-0.0005, 0.0005, 11)  # -0.05% to +0.05%
            threshold_labels = [f"L={L*100:.2f}%" for L in thresholds]

            omega_table = {}
            for sym in symbols:
                sym_rets = rets[sym]
                omega_table[sym] = [
                    omega_ratio(sym_rets, L=L) for L in thresholds
                ]

            # portfolio Omega for same thresholds
            omega_table["Portfolio"] = [
                omega_ratio(port_rets, L=L) for L in thresholds
            ]

            omega_df = pd.DataFrame(omega_table, index=threshold_labels).T
            omega_df.index.name = "Asset"

            st.dataframe(
                omega_df.style.format("{:.3f}"),
                use_container_width=True,
            )

            st.subheader("Returns Analysis – Cumulative")
            cum_rets = (1 + rets).cumprod() - 1
            cum_rets["Portfolio"] = (1 + port_rets).cumprod() - 1
            st.line_chart(cum_rets, use_container_width=True)

    # ================================================================
    # EFFICIENT FRONTIER TAB
    # ================================================================
    with tab_frontier:
        import altair as alt

        st.subheader("Omega-Efficient Frontier")
        st.caption("Standard deviation vs Omega ratio for random portfolios.")

        threshold_choice = st.selectbox(
            "Threshold L",
            options=np.linspace(-0.0005, 0.0005, 11),
            format_func=lambda x: f"L = {x*100:.2f}%",
            index=5,  # L = 0
        )

        # generate random portfolios for chosen threshold
        n_ports = 400
        results = []
        for _ in range(n_ports):
            w = np.random.rand(n_assets)
            w /= w.sum()
            p_rets = rets.dot(w)
            std = p_rets.std()
            om = omega_ratio(p_rets, L=threshold_choice)
            results.append((std, om, w))

        frontier_df = pd.DataFrame(results, columns=["std", "omega", "weights"])
        frontier_df = frontier_df.sort_values("std").reset_index(drop=True)

        best = -np.inf
        is_frontier = []
        for _, row in frontier_df.iterrows():
            if row["omega"] >= best:
                best = row["omega"]
                is_frontier.append(True)
            else:
                is_frontier.append(False)
        frontier_df["is_frontier"] = is_frontier

        # current portfolio point
        cur_std = port_rets.std()
        cur_om = omega_ratio(port_rets, L=threshold_choice)

        base = (
            alt.Chart(frontier_df)
            .mark_circle(opacity=0.4)
            .encode(
                x=alt.X("std", title="Standard Deviation"),
                y=alt.Y("omega", title="Omega Ratio"),
                color=alt.value("#A0A0A0"),
            )
        )

        frontier_line = (
            alt.Chart(frontier_df[frontier_df["is_frontier"]])
            .mark_line(point=True)
            .encode(
                x="std",
                y="omega",
                color=alt.value("#00AA55"),
            )
        )

        current_point = (
            alt.Chart(
                pd.DataFrame({"std": [cur_std], "omega": [cur_om], "label": ["Your Portfolio"]})
            )
            .mark_point(size=120, shape="diamond")
            .encode(
                x="std",
                y="omega",
                color=alt.value("#3366FF"),
            )
        )

        chart = base + frontier_line + current_point
        st.altair_chart(chart, use_container_width=True)

    # ================================================================
    # ANALYSIS TAB
    # ================================================================
    with tab_analysis:
        st.subheader("Analysis Insights")
        st.caption("Key findings from the Omega ratio analysis.")

        # text cards
        st.success(
            f"**Highest Omega ETF** – {best_row['Symbol']} has the highest Omega ratio at "
            f"L = 0% ({best_row['Omega_L0']:.3f}), indicating the best risk-adjusted performance "
            "relative to breakeven."
        )

        st.warning(
            f"**Lowest Omega ETF** – {worst_row['Symbol']} has the lowest Omega ratio "
            f"({worst_row['Omega_L0']:.3f}). You might underweight this ETF if you are seeking "
            "higher Omega and better downside protection."
        )

        st.info(
            f"**Portfolio Diversification Effect** – Your portfolio Omega at L = 0% is "
            f"{omega_L0:.3f}. Compare this with individual ETFs to see whether diversification "
            "is improving risk-adjusted performance."
        )

        st.info(
            "**Threshold Impact** – Lower thresholds (negative L) capture more gains and usually "
            "show higher Omega ratios. Higher thresholds are stricter and highlight the "
            "probability of achieving more ambitious return targets."
        )

        # efficient portfolio suggestion using frontier_L0
        best_frontier = frontier_L0[frontier_L0["is_frontier"]].iloc[-1]
        best_w = best_frontier["weights"]
        best_alloc = ", ".join(
            f"{sym}: {w*100:.1f}%"
            for sym, w in zip(symbols, best_w)
        )

        st.success(
            f"**Suggested Efficient Portfolio** – A portfolio on the efficient frontier at L = 0% "
            f"achieves an Omega of about {best_frontier['omega']:.3f}. "
            f"One possible allocation is: {best_alloc}."
        )

        st.markdown("---")
        st.markdown("### ETF Omega Ranking (L = 0%)")
        ranked = summary_df.sort_values("Omega_L0", ascending=False)[
            ["Symbol", "Omega_L0"]
        ]
        st.table(ranked.style.format({"Omega_L0": "{:.3f}"}))

        st.markdown("---")
        st.markdown("### How to Interpret Results")

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(
                "**Which ETFs have highest Omega?**  \n"
                "ETFs with Omega > 1 at L = 0% generate more gains than losses. "
                "Higher Omega indicates better downside protection relative to upside capture."
            )
            st.markdown(
                "**Do portfolios improve Omega?**  \n"
                "Diversification can improve Omega by reducing volatility while "
                "maintaining return potential. Compare your portfolio Omega against each ETF."
            )

        with col_b:
            st.markdown(
                "**How does threshold affect the frontier?**  \n"
                "Lower thresholds (negative L) are easier to beat, showing higher Omega. "
                "Higher thresholds reveal the probability of exceeding ambitious return targets."
            )
            st.markdown(
                "**Zero Correlation Assumption (optional note)**  \n"
                "If you assume zero correlation between ETFs, portfolio variance is simply the "
                "weighted sum of individual variances. This simplifies the efficient frontier calculation."
            )
