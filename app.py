import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import sqlite3
from streamlit_autorefresh import st_autorefresh
from datetime import datetime


st.set_page_config(
    page_title="Real-Time Stock Dashboard",
    page_icon="📈",
    layout="wide"
)
st.markdown("""
<style>

.main {
    padding-top: 1rem;
}

h1 {
    font-size: 42px;
    font-weight: 700;
}

h2 {
    font-size: 28px;
}

[data-testid="stMetric"] {
    background-color: #f5f7fa;
    border: 1px solid #e1e5ea;
    padding: 15px;
    border-radius: 12px;
}

[data-testid="stMetricValue"] {
    font-size: 25px;
    font-weight: 700;
}

.stButton > button {
    border-radius: 8px;
    font-weight: 600;
}

</style>
""", unsafe_allow_html=True)

st_autorefresh(
    interval=60000,
    key="stock_refresh"
)

st.title("📈 Real-Time Stock Market Dashboard")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

st.markdown(
    """
    Track stock prices, market trends, volume, technical indicators and performance in real time.
    """
)

st.sidebar.header("Search Stock")

stock = st.sidebar.text_input(
    "Enter Stock Symbol",
    "AAPL"
)

period = st.sidebar.selectbox(
    "Select Period",
    (
        "1mo",
        "3mo",
        "6mo",
        "1y",
        "5y"
    )
)

st.write("Selected Stock:", stock)

st.write("Selected Period:", period)

import yfinance as yf

st.set_page_config(layout="wide")

ticker = yf.Ticker(stock)

df = ticker.history(period=period)

st.dataframe(df)

current_price = df["Close"].iloc[-1]

high = df["High"].iloc[-1]

low = df["Low"].iloc[-1]

volume = df["Volume"].iloc[-1]

c1, c2, c3, c4 = st.columns(4)

c1.metric("Current Price", f"${current_price:.2f}")

c2.metric("Today's High", f"${high:.2f}")

c3.metric("Today's Low", f"${low:.2f}")

c4.metric("Volume", f"{volume:,}")

info = ticker.info

st.subheader("Company Information")

st.write("Company:", info.get("longName"))

st.write("Sector:", info.get("sector"))

st.write("Industry:", info.get("industry"))

st.write("Country:", info.get("country"))

st.write("Website:", info.get("website"))

import plotly.graph_objects as go

st.subheader("📈 Stock Price Chart")

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=df.index,
        y=df["Close"],
        mode="lines",
        name="Closing Price"
    )
)

fig.update_layout(
    title=f"{stock} Closing Price",
    xaxis_title="Date",
    yaxis_title="Price",
    hovermode="x unified"
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("🕯️ Candlestick Chart")

candlestick = go.Figure(
    data=[
        go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="Stock"
        )
    ]
)

candlestick.update_layout(
    title=f"{stock} Candlestick Chart",
    xaxis_title="Date",
    yaxis_title="Price",
    xaxis_rangeslider_visible=False
)

st.plotly_chart(
    candlestick,
    use_container_width=True
)

st.subheader("📊 Trading Volume")

volume_chart = go.Figure()

volume_chart.add_trace(
    go.Bar(
        x=df.index,
        y=df["Volume"],
        name="Volume"
    )
)

volume_chart.update_layout(
    title=f"{stock} Trading Volume",
    xaxis_title="Date",
    yaxis_title="Volume"
)

st.plotly_chart(
    volume_chart,
    use_container_width=True
)

df["MA20"] = df["Close"].rolling(window=20).mean()
df["MA50"] = df["Close"].rolling(window=50).mean()

st.subheader("📉 Moving Average Analysis")

ma_chart = go.Figure()

ma_chart.add_trace(
    go.Scatter(
        x=df.index,
        y=df["Close"],
        name="Close Price"
    )
)

ma_chart.add_trace(
    go.Scatter(
        x=df.index,
        y=df["MA20"],
        name="20 Day MA"
    )
)

ma_chart.add_trace(
    go.Scatter(
        x=df.index,
        y=df["MA50"],
        name="50 Day MA"
    )
)

ma_chart.update_layout(
    title=f"{stock} Moving Average",
    xaxis_title="Date",
    yaxis_title="Price"
)

st.plotly_chart(
    ma_chart,
    use_container_width=True
)

delta = df["Close"].diff()

gain = delta.clip(lower=0)

loss = -delta.clip(upper=0)

average_gain = gain.rolling(window=14).mean()

average_loss = loss.rolling(window=14).mean()

rs = average_gain / average_loss

df["RSI"] = 100 - (100 / (1 + rs))

st.subheader("📊 RSI Indicator")

rsi_chart = go.Figure()

