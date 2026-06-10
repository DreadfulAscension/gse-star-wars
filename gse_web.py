import streamlit as st
import random
import json
from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objects as go
import os

st.set_page_config(
    page_title="Galactic Trade Network",
    layout="wide",
    page_icon="🌌",
    initial_sidebar_state="expanded"
)

# ====================== GTN / SWTOR POLISHED CSS ======================
st.markdown("""
<style>
    /* Deep space background with starfield */
    .stApp {
        background: linear-gradient(rgba(8, 12, 28, 0.92), rgba(2, 4, 18, 0.95)), 
                    url('https://images.unsplash.com/photo-1464802686167-b939a7060ca4?ixlib=rb-4.0.3&q=85&fm=jpg&crop=entropy&cs=srgb') center/cover fixed;
        color: #00f5ff;
        font-family: 'Segoe UI', system-ui, sans-serif;
    }

    /* Holographic Main Header */
    .main-header {
        background: linear-gradient(90deg, #001122, #003355, #001122);
        padding: 25px 30px;
        border: 2px solid #00ccff;
        border-radius: 8px;
        margin-bottom: 20px;
        box-shadow: 0 0 30px rgba(0, 204, 255, 0.5);
        text-align: center;
        position: relative;
    }
    .main-header h1 {
        color: #00ffff !important;
        font-size: 3rem;
        text-shadow: 
            0 0 10px #00ffff,
            0 0 25px #00ffff,
            0 0 45px #0088ff;
        letter-spacing: 8px;
        margin: 0;
        text-transform: uppercase;
    }
    .main-header .subtitle {
        color: #aaccff;
        font-size: 1.15rem;
        letter-spacing: 4px;
        margin-top: 8px;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #0a1328;
        border: 2px solid #00aaff;
        border-radius: 6px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #88ccff;
        background-color: #0a1328;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(#003355, #001f33) !important;
        color: #00ffff !important;
        border-bottom: 4px solid #00ffcc;
    }

    /* Dataframes */
    .stDataFrame {
        background-color: #0a1428;
        border: 1px solid #336699;
    }
    .stDataFrame thead th {
        background-color: #001f3a;
        color: #00ffcc;
    }
    .stDataFrame tbody tr:hover {
        background-color: rgba(0, 255, 200, 0.08) !important;
        box-shadow: inset 0 0 12px rgba(0, 255, 200, 0.3);
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(#cc4400, #aa3300);
        color: white;
        border: 2px solid #ff8800;
        border-radius: 4px;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        box-shadow: 0 0 12px #ff5500;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        background: linear-gradient(#ff6600, #dd4400);
        box-shadow: 0 0 25px #ffaa00;
        transform: translateY(-2px);
    }
    .stButton>button[kind="primary"] {
        background: linear-gradient(#00aa77, #008866);
        border-color: #00ffcc;
        box-shadow: 0 0 15px #00ffaa;
    }

    /* Inputs */
    .stTextInput>div>div>input,
    .stSelectbox>div>div>select,
    .stNumberInput>div>div>input {
        background-color: #0a1628;
        color: #bbddff;
        border: 1px solid #4477aa;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #05080f;
        border-right: 3px solid #00aaff;
    }

    /* Messages */
    .stSuccess {
        background-color: #002211;
        border-left: 6px solid #00ff99;
    }
    .stError {
        background-color: #220000;
        border-left: 6px solid #ff5555;
    }

    /* Plotly Charts */
    .js-plotly-plot {
        background-color: #0a1328 !important;
        border: 1px solid #336699;
    }

    /* Subtle scanline + holo effect */
    .stApp::after {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: repeating-linear-gradient(
            transparent 0px,
            transparent 3px,
            rgba(0, 255, 220, 0.025) 3px,
            rgba(0, 255, 220, 0.025) 6px
        );
        pointer-events: none;
        z-index: 9999;
        animation: flicker 8s infinite alternate;
    }

    @keyframes flicker {
        0%   { opacity: 0.95; }
        100% { opacity: 1.0; }
    }
</style>
""", unsafe_allow_html=True)

