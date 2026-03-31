from __future__ import annotations

import streamlit as st

from algo_trading_system.backtest.engine import BacktestEngine
from algo_trading_system.config import DEFAULT_STRATEGIES
from algo_trading_system.data.kite_data_handler import CsvDataHandler
from algo_trading_system.selector import StrategySelector

st.set_page_config(page_title="NIFTY Options Algo Dashboard", layout="wide")
st.title("NIFTY Options Algo Trading Dashboard")

uploaded = st.file_uploader("Upload historical/live snapshot CSV", type=["csv"])
if uploaded:
    df = CsvDataHandler.from_csv(uploaded)
    selector = StrategySelector(strategy_names=DEFAULT_STRATEGIES)
    results = BacktestEngine(selector).run(df)

    if results:
        st.subheader("Strategy Comparison")
        table = [
            {
                "Strategy": v.strategy_name,
                "Total PnL": round(v.total_pnl, 2),
                "Win Rate %": round(v.win_rate, 2),
                "Drawdown": round(v.max_drawdown, 2),
                "Trades": v.trades,
            }
            for v in results.values()
        ]
        st.dataframe(table, use_container_width=True)

        best = sorted(results.values(), key=lambda x: x.win_rate, reverse=True)[0]
        st.metric("Running Strategy", best.strategy_name)
        st.metric("Accuracy %", f"{best.win_rate:.2f}")
        st.metric("Drawdown", f"{best.max_drawdown:.2f}")
    else:
        st.info("No strategy signals found for the uploaded dataset.")
else:
    st.caption("Upload data to view P&L, accuracy, and strategy ranking.")
