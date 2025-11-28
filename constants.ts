import { StrategyPreset } from './types';

export const STRATEGY_PRESETS: StrategyPreset[] = [
  {
    id: 'orb-breakout',
    title: 'Intraday ORB Breakout',
    description: '5/15-minute Opening Range Breakout strategy buying ATM Options.',
    prompt: `
      Create a Python script for Zerodha Kite Connect.
      Strategy: Intraday Opening Range Breakout (ORB).
      Instrument: Nifty 50 Options.
      Timeframe: 5-Minute or 15-Minute candles.
      Rules:
      1. Calculate ORB High/Low between 9:15-9:30 AM.
      2. If price breaks ORB High, BUY ATM Call Option.
      3. If price breaks ORB Low, BUY ATM Put Option.
      Risk Management:
      - Stop Loss: 1R (Risk).
      - Target: 1.5R (Reward) based on the breakout candle's range.
      Accuracy Check:
      - Before executing, run a backtest function on the last 30 days data.
      - Only place the order if the calculated historical accuracy is > 75%.
    `
  },
  {
    id: 'supertrend',
    title: 'Nifty Trend-Following (Supertrend)',
    description: 'Trend following using Supertrend (7,3) indicator on Nifty Options.',
    prompt: `
      Create a Python script for Zerodha Kite Connect.
      Strategy: Nifty Trend-Following Supertrend.
      Indicators: Supertrend (Period 7, Multiplier 3).
      Instrument: Nifty 50 Options.
      Rules:
      1. If Supertrend flips to Buy (Green), BUY ATM Call Option.
      2. If Supertrend flips to Sell (Red), BUY ATM Put Option.
      3. Exit trade when the Supertrend signal flips to the opposite direction.
      4. Hard exit at 3:20 PM intraday.
      Risk Management:
      - Stop Loss: The Supertrend line value itself acts as the trailing SL.
      Accuracy Check:
      - Before executing, simulate the strategy on the previous day's data.
      - Only place the order if the simulation accuracy is > 75%.
    `
  }
];

export const SYSTEM_INSTRUCTION = `
You are an expert Python developer specializing in Algorithmic Trading and the Zerodha Kite Connect API.
Your task is to generate production-grade, robust, and well-commented Python code based on the user's strategy requirements.

CRITICAL REQUIREMENTS:
1.  **Library**: Use 'kiteconnect' for API calls and 'pandas_ta' or 'talib' for technical indicators.
2.  **Accuracy Logic**: You MUST implement a specific function block (e.g., 'check_strategy_accuracy()') that simulates or backtests the strategy on historical data. 
    - The code must explicitly check: 'if accuracy > 75: execute_trade()'.
3.  **Option Chain**: Include logic to fetch the Nifty 50 spot price, calculate the ATM strike, and select the correct Option symbol (CE for bullish, PE for bearish).
4.  **Risk Management**: Implement Order placement with Stop Loss (SL-M or SL limit) and Target orders.
5.  **Structure**:
    - Setup API connection (API_KEY, API_SECRET).
    - Helper functions for fetching data, calculating indicators, and placing orders.
    - Main trading loop that runs every minute/tick.
6.  **Safety**: Add a disclaimer in comments about the risks of algo trading.

Do not output markdown formatting like \`\`\`python at the start or end. Just output the raw code.
`;