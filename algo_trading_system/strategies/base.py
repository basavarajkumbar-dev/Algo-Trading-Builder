from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd

from algo_trading_system.types import StrategySignal


class BaseStrategy(ABC):
    name: str

    def __init__(self, params: dict | None = None):
        self.params = params or {}

    @abstractmethod
    def generate_signal(self, data: pd.DataFrame) -> StrategySignal | None:
        raise NotImplementedError