# ====================== AUTHENTIC GTN HEADER ======================
st.markdown("""
<div class="main-header">
    <h1>GALACTIC TRADE NETWORK</h1>
    <div class="subtitle">THE OLD REPUBLIC ERA • SECURE TRADING TERMINAL</div>
</div>
""", unsafe_allow_html=True)

st.caption(f"**Current Cycle**: {datetime.now().strftime('%Y-%m-%d')} • Terminal Node: COR-77 • Republic/Imperial Joint Venture")

# ====================== STOCK DATABASE ======================
stocks = {
    "KDY": {"name": "Kuat Drive Yards", "price": 245.0, "vol": 0.12, "sector": "Starships", "div_yield": 0.018},
    "CZRK": {"name": "Czerka Corporation", "price": 178.0, "vol": 0.18, "sector": "Conglomerate", "div_yield": 0.012},
    "SITH": {"name": "Imperial Armaments Ltd.", "price": 132.0, "vol": 0.25, "sector": "Military", "div_yield": 0.008},
    "CORE": {"name": "Corellian Engineering", "price": 89.0, "vol": 0.14, "sector": "Starships", "div_yield": 0.015},
    "ARAK": {"name": "Arakyd Industries", "price": 156.0, "vol": 0.20, "sector": "Droids", "div_yield": 0.010},
    "HUTC": {"name": "Hutt Cartel Ventures", "price": 67.0, "vol": 0.35, "sector": "Crime", "div_yield": 0.025},
    "MEDT": {"name": "MedTech Solutions", "price": 203.0, "vol": 0.08, "sector": "Healthcare", "div_yield": 0.028},
    "GALM": {"name": "Galactic Mining Guild", "price": 94.0, "vol": 0.16, "sector": "Resources", "div_yield": 0.020},
    "NEUR": {"name": "Neuroniix", "price": 312.0, "vol": 0.28, "sector": "Biotech", "div_yield": 0.005},
    "LUXE": {"name": "LuxeLine Cruises", "price": 145.0, "vol": 0.10, "sector": "Luxury", "div_yield": 0.022},
    "REPC": {"name": "Republic Engineering Corp.", "price": 167.0, "vol": 0.13, "sector": "Infrastructure", "div_yield": 0.019},
    "TRAN": {"name": "TransGalMeg Industries", "price": 98.0, "vol": 0.15, "sector": "Logistics", "div_yield": 0.014},
    "CRYS": {"name": "Crystal Dynamics", "price": 221.0, "vol": 0.24, "sector": "Mystech", "div_yield": 0.009},
    "BIOZ": {"name": "Bio-Zenith", "price": 184.0, "vol": 0.19, "sector": "Pharma", "div_yield": 0.016},
    "ENER": {"name": "Energen Power", "price": 119.0, "vol": 0.14, "sector": "Energy", "div_yield": 0.021},
    "SHAD": {"name": "ShadowNet Syndicates", "price": 76.0, "vol": 0.32, "sector": "Espionage", "div_yield": 0.030},
    "SENX": {"name": "Senna Consumer Group", "price": 53.0, "vol": 0.09, "sector": "Retail", "div_yield": 0.023},
    "BANU": {"name": "Bantha Brands Inc.", "price": 41.0, "vol": 0.11, "sector": "Consumer", "div_yield": 0.027},
    "JAL": {"name": "Jalaar Shipyards", "price": 134.0, "vol": 0.17, "sector": "Starships", "div_yield": 0.013},
    "VOSS": {"name": "Voss Mystics Ltd.", "price": 158.0, "vol": 0.22, "sector": "Cultural", "div_yield": 0.011},
}

DATA_FILE = "gse_data.json"

