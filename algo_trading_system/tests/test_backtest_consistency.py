import pandas as pd

from algo_trading_system.backtest.engine import BacktestEngine
from algo_trading_system.selector import StrategySelector


def test_backtest_runs_and_returns_metrics():
    close = [22000 + (i % 7) * 3 for i in range(200)]
    df = pd.DataFrame(
        {
            "open": close,
            "high": [c + 15 for c in close],
            "low": [c - 15 for c in close],
            "close": close,
            "volume": [1000] * len(close),
        }
    )
    selector = StrategySelector(["long_call", "long_put", "iron_condor"])
    result = BacktestEngine(selector).run(df)
    assert isinstance(result, dict)
    assert len(result) >= 1
    for _, metrics in result.items():
        assert 0 <= metrics.win_rate <= 100
        assert metrics.trades > 0