rsi_chart.add_trace(
    go.Scatter(
        x=df.index,
        y=df["RSI"],
        name="RSI"
    )
)

rsi_chart.add_hline(
    y=70,
    line_dash="dash",
    annotation_text="Overbought (70)"
)

rsi_chart.add_hline(
    y=30,
    line_dash="dash",
    annotation_text="Oversold (30)"
)

rsi_chart.update_layout(
    title="Relative Strength Index (RSI)",
    xaxis_title="Date",
    yaxis_title="RSI"
)

st.plotly_chart(
    rsi_chart,
    use_container_width=True
)

latest_rsi = df["RSI"].iloc[-1]

st.subheader("RSI Analysis")

if latest_rsi >= 70:
    st.warning(
        f"RSI is {latest_rsi:.2f}. The stock may be overbought."
    )

elif latest_rsi <= 30:
    st.success(
        f"RSI is {latest_rsi:.2f}. The stock may be oversold."
    )

else:
    st.info(
        f"RSI is {latest_rsi:.2f}. The stock is in a relatively neutral range."
    )

df["Daily Return"] = df["Close"].pct_change() * 100
st.subheader("📈 Daily Returns")

return_chart = go.Figure()

return_chart.add_trace(
    go.Bar(
        x=df.index,
        y=df["Daily Return"],
        name="Daily Return"
    )
)

return_chart.update_layout(
    title=f"{stock} Daily Returns",
    xaxis_title="Date",
    yaxis_title="Return (%)"
)

st.plotly_chart(
    return_chart,
    use_container_width=True
)

st.subheader("📊 Stock Statistics")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Highest Price",
    f"${df['High'].max():.2f}"
)

col2.metric(
    "Lowest Price",
    f"${df['Low'].min():.2f}"
)

col3.metric(
    "Average Price",
    f"${df['Close'].mean():.2f}"
)

col4.metric(
    "Average Volume",
    f"{df['Volume'].mean():,.0f}"
)

st.subheader("📋 Historical Data")

st.dataframe(
    df,
    use_container_width=True
)

csv = df.to_csv().encode("utf-8")

st.download_button(
    label="⬇️ Download Stock Data",
    data=csv,
    file_name=f"{stock}_stock_data.csv",
    mime="text/csv"
)

st.subheader("📊 Compare Stocks")

stock1 = st.text_input("Stock 1", "AAPL")
stock2 = st.text_input("Stock 2", "MSFT")
stock3 = st.text_input("Stock 3", "GOOGL")

compare_period = st.selectbox(
    "Comparison Period",
    ["1mo", "3mo", "6mo", "1y", "5y"],
    key="comparison_period"
)

df1 = yf.download(
    stock1,
    period=compare_period,
    auto_adjust=True,
    progress=False
)

df2 = yf.download(
    stock2,
    period=compare_period,
    auto_adjust=True,
    progress=False
)

df3 = yf.download(
    stock3,
    period=compare_period,
    auto_adjust=True,
    progress=False
)

comparison_chart = go.Figure()

comparison_chart.add_trace(
    go.Scatter(
        x=df1.index,
        y=df1["Close"],
        mode="lines",
        name=stock1
    )
)

comparison_chart.add_trace(
    go.Scatter(
        x=df2.index,
        y=df2["Close"],
        mode="lines",
        name=stock2
    )
)

comparison_chart.add_trace(
    go.Scatter(
        x=df3.index,
        y=df3["Close"],
        mode="lines",
        name=stock3
    )
)

comparison_chart.update_layout(
    title="Stock Price Comparison",
    xaxis_title="Date",
    yaxis_title="Price",
    hovermode="x unified"
)

st.plotly_chart(
    comparison_chart,
    use_container_width=True
)

st.subheader("📈 Performance Comparison (%)")

def normalize_data(data):
    close = data["Close"]

    return ((close / close.iloc[0]) - 1) * 100


performance_chart = go.Figure()

performance_chart.add_trace(
    go.Scatter(
        x=df1.index,
        y=normalize_data(df1),
        mode="lines",
        name=stock1
    )
)

performance_chart.add_trace(
    go.Scatter(
        x=df2.index,
        y=normalize_data(df2),
        mode="lines",
        name=stock2
    )
)

performance_chart.add_trace(
    go.Scatter(
        x=df3.index,
        y=normalize_data(df3),
        mode="lines",
        name=stock3
    )
)

performance_chart.update_layout(
    title="Normalized Stock Performance",
    xaxis_title="Date",
    yaxis_title="Return (%)",
    hovermode="x unified"
)

st.plotly_chart(
    performance_chart,
    use_container_width=True
)

