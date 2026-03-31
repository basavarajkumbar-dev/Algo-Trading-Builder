from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

import pandas as pd

from algo_trading_system.risk import RiskManager
from algo_trading_system.types import StrategySignal, Trade


@dataclass
class PaperBroker:
    slippage_bps: float = 2.0

    def execute(self, signal: StrategySignal) -> list:
        filled = []
        for leg in signal.legs:
            slip = leg.entry_price * (self.slippage_bps / 10000)
            leg.entry_price = leg.entry_price + slip if leg.direction == "BUY" else leg.entry_price - slip
            filled.append(leg)
        return filled


@dataclass
class LiveBroker:
    kite_client: object

    def execute(self, signal: StrategySignal) -> list:
        placed_legs = []
        for leg in signal.legs:
            transaction_type = "BUY" if leg.direction == "BUY" else "SELL"
            # CNC/MIS/product can be made strategy-specific.
            self.kite_client.place_order(
                variety="regular",
                exchange="NFO",
                tradingsymbol=leg.symbol,
                transaction_type=transaction_type,
                quantity=leg.quantity,
                order_type="MARKET",
                product="MIS",
            )
            placed_legs.append(leg)
        return placed_legs


@dataclass
class ExecutionEngine:
    risk_manager: RiskManager
    broker: PaperBroker | LiveBroker
    trades: list[Trade] = field(default_factory=list)

    def open_trade(self, signal: StrategySignal) -> Trade | None:
        if not self.risk_manager.can_trade():
            return None
        signal = self.risk_manager.validate_signal(signal)
        filled_legs = self.broker.execute(signal)
        trade = Trade(
            trade_id=str(uuid4()),
            strategy_name=signal.strategy_name,
            legs=filled_legs,
            opened_at=datetime.utcnow(),
        )
        self.trades.append(trade)
        self.risk_manager.register_trade_open()
        return trade

    def mark_to_market(self, latest_price: float) -> float:
        total = 0.0
        for trade in self.trades:
            if trade.status == "CLOSED":
                total += trade.pnl
                continue
            leg_pnl = 0.0
            for leg in trade.legs:
                if leg.direction == "BUY":
                    leg_pnl += latest_price - leg.entry_price
                else:
                    leg_pnl += leg.entry_price - latest_price
            trade.pnl = leg_pnl
            total += leg_pnl
        return total

    def close_trade(self, trade_id: str, exit_price: float) -> None:
        for trade in self.trades:
            if trade.trade_id != trade_id or trade.status == "CLOSED":
                continue
            leg_pnl = 0.0
            for leg in trade.legs:
                if leg.direction == "BUY":
                    leg_pnl += exit_price - leg.entry_price
                else:
                    leg_pnl += leg.entry_price - exit_price
            trade.pnl = leg_pnl
            trade.status = "CLOSED"
            trade.closed_at = datetime.utcnow()
            self.risk_manager.register_trade_close(leg_pnl)
            return


def run_paper_session(engine: ExecutionEngine, selector, stream_df: pd.DataFrame) -> dict:
    for i in range(50, len(stream_df)):
        window = stream_df.iloc[:i]
        signal = selector.pick(window)
        if signal and not any(t.status == "OPEN" for t in engine.trades):
            engine.open_trade(signal)
        engine.mark_to_market(float(stream_df["close"].iloc[i]))

    live_pnl = sum(t.pnl for t in engine.trades)
    return {
        "live_pnl": live_pnl,
        "open_positions": len([t for t in engine.trades if t.status == "OPEN"]),
        "risk_exposure": abs(live_pnl) / max(engine.risk_manager.config.capital, 1),
    }
