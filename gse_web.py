import streamlit as st
import random
import json
from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objects as go
import os

st.set_page_config(page_title="Galactic Stock Exchange", layout="wide", page_icon="🌌")

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
                for ticker, price in data.get("stocks", {}).items():
                    if ticker in stocks:
                        stocks[ticker]["price"] = float(price)
                return (
                    data.get("portfolios", {}),
                    datetime.fromisoformat(data.get("current_date", datetime.now().isoformat())),
                    data.get("price_history", {})
                )
    except:
        pass
    return {}, datetime.now(), {}

def save_data(portfolios, current_date, price_history):
    try:
        data = {
            "stocks": {t: stocks[t]["price"] for t in stocks},
            "portfolios": portfolios,
            "current_date": current_date.isoformat(),
            "price_history": price_history
        }
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except:
        pass

# ====================== INITIALIZE ======================
if 'initialized' not in st.session_state:
    st.session_state.portfolios, st.session_state.current_date, st.session_state.price_history = load_data()
    st.session_state.initialized = True

portfolios = st.session_state.portfolios
price_history = st.session_state.price_history

# Initialize price history for all stocks
for ticker in stocks:
    if ticker not in price_history:
        price_history[ticker] = [{"date": st.session_state.current_date.strftime('%Y-%m-%d'), "price": stocks[ticker]["price"]}]

# ====================== SIMULATE ======================
def simulate_week():
    for ticker, data in stocks.items():
        roll = random.gauss(0, data["vol"] * 100)
        
        if roll > 20:   change = random.uniform(18, 40)
        elif roll > 8:  change = random.uniform(5, 18)
        elif roll > -9: change = random.uniform(-5, 5)
        elif roll > -21:change = random.uniform(-18, -5)
        else:           change = random.uniform(-40, -18)
        
        new_price = max(1.0, round(data["price"] * (1 + change/100), 2))
        data["price"] = new_price
        
        price_history[ticker].append({
            "date": st.session_state.current_date.strftime('%Y-%m-%d'),
            "price": new_price
        })
    
    st.session_state.current_date += timedelta(days=7)

# ====================== UI ======================
st.title("🌌 Galactic Stock Exchange")
st.caption(f"**The Old Republic Era** • {st.session_state.current_date.strftime('%Y-%m-%d')}")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Market", "📈 Charts", "💼 Portfolio", "🚀 Simulate", "🏦 Takeover"])

with tab1:
    st.subheader("Current Market Prices")
    market_data = [{
        "Ticker": t,
        "Company": info["name"],
        "Sector": info["sector"],
        "Price (GC)": f"{info['price']:,.2f}",
        "Div Yield": f"{info['div_yield']*100:.1f}%"
    } for t, info in stocks.items()]
    st.dataframe(pd.DataFrame(market_data), use_container_width=True, hide_index=True)

with tab2:
    st.subheader("Price History Charts")
    ticker = st.selectbox("Select Company", list(stocks.keys()))
    weeks = st.slider("Show last N weeks", 5, 100, 40)
    
    if ticker in price_history and len(price_history[ticker]) > 1:
        df = pd.DataFrame(price_history[ticker][-weeks:])
        df["date"] = pd.to_datetime(df["date"])
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["date"], y=df["price"], mode='lines+markers'))
        fig.update_layout(title=f"{ticker} - {stocks[ticker]['name']}", xaxis_title="Date", yaxis_title="Price (GC)", template="plotly_dark", height=500)
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    player = st.text_input("Character Name", "Jedi Knight Sera")
    if player not in portfolios:
        if st.button("Create Portfolio"):
            portfolios[player] = {"cash": 250000.0, "holdings": {}}
            st.rerun()
    
    if player in portfolios:
        p = portfolios[player]
        st.write(f"**Cash**: {p['cash']:,.2f} GC")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            tr_ticker = st.selectbox("Ticker", list(stocks.keys()), key="trade_ticker")
        with col2:
            action = st.radio("Action", ["Buy", "Sell"])
        with col3:
            qty = st.number_input("Shares", min_value=1, value=100)
        
        if st.button(action, type="primary"):
            price = stocks[tr_ticker]["price"]
            if action == "Buy":
                cost = price * qty * 1.015
                if p["cash"] >= cost:
                    p["cash"] -= cost
                    p["holdings"][tr_ticker] = p["holdings"].get(tr_ticker, 0) + qty
                    st.success("✅ Bought!")
                else:
                    st.error("Not enough credits!")
            else:
                if tr_ticker in p.get("holdings", {}) and p["holdings"][tr_ticker] >= qty:
                    p["cash"] += price * qty * 0.985
                    p["holdings"][tr_ticker] -= qty
                    if p["holdings"][tr_ticker] <= 0:
                        del p["holdings"][
