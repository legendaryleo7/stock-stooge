# Stock Stooge

Stock Stooge is a Streamlit web app for analyzing stocks with price history, news aggregation, and AI-powered recommendations. Enter one or more stock tickers to view interactive charts, recent news, and receive concise bullish/bearish/neutral analysis using OpenAI.

## Features
- **Interactive Price Charts:** Visualize historical price data for multiple stocks using Plotly candlesticks.
- **Recent News:** Aggregates latest news headlines for each stock via Tavily API.
- **AI Analysis:** Summarizes technical outlook and news sentiment, providing a recommendation (Bullish, Bearish, Neutral) using OpenAI's LLM.
- **Customizable Period:** Select price history period (1mo, 3mo, 6mo, 1y, 2y, 5y).
- **API Key Management:** Enter Tavily and OpenAI API keys securely in the sidebar.

## Installation
1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd stock-stooge
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
1. Launch the app:
   ```bash
   streamlit run app.py
   ```
2. Enter your Tavily and OpenAI API keys in the sidebar (or set them in a `.env` file):
   ```env
   TAVILY_API_KEY=your_tavily_key
   OPENAI_API_KEY=your_openai_key
   ```
3. Input stock tickers (e.g., `AAPL, MSFT, GOOGL`) and click **Analyze**.

## Requirements
- Python 3.8+
- See `requirements.txt` for dependencies

## Environment Variables
- `.env` file supported for API keys:
  - `TAVILY_API_KEY`
  - `OPENAI_API_KEY`

## Credits
- Data: Yahoo Finance via yfinance
- News: Tavily
- AI Analysis: OpenAI

## License
MIT License
