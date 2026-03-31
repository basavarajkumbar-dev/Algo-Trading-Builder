# NIFTY Options Algo Trading System (Kite Connect)

Production-oriented, modular Python trading framework supporting:

- **Backtesting** (historical data)
- **Paper trading** (live simulation)
- **Live trading** (Kite order routing)
- **Dynamic strategy selection** based on regime + historical performance

## Implemented strategies

### Directional
- Long Call
- Long Put
- Bull Call Spread
- Bear Put Spread

### Neutral / Income
- Iron Condor
- Short Straddle
- Short Strangle

### Hedged
- Protective Put
- Covered Call

All strategies define entry/SL/target and support multi-leg structures.

## Architecture

```text
algo_trading_system/
  data/                 # Kite + CSV data handlers
  strategies/           # Strategy abstraction + option strategy library
  selector.py           # Regime + performance-aware strategy selector
  risk.py               # 1:2 RR + lot sizing + risk caps
  backtest/engine.py    # Historical strategy evaluation
  execution/engine.py   # Paper/Live execution workflow
  dashboard/            # Streamlit dashboard
  utils/reporting.py    # CSV reports/logging
  tests/                # Unit tests and consistency checks
```

## Risk controls (strict)

- **Risk:Reward = 1:2** (enforced by `RiskManager.validate_signal`)
- **Fixed lot size: 2 lots** minimum
- **Max risk per trade** configurable (default 2% capital)
- **Daily loss limit** configurable
- **Max trades/day** configurable

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configure

Edit `config.yaml`:

- Kite API keys/tokens
- Risk settings
- Enabled strategies
- Mode (backtest / paper / live)

## Run

### Backtest

```bash
python -m algo_trading_system.main --config config.yaml --data sample_nifty.csv --mode backtest
```

### Paper trade simulation

```bash
python -m algo_trading_system.main --config config.yaml --data sample_nifty.csv --mode paper
```

### Streamlit dashboard

```bash
streamlit run algo_trading_system/dashboard/streamlit_app.py
```

## Kite Connect integration points

- `KiteDataHandler.get_historical_data(...)` for backtesting candles
- `KiteDataHandler.create_ticker()` for live ticks
- `KiteDataHandler.get_option_chain()` for strike discovery
- `LiveBroker.execute(...)` for order placement (multi-leg)

## Notes for production hardening

- Add async order manager and fill reconciliation
- Persist positions/trades in PostgreSQL
- Add websocket resiliency + reconnect state machine
- Add ML model in `selector.py` with periodic retraining
- Extend strike selection with live Greeks (delta-focused)

## Testing

```bash
pytest -q
```

The tests cover strategy signal generation and backtest consistency checks.
