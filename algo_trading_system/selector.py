from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from algo_trading_system.strategies.options import build_strategy
from algo_trading_system.types import BacktestResult, StrategySignal


@dataclass
class StrategySelector:
    strategy_names: list[str]
    performance_db: dict[str, BacktestResult] = field(default_factory=dict)

    def _market_regime(self, data: pd.DataFrame) -> str:
        close = data["close"]
        ema9 = close.ewm(span=9, adjust=False).mean().iloc[-1]
        ema21 = close.ewm(span=21, adjust=False).mean().iloc[-1]
        ret = close.pct_change().dropna()
        vol = float(ret.rolling(20).std().iloc[-1]) if len(ret) > 20 else float(ret.std())

        if ema9 > ema21 and vol > 0.003:
            return "bullish"
        if ema9 < ema21 and vol > 0.003:
            return "bearish"
        return "sideways"

    def pick(self, data: pd.DataFrame) -> StrategySignal | None:
        regime = self._market_regime(data)
        regime_map = {
            "bullish": ["bull_call_spread", "long_call", "covered_call"],
            "bearish": ["bear_put_spread", "long_put", "protective_put"],
            "sideways": ["iron_condor", "short_straddle", "short_strangle"],
        }

        candidates = [s for s in self.strategy_names if s in regime_map[regime]]
        best_signal = None
        best_score = -1.0

        for name in candidates:
            strategy = build_strategy(name)
            signal = strategy.generate_signal(data)
            if signal is None:
                continue
            perf = self.performance_db.get(name)
            historical_score = (perf.win_rate / 100.0) if perf else 0.5
            drawdown_penalty = min((perf.max_drawdown / 100.0), 0.4) if perf else 0.1
            score = (signal.confidence * 0.5) + (historical_score * 0.4) - (drawdown_penalty * 0.1)
            if score > best_score:
                best_score = score
                best_signal = signal

        return best_signal
