import streamlit as st
import random
import json
from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objects as go

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

if 'initialized' not in st.session_state:
    st.session_state.portfolios, st.session_state.current_date, st.session_state.price_history, st.session_state.portfolio_history = load_data()
    st.session_state.initialized = True

portfolios = st.session_state.portfolios
price_history = st.session_state.price_history
portfolio_history = st.session_state.portfolio_history

# Initialize price history
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

# ====================== UI ======================
st.title("🌌 Galactic Stock Exchange")
st.caption(f"**The Old Republic Era** • {st.session_state.current_date.strftime('%Y-%m-%d')}")

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
    st.caption(f"Data points available: **{len(history)}**")
    
    if len(history) > 1:
        df = pd.DataFrame(history[-weeks:])
        df["date"] = pd.to_datetime(df["date"])
        fig = go.Figure(go.Scatter(x=df["date"], y=df["price"], mode='lines+markers'))
        fig.update_layout(title=f"{ticker} - {stocks[ticker]['name']}", height=550)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Simulate at least 2-3 weeks to generate chart data.")

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
                "Value": f"{value:,.2f}",
                "Div Yield": f"{info['div_yield']*100:.1f}%"
            })
        
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        st.write(f"**Net Worth**: {net:,.2f} GC")

        st.subheader("Trade")
        c1, c2, c3 = st.columns(3)
        with c1:
            tr_ticker = st.selectbox("Company", list(stocks.keys()), key="trade_ticker")
        with c2:
            action = st.radio("Action", ["Buy", "Sell"])
        with c3:
            qty = st.number_input("Shares", min_value=1, value=100)
        
        if st.button(action, type="primary"):
            current_price = stocks[tr_ticker]["price"]
            st.info(f"Current price of **{tr_ticker}**: {current_price:,.2f} GC")
            
            if action == "Buy":
                cost = current_price * qty * 1.015
                if p["cash"] >= cost:
                    p["cash"] -= cost
                    p["holdings"][tr_ticker] = p["holdings"].get(tr_ticker, 0) + qty
                    st.success(f"Bought {qty} shares at {current_price:,.2f} GC")
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
                    st.success(f"Sold {qty} shares at {current_price:,.2f} GC")
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

with tab5:
    st.subheader("Advance the Market")
    weeks = st.slider("Number of weeks", 1, 12, 1)
    if st.button("🚀 Simulate Weeks", type="primary"):
        for _ in range(weeks):
            simulate_week()
        st.success(f"Advanced {weeks} weeks!")
        st.rerun()

with st.sidebar:
    if st.button("💾 Save Game"):
        save_data(portfolios, st.session_state.current_date, price_history, portfolio_history)
        st.success("Game Saved!")

save_data(portfolios, st.session_state.current_date, price_history, portfolio_history)
