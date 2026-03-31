from __future__ import annotations

from dataclasses import dataclass

from algo_trading_system.config import RiskConfig
from algo_trading_system.types import StrategySignal


@dataclass
class RiskState:
    daily_realized_pnl: float = 0.0
    trades_today: int = 0


class RiskManager:
    def __init__(self, config: RiskConfig):
        self.config = config
        self.state = RiskState()

    def can_trade(self) -> bool:
        if self.state.trades_today >= self.config.max_trades_per_day:
            return False
        if self.state.daily_realized_pnl <= -(self.config.capital * self.config.daily_loss_limit_pct):
            return False
        return True

    def position_size(self, stop_loss_points: float) -> int:
        max_risk_amt = self.config.capital * self.config.max_risk_per_trade_pct
        if stop_loss_points <= 0:
            return 0
        per_lot_qty = 50  # NIFTY lot (can be made dynamic from instrument master)
        total_qty = int(max_risk_amt / stop_loss_points)
        min_qty = self.config.fixed_lots * per_lot_qty
        return max(min_qty, (total_qty // per_lot_qty) * per_lot_qty)

    def validate_signal(self, signal: StrategySignal) -> StrategySignal:
        for leg in signal.legs:
            risk = abs(leg.entry_price - leg.stop_loss)
            reward = abs(leg.target - leg.entry_price)
            if risk == 0:
                raise ValueError(f"Invalid SL for leg {leg.symbol}")
            rr = reward / risk
            if rr < self.config.risk_reward_ratio:
                if leg.direction == "BUY":
                    leg.target = leg.entry_price + (risk * self.config.risk_reward_ratio)
                else:
                    leg.target = leg.entry_price - (risk * self.config.risk_reward_ratio)
        return signal

    def register_trade_open(self) -> None:
        self.state.trades_today += 1

    def register_trade_close(self, pnl: float) -> None:
        self.state.daily_realized_pnl += pnl
