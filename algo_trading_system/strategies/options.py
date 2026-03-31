from __future__ import annotations

import math

import pandas as pd

from algo_trading_system.strategies.base import BaseStrategy
from algo_trading_system.types import OptionLeg, StrategySignal


def _ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()


def _atr(data: pd.DataFrame, period: int = 14) -> float:
    high_low = data["high"] - data["low"]
    high_close = (data["high"] - data["close"].shift()).abs()
    low_close = (data["low"] - data["close"].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return float(tr.rolling(period).mean().iloc[-1])


def _atm_strike(spot: float, step: int = 50) -> int:
    return int(round(spot / step) * step)


class LongCallStrategy(BaseStrategy):
    name = "long_call"

    def generate_signal(self, data: pd.DataFrame) -> StrategySignal | None:
        fast = _ema(data["close"], self.params.get("fast_ema", 9)).iloc[-1]
        slow = _ema(data["close"], self.params.get("slow_ema", 21)).iloc[-1]
        spot = float(data["close"].iloc[-1])
        if fast <= slow:
            return None
        premium = self.params.get("premium", max(80.0, spot * 0.0035))
        risk = premium * 0.25
        leg = OptionLeg(
            symbol="NIFTY_CE",
            direction="BUY",
            quantity=1,
            entry_price=premium,
            stop_loss=premium - risk,
            target=premium + 2 * risk,
            strike=_atm_strike(spot),
            option_type="CE",
        )
        return StrategySignal(self.name, 0.62, "Bullish EMA crossover", [leg])


class LongPutStrategy(BaseStrategy):
    name = "long_put"

    def generate_signal(self, data: pd.DataFrame) -> StrategySignal | None:
        fast = _ema(data["close"], self.params.get("fast_ema", 9)).iloc[-1]
        slow = _ema(data["close"], self.params.get("slow_ema", 21)).iloc[-1]
        spot = float(data["close"].iloc[-1])
        if fast >= slow:
            return None
        premium = self.params.get("premium", max(80.0, spot * 0.0035))
        risk = premium * 0.25
        leg = OptionLeg(
            symbol="NIFTY_PE",
            direction="BUY",
            quantity=1,
            entry_price=premium,
            stop_loss=premium - risk,
            target=premium + 2 * risk,
            strike=_atm_strike(spot),
            option_type="PE",
        )
        return StrategySignal(self.name, 0.62, "Bearish EMA crossover", [leg])


class BullCallSpreadStrategy(BaseStrategy):
    name = "bull_call_spread"

    def generate_signal(self, data: pd.DataFrame) -> StrategySignal | None:
        spot = float(data["close"].iloc[-1])
        fast = _ema(data["close"], 9).iloc[-1]
        slow = _ema(data["close"], 21).iloc[-1]
        if fast <= slow:
            return None
        atm = _atm_strike(spot)
        width = self.params.get("spread_width", 100)
        buy = OptionLeg("NIFTY_CE_BUY", "BUY", 1, 120, 90, 180, atm, "CE")
        sell = OptionLeg("NIFTY_CE_SELL", "SELL", 1, 60, 90, 30, atm + width, "CE")
        return StrategySignal(self.name, 0.68, "Bullish with defined risk", [buy, sell])


class BearPutSpreadStrategy(BaseStrategy):
    name = "bear_put_spread"

    def generate_signal(self, data: pd.DataFrame) -> StrategySignal | None:
        spot = float(data["close"].iloc[-1])
        fast = _ema(data["close"], 9).iloc[-1]
        slow = _ema(data["close"], 21).iloc[-1]
        if fast >= slow:
            return None
        atm = _atm_strike(spot)
        width = self.params.get("spread_width", 100)
        buy = OptionLeg("NIFTY_PE_BUY", "BUY", 1, 120, 90, 180, atm, "PE")
        sell = OptionLeg("NIFTY_PE_SELL", "SELL", 1, 60, 90, 30, atm - width, "PE")
        return StrategySignal(self.name, 0.68, "Bearish with defined risk", [buy, sell])


class RangeIncomeStrategy(BaseStrategy):
    """Implements Iron Condor / Short Straddle / Short Strangle based on ATR regime."""

    name = "range_income"

    def generate_signal(self, data: pd.DataFrame) -> StrategySignal | None:
        atr = _atr(data)
        spot = float(data["close"].iloc[-1])
        atr_pct = atr / max(spot, 1)
        atm = _atm_strike(spot)
        if atr_pct > self.params.get("max_atr_pct", 0.012):
            return None

        regime = self.params.get("regime", "iron_condor")
        width = self.params.get("wings", 200)
        if regime == "short_straddle":
            legs = [
                OptionLeg("NIFTY_CE", "SELL", 1, 180, 240, 60, atm, "CE"),
                OptionLeg("NIFTY_PE", "SELL", 1, 180, 240, 60, atm, "PE"),
            ]
        elif regime == "short_strangle":
            legs = [
                OptionLeg("NIFTY_CE", "SELL", 1, 130, 190, 40, atm + width, "CE"),
                OptionLeg("NIFTY_PE", "SELL", 1, 130, 190, 40, atm - width, "PE"),
            ]
        else:  # iron_condor
            legs = [
                OptionLeg("NIFTY_CE_SHORT", "SELL", 1, 100, 140, 20, atm + width, "CE"),
                OptionLeg("NIFTY_CE_HEDGE", "BUY", 1, 40, 0, 120, atm + width + 150, "CE"),
                OptionLeg("NIFTY_PE_SHORT", "SELL", 1, 100, 140, 20, atm - width, "PE"),
                OptionLeg("NIFTY_PE_HEDGE", "BUY", 1, 40, 0, 120, atm - width - 150, "PE"),
            ]
        return StrategySignal(regime, 0.66, f"Low-volatility regime detected ({atr_pct:.2%})", legs)


class ProtectivePutStrategy(BaseStrategy):
    name = "protective_put"

    def generate_signal(self, data: pd.DataFrame) -> StrategySignal | None:
        spot = float(data["close"].iloc[-1])
        atm = _atm_strike(spot)
        lot_equiv = int(self.params.get("underlying_lot_equiv", 1))
        return StrategySignal(
            self.name,
            0.58,
            "Hedged bullish exposure",
            [
                OptionLeg("NIFTY_FUT", "BUY", lot_equiv, spot, spot * 0.98, spot * 1.04),
                OptionLeg("NIFTY_PE_HEDGE", "BUY", lot_equiv, 110, 70, 190, atm, "PE"),
            ],
        )


class CoveredCallStrategy(BaseStrategy):
    name = "covered_call"

    def generate_signal(self, data: pd.DataFrame) -> StrategySignal | None:
        spot = float(data["close"].iloc[-1])
        atm = _atm_strike(spot)
        otm = atm + int(self.params.get("otm_distance", 200))
        return StrategySignal(
            self.name,
            0.56,
            "Income overlay on long underlying",
            [
                OptionLeg("NIFTY_FUT", "BUY", 1, spot, spot * 0.98, spot * 1.03),
                OptionLeg("NIFTY_CE_SHORT", "SELL", 1, 120, 180, 20, otm, "CE"),
            ],
        )


STRATEGY_REGISTRY = {
    cls.name: cls
    for cls in [
        LongCallStrategy,
        LongPutStrategy,
        BullCallSpreadStrategy,
        BearPutSpreadStrategy,
        RangeIncomeStrategy,
        ProtectivePutStrategy,
        CoveredCallStrategy,
    ]
}


def build_strategy(name: str, params: dict | None = None) -> BaseStrategy:
    normalized = name.lower()
    if normalized in {"iron_condor", "short_straddle", "short_strangle"}:
        p = {"regime": normalized}
        if params:
            p.update(params)
        return RangeIncomeStrategy(p)

    if normalized not in STRATEGY_REGISTRY:
        raise ValueError(f"Unsupported strategy: {name}")
    return STRATEGY_REGISTRY[normalized](params)
