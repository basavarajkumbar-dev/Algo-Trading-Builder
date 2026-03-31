from __future__ import annotations

from pathlib import Path

import pandas as pd

from algo_trading_system.types import BacktestResult, Trade


def export_trade_log(trades: list[Trade], path: str = "algo_trading_system/logs/trades.csv") -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    records = []
    for trade in trades:
        records.append(
            {
                "trade_id": trade.trade_id,
                "strategy": trade.strategy_name,
                "opened_at": trade.opened_at,
                "closed_at": trade.closed_at,
                "status": trade.status,
                "pnl": trade.pnl,
                "legs": len(trade.legs),
            }
        )
    pd.DataFrame(records).to_csv(out, index=False)
    return out


def export_backtest_report(
    results: dict[str, BacktestResult], path: str = "algo_trading_system/reports/backtest_summary.csv"
) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        {
            "strategy": r.strategy_name,
            "total_pnl": r.total_pnl,
            "win_rate": r.win_rate,
            "max_drawdown": r.max_drawdown,
            "trades": r.trades,
            **r.metrics,
        }
        for r in results.values()
    ]
    df = pd.DataFrame(rows).sort_values(by="win_rate", ascending=False)
    df.to_csv(out, index=False)
    return out
