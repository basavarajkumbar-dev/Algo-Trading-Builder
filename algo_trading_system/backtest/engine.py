from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from algo_trading_system.selector import StrategySelector
from algo_trading_system.types import BacktestResult


@dataclass
class BacktestEngine:
    selector: StrategySelector

    def run(self, data: pd.DataFrame) -> dict[str, BacktestResult]:
        results: dict[str, list[float]] = {}
        rolling_window = 50

        for i in range(rolling_window, len(data)):
            window = data.iloc[:i]
            signal = self.selector.pick(window)
            if signal is None:
                continue

            current_price = float(window["close"].iloc[-1])
            next_price = float(data["close"].iloc[i])
            direction = 1 if signal.strategy_name in {"long_call", "bull_call_spread", "covered_call"} else -1
            pnl = (next_price - current_price) * direction
            results.setdefault(signal.strategy_name, []).append(pnl)

        summary: dict[str, BacktestResult] = {}
        for strategy_name, pnl_list in results.items():
            if not pnl_list:
                continue
            pnl_series = pd.Series(pnl_list)
            equity = pnl_series.cumsum()
            drawdown = (equity - equity.cummax()).min()
            summary[strategy_name] = BacktestResult(
                strategy_name=strategy_name,
                total_pnl=float(pnl_series.sum()),
                win_rate=float((pnl_series > 0).mean() * 100),
                max_drawdown=float(abs(drawdown)),
                trades=len(pnl_list),
                metrics={
                    "avg_pnl": float(pnl_series.mean()),
                    "profit_factor": float(
                        pnl_series[pnl_series > 0].sum() / max(abs(pnl_series[pnl_series < 0].sum()), 1e-9)
                    ),
                },
            )
        return summary
