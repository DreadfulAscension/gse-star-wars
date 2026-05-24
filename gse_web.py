import streamlit as st
import random
import json
from datetime import datetime, timedelta
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ====================== CONFIG ======================
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

# Initialize history for new stocks
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
        
        old_price = data["price"]
        new_price = max(1.0, round(old_price * (1 + change_pct/100), 2))
        data["price"] = new_price
        
        # Record history
        if ticker not in price_history:
            price_history[ticker] = []
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

def calculate_takeover(ticker, shares_owned, total_shares=10_000_000):
    ownership = (shares_owned / total_shares) * 100
    if ownership < 15:
        return ownership, 0
    chance = max(0, min(95, (ownership - 15) * 4 - stocks[ticker]["vol"] * 30))
    return ownership, chance

# ====================== UI ======================
st.title("🌌 Galactic Stock Exchange")
st.caption(f"**The Old Republic Era** | {current_date.strftime('%Y-%m-%d')}")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Market Overview", "📈 Price Charts", "💼 Portfolio", "📈 Simulate", "🏦 Corporate Control"])

# ------------------- TAB 1: MARKET OVERVIEW -------------------
with tab1:
    st.subheader("Current Market Prices")
    data = []
    for t, info in stocks.items():
        data.append({
            "Ticker": t,
            "Company": info["name"],
            "Sector": info["sector"],
            "Price (GC)": f"{info['price']:,.2f}",
            "Vol": f"{info['vol']:.2f}",
            "Div %": f"{info['div_yield']*100:.1f}%"
        })
    st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)

# ------------------- TAB 2: INTERACTIVE PRICE CHARTS -------------------
with tab2:
    st.subheader("Interactive Price History")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        selected_ticker = st.selectbox("Select Company", options=list(stocks.keys()), key="chart_ticker")
        show_all = st.checkbox("Compare with GSE Index", value=False)
    
    with col2:
        period = st.slider("Show last N weeks", 4, 104, 52)
    
    if selected_ticker in price_history and len(price_history[selected_ticker]) > 1:
        df = pd.DataFrame(price_history[selected_ticker][-period:])
        df["date"] = pd.to_datetime(df["date"])
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["date"], 
            y=df["price"],
            mode='lines+markers',
            name=stocks[selected_ticker]["name"],
            line=dict(width=3)
        ))
        
        fig.update_layout(
            title=f"{selected_ticker} - {stocks[selected_ticker]['name']} Price History",
            xaxis_title="Date",
            yaxis_title="Price (Galactic Credits)",
            hovermode="x unified",
            template="plotly_dark",
            height=600
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Statistics
        prices = df["price"]
        st.metric("Current Price", f"{prices.iloc[-1]:,.2f} GC", 
                 f"{((prices.iloc[-1]/prices.iloc[0])-1)*100:+.2f}%")
    else:
        st.info("Not enough history yet. Simulate some weeks!")

# ------------------- TAB 3: PORTFOLIO -------------------
with tab3:
    col1, col2 = st.columns([1, 1])
    with col1:
        player_name = st.text_input("Player / Character Name", value="Jedi Knight Sera")
        if player_name not in portfolios:
            if st.button("Create New Portfolio"):
                portfolios[player_name] = {"cash": 250000, "holdings": {}}
                st.success(f"Portfolio created for {player_name}!")
                st.rerun()
    
    if player_name in portfolios:
        p = portfolios[player_name]
        st.subheader(f"{player_name}'s Portfolio")
        st.write(f"**Cash**: {p['cash']:,.2f} GC")
        
        if p.get("holdings"):
            holdings_data = []
            net_worth = p["cash"]
            for t, shares in p["holdings"].items():
                value = shares * stocks[t]["price"]
                net_worth += value
                holdings_data.append({"Ticker": t, "Shares": shares, "Price": stocks[t]["price"], "Value": round(value,2)})
            st.dataframe(pd.DataFrame(holdings_data), use_container_width=True)
            st.write(f"**Net Worth**: {net_worth:,.2f} GC")
        else:
            st.info("No holdings yet.")

        # Buy / Sell Section
        st.subheader("Trade")
        c1, c2, c3 = st.columns(3)
        with c1:
            ticker = st.selectbox("Ticker", options=list(stocks.keys()), key="trade_ticker")
        with c2:
            action = st.radio("Action", ["Buy", "Sell"])
        with c3:
            qty = st.number_input("Quantity", min_value=1, value=100)
        
        if st.button(action, type="primary"):
            price = stocks[ticker]["price"]
            if action == "Buy":
                cost = price * qty * 1.015
                if p["cash"] >= cost:
                    p["cash"] -= cost
                    p["holdings"][ticker] = p["holdings"].get(ticker, 0) + qty
                    st.success(f"Bought {qty:,} shares of {ticker}!")
                else:
                    st.error("Insufficient funds!")
            else:
                if ticker in p["holdings"] and p["holdings"][ticker] >= qty:
                    revenue = price * qty * 0.985
                    p["cash"] += revenue
                    p["holdings"][ticker] -= qty
                    if p["holdings"][ticker] <= 0:
                        del p["holdings"][ticker]
                    st.success(f"Sold {qty:,} shares of {ticker}!")
                else:
                    st.error("Not enough shares to sell!")
            st.rerun()

# ------------------- TAB 4: SIMULATE -------------------
with tab4:
    st.subheader("Advance Galactic Market")
    weeks = st.slider("Weeks to simulate", 1, 12, 1)
    event_desc = st.text_input("Major Galactic Event (optional)")
    
    modifiers = {}
    with st.expander("Custom Modifiers (Player Influence)"):
        cols = st.columns(5)
        for i, t in enumerate(stocks.keys()):
            with cols[i % 5]:
                mod = st.number_input(f"{t}", value=0, min_value=-10, max_value=10, key=f"mod_{t}")
                if mod != 0:
                    modifiers[t] = mod
    
    if st.button("🚀 Simulate Weeks", type="primary"):
        for _ in range(weeks):
            simulate_week(modifiers, event_desc)
        st.success(f"Advanced {weeks} weeks to {current_date.strftime('%Y-%m-%d')}")
        
        if current_date.day % 30 < 7:
            dividends = pay_dividends()
            if dividends:
                st.write("**Dividends Paid This Quarter:**")
                for p_name, amt in dividends.items():
                    st.write(f"• {p_name}: **{amt:,.2f} GC**")
        st.rerun()

# ------------------- TAB 5: CORPORATE CONTROL -------------------
with tab5:
    st.subheader("Hostile Takeover Calculator")
    tkr = st.selectbox("Target Company", list(stocks.keys()), key="takeover_tkr")
    shares = st.number_input("Shares Owned", min_value=0, value=2_000_000, step=100_000)
    own_pct, chance = calculate_takeover(tkr, shares)
    st.metric("Ownership", f"{own_pct:.2f}%")
    st.metric("Takeover Chance", f"{chance:.1f}%")
    if chance >= 60:
        st.success("**Hostile Takeover is highly viable** — RP opportunity!")

# ====================== SIDEBAR ======================
with st.sidebar:
    st.header("Game Controls")
    if st.button("💾 Save Game"):
        save_data(portfolios, current_date, price_history)
        st.success("Game saved successfully!")
    
    if st.button("Reset All Data"):
        if st.checkbox("Confirm full reset?"):
            st.session_state.clear()
            st.rerun()
    
    st.divider()
    st.caption("Star Wars: The Old Republic\nGalactic Stock Exchange Simulator")

# Auto-save when Streamlit reruns (best effort)
save_data(portfolios, current_date, price_history)