def create_database():

    conn = sqlite3.connect("database/watchlist.db")

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS watchlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT UNIQUE
        )
    """)

    conn.commit()
    conn.close()


create_database()

st.sidebar.subheader("⭐ Watchlist")

watchlist_stock = st.sidebar.text_input(
    "Add Stock",
    placeholder="Example: AAPL"
)

if st.sidebar.button("Add to Watchlist"):

    if watchlist_stock:

        conn = sqlite3.connect(
            "database/watchlist.db"
        )

        cursor = conn.cursor()

        try:

            cursor.execute(
                "INSERT INTO watchlist (symbol) VALUES (?)",
                (watchlist_stock.upper(),)
            )

            conn.commit()

            st.sidebar.success(
                f"{watchlist_stock.upper()} added!"
            )

        except sqlite3.IntegrityError:

            st.sidebar.warning(
                "Stock already exists!"
            )

        conn.close()

def get_watchlist():

    conn = sqlite3.connect(
        "database/watchlist.db"
    )

    cursor = conn.cursor()

    cursor.execute(
        "SELECT symbol FROM watchlist"
    )

    stocks = cursor.fetchall()

    conn.close()

    return [stock[0] for stock in stocks]


st.sidebar.subheader("📋 My Watchlist")

watchlist = get_watchlist()

if watchlist:

    for symbol in watchlist:
        st.sidebar.write(f"⭐ {symbol}")

else:

    st.sidebar.info(
        "Your watchlist is empty."
    )

if watchlist:

    remove_stock = st.sidebar.selectbox(
        "Remove Stock",
        watchlist
    )

    if st.sidebar.button("Remove"):

        conn = sqlite3.connect(
            "database/watchlist.db"
        )

        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM watchlist WHERE symbol = ?",
            (remove_stock,)
        )

        conn.commit()
        conn.close()

        st.sidebar.success(
            f"{remove_stock} removed!"
        )

        st.rerun()

year_data = ticker.history(period="1y")

if not year_data.empty:

    week52_high = year_data["High"].max()

    week52_low = year_data["Low"].min()

    col1, col2 = st.columns(2)

    col1.metric(
        "52 Week High",
        f"${week52_high:.2f}"
    )

    col2.metric(
        "52 Week Low",
        f"${week52_low:.2f}"
    )

if len(df) >= 2:

    previous_close = df["Close"].iloc[-2]

    price_change = current_price - previous_close

    percentage_change = (
        price_change / previous_close
    ) * 100

    st.metric(
        "Price Change",
        f"${price_change:.2f}",
        f"{percentage_change:.2f}%"
    )

if st.button("🔄 Refresh Data"):

    st.cache_data.clear()

    st.rerun()

st.divider()

st.markdown(
    """
    ### 📊 Real-Time Stock Market Dashboard

    Built using Python, Pandas, Plotly, yFinance and Streamlit.

    **Disclaimer:** This dashboard is for educational
    and informational purposes only and should not be
    considered financial advice.
    """
)

# ==============================
# STOCK NEWS
# ==============================

st.subheader("📰 Latest Stock News")

try:
    news = ticker.news

    if news:

        for item in news[:5]:

            title = item.get("title", "No title available")
            publisher = item.get("publisher", "Unknown source")
            link = item.get("link", "#")

            st.markdown(
                f"""
                ### {title}

                **Source:** {publisher}

                [Read Full Article]({link})

                ---
                """
            )

    else:
        st.info("No recent news available.")

except Exception as e:
    st.warning("Unable to load news at the moment.")

df = ticker.history(period=period)
if df.empty:

    st.error(
        f"❌ No data found for '{stock}'. "
        "Please check the stock symbol."
    )

    st.stop()

st.subheader("🟢 Market Information")

current_price = df["Close"].iloc[-1]

previous_close = df["Close"].iloc[-2]

change = current_price - previous_close

change_percent = (
    change / previous_close
) * 100

if change > 0:

    status = "📈 Positive"

elif change < 0:

    status = "📉 Negative"

else:

    status = "➡️ Unchanged"

st.write(f"Market movement: **{status}**")

year_data = ticker.history(period="1y")

if not year_data.empty:

    week52_high = year_data["High"].max()

    week52_low = year_data["Low"].min()

    col1, col2 = st.columns(2)

    col1.metric(
        "52 Week High",
        f"{week52_high:.2f}"
    )

    col2.metric(
        "52 Week Low",
        f"{week52_low:.2f}"
    )

csv_data = df.to_csv().encode("utf-8")

st.download_button(
    label="⬇️ Download Stock Data",
    data=csv_data,
    file_name=f"{stock}_data.csv",
    mime="text/csv"
)