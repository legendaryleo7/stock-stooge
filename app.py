import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Stock Stooge", page_icon="📈", layout="wide")
st.title("📈 Stonk News")
st.markdown("Enter stock tickers to view price history, news, and AI analysis")

# Initialize session state for API keys
if "tavily_key" not in st.session_state:
    st.session_state.tavily_key = os.getenv("TAVILY_API_KEY", "")
if "openai_key" not in st.session_state:
    st.session_state.openai_key = os.getenv("OPENAI_API_KEY", "")

# Sidebar for API keys
with st.sidebar:
    st.header("API Configuration")
    tavily_key = st.text_input("Tavily API Key", value=st.session_state.tavily_key, type="password", key="tavily_input")
    openai_key = st.text_input("OpenAI API Key", value=st.session_state.openai_key, type="password", key="openai_input")
    
    # Update session state when keys change
    if tavily_key != st.session_state.tavily_key:
        st.session_state.tavily_key = tavily_key
    if openai_key != st.session_state.openai_key:
        st.session_state.openai_key = openai_key
    
    st.header("Settings")
    period = st.selectbox("Price History Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=0)

# Main input
tickers_input = st.text_input("Enter stock ticker(s) separated by commas", placeholder="AAPL, MSFT, GOOGL")

if st.button("Analyze", type="primary") and tickers_input:
    tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
    
    for ticker in tickers:
        header_col1, header_col2 = st.columns([3, 1])
        with header_col1:
            st.header(f"📊 {ticker}")
        badge_placeholder = header_col2.empty()
        
        # Fetch stock data
        with st.spinner(f"Fetching data for {ticker}..."):
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period=period)
                info = stock.info
                
                if hist.empty:
                    st.error(f"No data found for {ticker}")
                    continue
                
                # Display basic info
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Current Price", f"${hist['Close'].iloc[-1]:.2f}")
                col2.metric("Change", f"{((hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0] * 100):.2f}%")
                col3.metric("High", f"${hist['High'].max():.2f}")
                col4.metric("Low", f"${hist['Low'].min():.2f}")
                
                # Price chart
                fig = go.Figure()
                fig.add_trace(go.Candlestick(
                    x=hist.index,
                    open=hist['Open'],
                    high=hist['High'],
                    low=hist['Low'],
                    close=hist['Close'],
                    name=ticker
                ))
                fig.update_layout(
                    title=f"{ticker} Price History",
                    xaxis_title="Date",
                    yaxis_title="Price (USD)",
                    xaxis_rangeslider_visible=False,
                    height=400
                )
                st.plotly_chart(fig, width="content")
                
                # News search with Tavily
                if tavily_key:
                    st.subheader("📰 Recent News")
                    with st.spinner("Searching for news..."):
                        try:
                            from tavily import TavilyClient
                            tavily = TavilyClient(api_key=tavily_key)
                            company_name = info.get('longName', ticker)
                            search_result = tavily.search(
                                query=f"{company_name} stock news",
                                max_results=5,
                                search_depth="basic"
                            )
                            
                            news_text = ""
                            for result in search_result.get('results', []):
                                st.markdown(f"**[{result['title']}]({result['url']})**")
                                st.caption(f"{result.get('content', '')[:150]}...")
                                news_text += f"{result['title']}: {result.get('content', '')}\n\n"
                            
                            # LLM Analysis
                            if openai_key and news_text:
                                st.subheader("🤖 AI Analysis")
                                with st.spinner("Generating analysis..."):
                                    try:
                                        from openai import OpenAI
                                        client = OpenAI(api_key=openai_key)
                                        
                                        price_change = ((hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0] * 100)
                                        
                                        prompt = f"""Analyze the following stock and provide a brief bullish/bearish recommendation:

Stock: {ticker} ({info.get('longName', 'Unknown')})
Current Price: ${hist['Close'].iloc[-1]:.2f}
Period Change: {price_change:.2f}%
52-Week High: ${info.get('fiftyTwoWeekHigh', 'N/A')}
52-Week Low: ${info.get('fiftyTwoWeekLow', 'N/A')}

Recent News:
{news_text[:2000]}

Provide a concise analysis (2-3 paragraphs) with:
1. Technical outlook based on price action
2. Sentiment from recent news
3. Overall recommendation: BULLISH, BEARISH, or NEUTRAL with brief reasoning"""

                                        response = client.chat.completions.create(
                                            model="gpt-5-mini",
                                            reasoning_effort="medium",
                                            messages=[{"role": "user", "content": prompt}],
                                            max_completion_tokens=4000
                                        )
                                        
                                        analysis = response.choices[0].message.content
                                        
                                        if not analysis: 
                                            continue

                                        if "BULLISH" in analysis.upper():
                                            badge_placeholder.success("🟢 BULLISH")
                                            st.success(analysis)
                                        elif "BEARISH" in analysis.upper():
                                            badge_placeholder.error("🔴 BEARISH")
                                            st.error(analysis)
                                        else:
                                            badge_placeholder.warning("🟡 NEUTRAL")
                                            st.info(analysis)
                                            
                                    except Exception as e:
                                        st.warning(f"LLM analysis failed: {e}")
                            elif not openai_key:
                                st.info("Add OpenAI API key for AI analysis")
                                
                        except Exception as e:
                            st.warning(f"News search failed: {e}")
                else:
                    st.info("Add Tavily API key for news search")
                    
            except Exception as e:
                st.error(f"Error fetching {ticker}: {e}")
        
        st.divider()

st.markdown("---")
st.caption("Data provided by Yahoo Finance. News by Tavily. Analysis by OpenAI.")
