import pandas as pd

from algo_trading_system.strategies.options import build_strategy


def _sample_df(trend: str = "up") -> pd.DataFrame:
    prices = list(range(22000, 22120, 5)) if trend == "up" else list(range(22120, 22000, -5))
    return pd.DataFrame(
        {
            "open": prices,
            "high": [p + 10 for p in prices],
            "low": [p - 10 for p in prices],
            "close": prices,
            "volume": [1000] * len(prices),
        }
    )


def test_long_call_signal_generated_on_uptrend():
    strategy = build_strategy("long_call")
    signal = strategy.generate_signal(_sample_df("up"))
    assert signal is not None
    assert signal.strategy_name == "long_call"


def test_long_put_signal_generated_on_downtrend():
    strategy = build_strategy("long_put")
    signal = strategy.generate_signal(_sample_df("down"))
    assert signal is not None
    assert signal.strategy_name == "long_put"


def test_iron_condor_builds_multileg():
    strategy = build_strategy("iron_condor")
    signal = strategy.generate_signal(_sample_df("up"))
    assert signal is not None
    assert len(signal.legs) == 4
