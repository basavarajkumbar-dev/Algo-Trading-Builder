from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable

import pandas as pd

try:
    from kiteconnect import KiteConnect, KiteTicker
except Exception:  # pragma: no cover - optional dependency during tests
    KiteConnect = None
    KiteTicker = None


@dataclass
class KiteDataHandler:
    api_key: str
    access_token: str
    client: KiteConnect | None = None

    def connect(self) -> None:
        if KiteConnect is None:
            raise ImportError("kiteconnect not installed. Run `pip install kiteconnect`.")
        self.client = KiteConnect(api_key=self.api_key)
        self.client.set_access_token(self.access_token)

    def get_historical_data(
        self,
        instrument_token: int,
        start: datetime,
        end: datetime,
        interval: str = "5minute",
    ) -> pd.DataFrame:
        if not self.client:
            self.connect()
        candles = self.client.historical_data(instrument_token, start, end, interval)
        df = pd.DataFrame(candles)
        if not df.empty:
            df["date"] = pd.to_datetime(df["date"])
        return df

    def get_option_chain(self, exchange: str = "NFO") -> pd.DataFrame:
        if not self.client:
            self.connect()
        instruments = self.client.instruments(exchange)
        df = pd.DataFrame(instruments)
        return df[df["name"].str.contains("NIFTY", na=False)].copy()

    def create_ticker(self) -> KiteTicker:
        if KiteTicker is None:
            raise ImportError("kiteconnect not installed. Run `pip install kiteconnect`.")
        return KiteTicker(self.api_key, self.access_token)


class CsvDataHandler:
    """Fallback data handler for development/testing without API."""

    @staticmethod
    def from_csv(path: str) -> pd.DataFrame:
        df = pd.read_csv(path)
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
        return df

    @staticmethod
    def stream_rows(df: pd.DataFrame) -> Iterable[pd.Series]:
        for _, row in df.iterrows():
            yield row
