import streamlit as st
import random
import json
from datetime import datetime, timedelta
import os
import pandas as pd
import plotly.graph_objects as go

# ====================== PAGE CONFIG ======================
st.set_page_config(
    page_title="Galactic Stock Exchange",
    layout="wide",
    page_icon="🌌",
    initial_sidebar_state="expanded"
)

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
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            for ticker, price in data.get("stocks", {}).items():
                if ticker in stocks:
                    stocks[ticker]["price"] = price
            return (data.get("portfolios", {}), 
                    datetime.fromisoformat(data.get("current_date", datetime.now().isoformat())),
                    data.get("price_history", {}))
    return {}, datetime.now(), {}

def save_data(portfolios, current_date, price_history):
    data = {
        "stocks": {t: stocks[t]["price"] for t in stocks},
        "portfolios": portfolios,
        "current_date": current_date.isoformat(),
        "price_history": price_history
    }
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# Initialize session state
if 'portfolios' not in st.session_state:
    st.session_state.portfolios, st.session_state.current_date, st.session_state.price_history = load_data()

portfolios = st.session_state.portfolios
current_date = st.session_state.current_date
price_history = st.session_state.price_history

# Initialize price history
for ticker in stocks:
    if ticker not in price_history:
        price_history[ticker] = [{"date": current_date.strftime('%Y-%m-%d'), "price": stocks[ticker]["price"]}]

# ====================== HELPER FUNCTIONS ======================
def simulate_week(manual_modifiers=None, event_desc=""):
    if manual_modifiers is None:
        manual_modifiers = {}
    
    for ticker, data in stocks.items():
        mod = manual_modifiers.get(ticker, 0)
        roll = random.gauss(0, data["vol"] * 100) + mod * 6
        
        if roll > 20:   change_pct = random.uniform(18, 40)
        elif roll > 8:  change_pct = random.uniform(5, 18)
        elif roll > -9: change_pct = random.uniform(-5, 5)
        elif roll > -21:change_pct = random.uniform(-18, -5)
        else:           change_pct = random.uniform(-40, -18)
        
        new_price = max(1.0, round(data["price"] * (1 + change_pct/100), 2))
        data["price"] = new_price
        
        # Record history
        price_history[ticker].append({
            "date": current_date.strftime('%Y-%m-%d'),
            "price": new_price
        })
    
    global current_date
    current_date += timedelta(days=7)
    st.session_state.current_date = current_date

def pay_dividends():
    total_paid = {}
    for player, portfolio in portfolios.items():
        div_total = 0
        for ticker, shares in portfolio.get("holdings", {}).items():
            if ticker in stocks and shares > 0:
                div = stocks[ticker]["price"] * stocks[ticker]["div_yield"] * shares / 4
                portfolio["cash"] += div
                div_total += div
        if div_total > 0:
            total_paid[player] = round(div_total, 2)
    return total_paid

def calculate_takeover(ticker, shares_owned, total_shares=10000000):
    ownership = (shares_owned / total_shares) * 100
    if ownership < 15:
        return ownership, 0
    chance = max(0, min(95, (ownership - 15) * 4 - stocks[ticker]["vol"] * 30))
    return ownership, chance

# ====================== MAIN UI ======================
st.title("🌌 Galactic Stock Exchange")
st.caption(f"**Star Wars: The Old Republic** | {current_date.strftime('%Y-%m-%d')}")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Market", "📈 Charts", "💼 Portfolio", "🚀 Simulate", "🏦 Takeover"])

with tab1:
    st.subheader("Current Market Prices")
    data = []
    for t, info in stocks.items():
        data.append({
            "Ticker": t,
            "Company": info["name"],
            "Sector": info["sector"],
            "Price": f"{info['price']:,.2f}",
            "Vol": info["vol"],
            "Div Yield": f"{info['div_yield']*100:.1f}%"
        })
    st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)

with tab2:
    st.subheader("Interactive Price Charts")
    ticker = st.selectbox("Select Company", options=list(stocks.keys()), key="chart_select")
    weeks = st.slider("Show last N weeks", 5, 100, 52)
    
    if ticker in price_history and len(price_history[ticker]) > 1:
        df = pd.DataFrame(price_history[ticker][-weeks:])
        df["date"] = pd.to_datetime(df["date"])
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["date"], y=df["price"], mode='lines+markers', name=stocks[ticker]["name"], line=dict(width=3)))
        fig.update_layout(
            title=f"{ticker} - {stocks[ticker]['name']}",
            xaxis_title="Date",
            yaxis_title="Price (GC)",
            template="plotly_dark",
            height=550
        )
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    player = st.text_input("Character / Player Name", value="Jedi Knight Sera")
    if player not in portfolios:
        if st.button("Create Portfolio"):
            portfolios[player] = {"cash": 250000, "holdings": {}}
            st.success(f"Portfolio created for {player}!")
            st.rerun()
    
    if player in portfolios:
        p = portfolios[player]
        st.write(f"**Cash**: {p['cash']:,.2f} GC")
        
        if p.get("holdings"):
            holdings = []
            net = p["cash"]
            for t, qty in p["holdings"].items():
                val = qty * stocks[t]["price"]
                net += val
                holdings.append({"Ticker": t, "Shares": qty, "Price": stocks[t]["price"], "Value": val})
            st.dataframe(pd.DataFrame(holdings), use_container_width=True)
            st.write(f"**Net Worth**: {net:,.2f} GC")
        
        # Trade
        c1, c2, c3 = st.columns(3)
        with c1:
            trade_ticker = st.selectbox("Ticker", list(stocks.keys()), key="trade")
        with c2:
            action = st.radio("Action", ["Buy", "Sell"])
        with c3:
            qty = st.number_input("Shares", min_value=1, value=100)
        
        if st.button(action):
            price = stocks[trade_ticker]["price"]
            if action == "Buy":
                cost = price * qty * 1.015
                if p["cash"] >= cost:
                    p["cash"] -= cost
                    p["holdings"][trade_ticker] = p["holdings"].get(trade_ticker, 0) + qty
                    st.success("Purchase successful!")
                else:
                    st.error("Not enough credits!")
            else:
                if trade_ticker in p["holdings"] and p["holdings"][trade_ticker] >= qty:
                    revenue = price * qty * 0.985
                    p["cash"] += revenue
                    p["holdings"][trade_ticker] -= qty
                    if p["holdings"][trade_ticker] <= 0:
                        del p["holdings"][trade_ticker]
                    st.success("Sale successful!")
                else:
                    st.error("Not enough shares!")
            st.rerun()

with tab4:
    st.subheader("Advance the Market")
    weeks = st.slider("Weeks to simulate", 1, 12, 1)
    event = st.text_input("Galactic Event (optional)")
    
    if st.button("🚀 Simulate Weeks", type="primary"):
        for _ in range(weeks):
            simulate_week({}, event)
        st.success(f"Market advanced {weeks} weeks!")
        st.rerun()

with tab5:
    st.subheader("Hostile Takeover")
    tkr = st.selectbox("Target Company", list(stocks.keys()), key="takeover")
    shares = st.number_input("Shares Owned", 0, 10000000, 1500000, step=100000)
    pct, chance = calculate_takeover(tkr, shares)
    st.metric("Ownership", f"{pct:.2f}%")
    st.metric("Success Chance", f"{chance:.1f}%")

# Sidebar
with st.sidebar:
    if st.button("💾 Save Game"):
        save_data(portfolios, current_date, price_history)
        st.success("Saved!")
    
    st.caption("Star Wars: The Old Republic\nGalactic Stock Market Simulator")

# Auto-save
save_data(portfolios, current_date, price_history)