def load_data():
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                for t, p in data.get("stocks", {}).items():
                    if t in stocks:
                        stocks[t]["price"] = float(p)
                return (data.get("portfolios", {}), 
                        datetime.fromisoformat(data.get("current_date", datetime.now().isoformat())),
                        data.get("price_history", {}),
                        data.get("portfolio_history", {}))
    except:
        pass
    return {}, datetime.now(), {}, {}

def save_data(portfolios, current_date, price_history, portfolio_history):
    try:
        data = {
            "stocks": {t: stocks[t]["price"] for t in stocks},
            "portfolios": portfolios,
            "current_date": current_date.isoformat(),
            "price_history": price_history,
            "portfolio_history": portfolio_history
        }
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except:
        pass

# ====================== SESSION STATE ======================
if 'initialized' not in st.session_state:
    st.session_state.portfolios, st.session_state.current_date, st.session_state.price_history, st.session_state.portfolio_history = load_data()
    st.session_state.initialized = True

portfolios = st.session_state.portfolios
price_history = st.session_state.price_history
portfolio_history = st.session_state.portfolio_history

# Initialize histories
for ticker in stocks:
    if ticker not in price_history or len(price_history[ticker]) == 0:
        price_history[ticker] = [{"date": st.session_state.current_date.strftime('%Y-%m-%d'), "price": stocks[ticker]["price"]}]

def simulate_week():
    for ticker, data in stocks.items():
        roll = random.gauss(0, data["vol"] * 100)
        if roll > 20: change = random.uniform(18, 40)
        elif roll > 8: change = random.uniform(5, 18)
        elif roll > -9: change = random.uniform(-5, 5)
        elif roll > -21: change = random.uniform(-18, -5)
        else: change = random.uniform(-40, -18)
        
        new_price = max(1.0, round(data["price"] * (1 + change/100), 2))
        data["price"] = new_price
        price_history[ticker].append({"date": st.session_state.current_date.strftime('%Y-%m-%d'), "price": new_price})
    
    st.session_state.current_date += timedelta(days=7)
    
    # Record Portfolio Performance
    for player, p in portfolios.items():
        if player not in portfolio_history:
            portfolio_history[player] = []
        holdings = p.get("holdings", {})
        net_worth = p.get("cash", 0)
        for t, shares in holdings.items():
            if t in stocks:
                net_worth += shares * stocks[t]["price"]
        portfolio_history[player].append({
            "date": st.session_state.current_date.strftime('%Y-%m-%d'),
            "net_worth": round(net_worth, 2)
        })
    
    # Quarterly Dividends
    if st.session_state.current_date.day % 28 < 7:
        for player, p in portfolios.items():
            total_div = 0
            for ticker, shares in p.get("holdings", {}).items():
                if ticker in stocks and shares > 0:
                    div = stocks[ticker]["price"] * stocks[ticker]["div_yield"] * shares / 4
                    p["cash"] += div
                    total_div += div
            if total_div > 0:
                st.success(f"💰 Dividends Paid to {player}: {total_div:,.2f} GC")

# ====================== UI TABS ======================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📊 Market", "📈 Stock Charts", "💼 Portfolio", "📈 Portfolio Performance", "🚀 Simulate", "🏦 Takeover"])

