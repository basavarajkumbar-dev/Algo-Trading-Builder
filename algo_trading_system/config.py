from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class RiskConfig:
    capital: float = 500_000.0
    max_risk_per_trade_pct: float = 0.02
    risk_reward_ratio: float = 2.0
    fixed_lots: int = 2
    daily_loss_limit_pct: float = 0.05
    max_trades_per_day: int = 5


@dataclass
class StrategyConfig:
    name: str
    enabled: bool = True
    params: dict[str, Any] = field(default_factory=dict)


@dataclass
class KiteConfig:
    api_key: str = ""
    api_secret: str = ""
    access_token: str = ""


@dataclass
class AppConfig:
    mode: str = "backtest"  # backtest | paper | live
    underlying_symbol: str = "NIFTY 50"
    timeframe: str = "5minute"
    risk: RiskConfig = field(default_factory=RiskConfig)
    kite: KiteConfig = field(default_factory=KiteConfig)
    strategies: list[StrategyConfig] = field(default_factory=list)


DEFAULT_STRATEGIES = [
    "long_call",
    "long_put",
    "bull_call_spread",
    "bear_put_spread",
    "iron_condor",
    "short_straddle",
    "short_strangle",
    "protective_put",
    "covered_call",
]


def load_config(path: str | Path) -> AppConfig:
    data = yaml.safe_load(Path(path).read_text())
    risk = RiskConfig(**data.get("risk", {}))
    kite = KiteConfig(**data.get("kite", {}))

    strategy_configs = []
    for strategy_name in data.get("strategies", DEFAULT_STRATEGIES):
        if isinstance(strategy_name, dict):
            strategy_configs.append(StrategyConfig(**strategy_name))
        else:
            strategy_configs.append(StrategyConfig(name=strategy_name))

    return AppConfig(
        mode=data.get("mode", "backtest"),
        underlying_symbol=data.get("underlying_symbol", "NIFTY 50"),
        timeframe=data.get("timeframe", "5minute"),
        risk=risk,
        kite=kite,
        strategies=strategy_configs,
    )
