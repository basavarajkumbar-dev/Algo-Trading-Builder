from __future__ import annotations

import argparse
from pathlib import Path

from algo_trading_system.backtest.engine import BacktestEngine
from algo_trading_system.config import DEFAULT_STRATEGIES, load_config
from algo_trading_system.data.kite_data_handler import CsvDataHandler
from algo_trading_system.execution.engine import ExecutionEngine, PaperBroker, run_paper_session
from algo_trading_system.risk import RiskManager
from algo_trading_system.selector import StrategySelector
from algo_trading_system.utils.reporting import export_backtest_report, export_trade_log


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="NIFTY options algo trading system")
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--data", required=True, help="CSV with OHLCV for NIFTY")
    parser.add_argument("--mode", choices=["backtest", "paper", "live"], default=None)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    config = load_config(args.config)
    mode = args.mode or config.mode

    df = CsvDataHandler.from_csv(args.data)
    strategy_names = [s.name for s in config.strategies] or DEFAULT_STRATEGIES
    selector = StrategySelector(strategy_names=strategy_names)

    if mode == "backtest":
        bt = BacktestEngine(selector)
        results = bt.run(df)
        report = export_backtest_report(results)
        print(f"Backtest completed. Strategies tested: {len(results)}")
        print(f"Report: {report}")
        return

    rm = RiskManager(config.risk)
    broker = PaperBroker()  # for live mode replace with LiveBroker(KiteClient)
    engine = ExecutionEngine(risk_manager=rm, broker=broker)
    summary = run_paper_session(engine, selector, df)
    trade_log = export_trade_log(engine.trades)
    print(f"Mode: {mode} | PnL: {summary['live_pnl']:.2f} | Open positions: {summary['open_positions']}")
    print(f"Trade log: {trade_log}")


if __name__ == "__main__":
    main()