with tab1:
    st.subheader("Current Market Prices")
    df = pd.DataFrame([{
        "Ticker": t, 
        "Company": info["name"], 
        "Price (GC)": f"{info['price']:,.2f}", 
        "Div Yield": f"{info['div_yield']*100:.1f}%"
    } for t, info in stocks.items()])
    st.dataframe(df, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("Stock Price Charts")
    ticker = st.selectbox("Select Company", list(stocks.keys()))
    weeks = st.slider("Show last N weeks", 5, 100, 40)
    history = price_history.get(ticker, [])
    st.caption(f"Data points: **{len(history)}**")
    if len(history) > 1:
        df = pd.DataFrame(history[-weeks:])
        df["date"] = pd.to_datetime(df["date"])
        fig = go.Figure(go.Scatter(x=df["date"], y=df["price"], mode='lines+markers'))
        fig.update_layout(title=f"{ticker} - {stocks[ticker]['name']}", height=550)
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("💼 Your Portfolio")
    player = st.text_input("Character Name", "Jedi Knight Sera", key="player_name")
    
    if player not in portfolios:
        if st.button("Create Portfolio"):
            portfolios[player] = {"cash": 250000.0, "holdings": {}}
            st.rerun()
    
    if player in portfolios:
        p = portfolios[player]
        st.write(f"**Cash**: {p['cash']:,.2f} GC")
        
        holdings = p.get("holdings", {})
        rows = []
        net = p["cash"]
        for t, info in stocks.items():
            shares = holdings.get(t, 0)
            value = shares * info["price"]
            net += value
            rows.append({
                "Ticker": t, 
                "Company": info["name"], 
                "Shares": shares, 
                "Price": f"{info['price']:,.2f}", 
                "Value": f"{value:,.2f}"
            })
        
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        st.write(f"**Net Worth**: {net:,.2f} GC")

        st.subheader("Trade")
        c1, c2, c3 = st.columns(3)
        with c1: 
            tr_ticker = st.selectbox("Company", list(stocks.keys()), key="trade")
        with c2: 
            action = st.radio("Action", ["Buy", "Sell"])
        with c3: 
            qty = st.number_input("Shares", min_value=1, value=100)
        
        if st.button(action, type="primary"):
            current_price = stocks[tr_ticker]["price"]
            if action == "Buy":
                cost = current_price * qty * 1.015
                if p["cash"] >= cost:
                    p["cash"] -= cost
                    p["holdings"][tr_ticker] = p["holdings"].get(tr_ticker, 0) + qty
                    st.success(f"Bought {qty} shares of {tr_ticker}!")
                else:
                    st.error("Not enough credits!")
            else:
                holdings = p.get("holdings", {})
                if tr_ticker in holdings and holdings[tr_ticker] >= qty:
                    revenue = current_price * qty * 0.985
                    p["cash"] += revenue
                    p["holdings"][tr_ticker] -= qty
                    if p["holdings"][tr_ticker] <= 0:
                        del p["holdings"][tr_ticker]
                    st.success(f"Sold {qty} shares of {tr_ticker}!")
                else:
                    st.error("Not enough shares!")
            st.rerun()

with tab4:
    st.subheader("📈 Portfolio Performance")
    if portfolio_history:
        player_sel = st.selectbox("Select Player", list(portfolio_history.keys()), key="perf_player")
        hist = portfolio_history[player_sel]
        st.caption(f"Performance data points: **{len(hist)}**")
        if len(hist) > 1:
            df = pd.DataFrame(hist)
            df["date"] = pd.to_datetime(df["date"])
            fig = go.Figure(go.Scatter(x=df["date"], y=df["net_worth"], mode='lines+markers'))
            fig.update_layout(title=f"{player_sel}'s Net Worth Over Time", height=600)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Simulate several weeks to see performance history.")
    else:
        st.info("No portfolio history yet. Simulate weeks after creating a portfolio.")

with tab5:
    st.subheader("Advance the Market")
    weeks = st.slider("Number of weeks", 1, 12, 1)
    if st.button("🚀 Simulate Weeks", type="primary"):
        for _ in range(weeks):
            simulate_week()
        st.success(f"Advanced {weeks} weeks!")
        st.rerun()

with tab6:
    st.info("🏦 Corporate Takeover system coming soon...")

# ====================== SIDEBAR ======================
with st.sidebar:
    if st.button("💾 Save Game"):
        save_data(portfolios, st.session_state.current_date, price_history, portfolio_history)
        st.success("Game Saved Successfully!")

# Auto-save on every run
save_data(portfolios, st.session_state.current_date, price_history, portfolio_history)
