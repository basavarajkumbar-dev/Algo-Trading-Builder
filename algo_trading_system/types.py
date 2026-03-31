from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal

Direction = Literal["BUY", "SELL"]


@dataclass
class OptionLeg:
    symbol: str
    direction: Direction
    quantity: int
    entry_price: float
    stop_loss: float
    target: float
    strike: int | None = None
    option_type: Literal["CE", "PE"] | None = None
    expiry: str | None = None


@dataclass
class StrategySignal:
    strategy_name: str
    confidence: float
    reason: str
    legs: list[OptionLeg] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


@dataclass
class Trade:
    trade_id: str
    strategy_name: str
    legs: list[OptionLeg]
    opened_at: datetime
    status: Literal["OPEN", "CLOSED"] = "OPEN"
    closed_at: datetime | None = None
    pnl: float = 0.0


@dataclass
class BacktestResult:
    strategy_name: str
    total_pnl: float
    win_rate: float
    max_drawdown: float
    trades: int
    metrics: dict = field(default_factory=dict)
