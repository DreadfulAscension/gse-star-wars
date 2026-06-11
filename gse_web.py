import streamlit as st
import random
import json
from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os

st.set_page_config(page_title="Galactic Trade Network", layout="wide", page_icon="🌌", initial_sidebar_state="expanded")

# ====================== GTN CSS ======================
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(rgba(8,12,28,0.92), rgba(2,4,18,0.95)), 
                    url('https://images.unsplash.com/photo-1464802686167-b939a7060ca4?ixlib=rb-4.0.3&q=85&fm=jpg&crop=entropy&cs=srgb') center/cover fixed;
        color: #00f5ff;
    }
    .main-header {
        background: linear-gradient(90deg, #001122, #003355, #001122);
        padding: 25px 30px;
        border: 2px solid #00ccff;
        border-radius: 8px;
        margin-bottom: 20px;
        text-align: center;
        box-shadow: 0 0 30px rgba(0, 204, 255, 0.5);
    }
    .main-header h1 { 
        color: #00ffff !important; 
        font-size: 3rem; 
        text-shadow: 0 0 20px #00ffff; 
        letter-spacing: 8px; 
    }
    .report-card { 
        background-color: #0a1428; 
        border: 1px solid #336699; 
        padding: 20px; 
        border-radius: 8px; 
        margin: 15px 0; 
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>GALACTIC TRADE NETWORK</h1>
    <div class="subtitle">THE OLD REPUBLIC ERA • SECURE TRADING TERMINAL</div>
</div>
""", unsafe_allow_html=True)

st.caption(f"**Current Cycle**: {datetime.now().strftime('%Y-%m-%d')} • Terminal Node: COR-77")

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

for ticker in stocks:
    if ticker not in price_history or not price_history[ticker]:
        price_history[ticker] = [{"date": st.session_state.current_date.strftime('%Y-%m-%d'), "price": stocks[ticker]["price"]}]

# ====================== SIMULATE WEEK ======================
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
    
    for player, p in portfolios.items():
        if player not in portfolio_history:
            portfolio_history[player] = []
        net_worth = p.get("cash", 0) + sum(sh * stocks[t]["price"] for t, sh in p.get("holdings", {}).items())
        portfolio_history[player].append({
            "date": st.session_state.current_date.strftime('%Y-%m-%d'),
            "net_worth": round(net_worth, 2)
        })
    
    if st.session_state.current_date.day % 28 < 7:
        for player, p in portfolios.items():
            total_div = 0
            for t, sh in p.get("holdings", {}).items():
                if t in stocks and sh > 0:
                    div = stocks[t]["price"] * stocks[t]["div_yield"] * sh / 4
                    p["cash"] += div
                    total_div += div
                    p["total_dividends"] = p.get("total_dividends", 0) + div
            if total_div > 0:
                st.success(f"💰 Dividends Paid to {player}: {total_div:,.2f} GC")

# ====================== PORTFOLIO REPORT ======================
def generate_portfolio_report(player):
    if player not in portfolios: return None
    p = portfolios[player]
    holdings = p.get("holdings", {})
    transactions = p.get("transactions", [])
    
    total_value = 0
    total_cost_basis = 0
    unrealized_pnl = 0
    report_rows = []
    
    for ticker, shares in holdings.items():
        if ticker not in stocks: continue
        curr_price = stocks[ticker]["price"]
        value = shares * curr_price
        
        buys = [tx for tx in transactions if tx["ticker"] == ticker and tx["action"] == "Buy"]
        if buys:
            total_bought = sum(tx["shares"] for tx in buys)
            total_spent = sum(tx["total"] for tx in buys)
            avg_cost = total_spent / total_bought if total_bought > 0 else curr_price
        else:
            avg_cost = curr_price
        cost_basis = shares * avg_cost
        
        pnl = value - cost_basis
        unrealized_pnl += pnl
        total_value += value
        total_cost_basis += cost_basis
        
        report_rows.append({
            "Ticker": ticker,
            "Company": stocks[ticker]["name"],
            "Shares": shares,
            "Avg Cost (GC)": round(avg_cost, 2),
            "Current Price": round(curr_price, 2),
            "Market Value": round(value, 2),
            "Unrealized P&L": round(pnl, 2),
            "P&L %": round((pnl / cost_basis * 100), 2) if cost_basis > 0 else 0
        })
    
    realized_gains = sum(tx.get("realized_gain", 0) for tx in transactions if tx["action"] == "Sell")
    
    return {
        "player": player,
        "cash": p.get("cash", 0),
        "total_value": total_value,
        "net_worth": p.get("cash", 0) + total_value,
        "total_cost_basis": total_cost_basis,
        "unrealized_pnl": unrealized_pnl,
        "realized_gains": realized_gains,
        "total_dividends": p.get("total_dividends", 0),
        "overall_pnl": realized_gains + unrealized_pnl,
        "holdings": report_rows,
        "transactions": transactions
    }

# ====================== TABS ======================
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📊 Market", "📈 Charts", "💼 Portfolio", 
    "📋 Detailed Report", "📈 Performance", "🚀 Simulate", "🏦 Takeover"
])

# Tab 1: Market
with tab1:
    st.subheader("Current Market Prices")
    df = pd.DataFrame([{
        "Ticker": t,
        "Company": info["name"],
        "Price (GC)": f"{info['price']:,.2f}",
        "Div Yield": f"{info['div_yield']*100:.1f}%"
    } for t, info in stocks.items()])
    st.dataframe(df, use_container_width=True, hide_index=True)

# Tab 2: Charts
with tab2:
    st.subheader("Stock Price Charts")
    ticker = st.selectbox("Select Company", list(stocks.keys()))
    weeks = st.slider("Show last N weeks", 5, 100, 40)
    history = price_history.get(ticker, [])
    if len(history) > 1:
        df_hist = pd.DataFrame(history[-weeks:])
        df_hist["date"] = pd.to_datetime(df_hist["date"])
        fig = go.Figure(go.Scatter(x=df_hist["date"], y=df_hist["price"], mode='lines+markers'))
        fig.update_layout(title=f"{ticker} - {stocks[ticker]['name']}", height=550)
        st.plotly_chart(fig, use_container_width=True)

# Tab 3: Portfolio
with tab3:
    st.subheader("💼 Your Portfolio")
    player = st.text_input("Character Name", "Jedi Knight Sera", key="player_name")
    
    if player not in portfolios:
        if st.button("Create Portfolio"):
            portfolios[player] = {"cash": 250000.0, "holdings": {}, "transactions": [], "total_dividends": 0.0}
            st.rerun()
    
    if player in portfolios:
        p = portfolios[player]
        st.write(f"**Cash Balance**: {p['cash']:,.2f} GC")
        
        holdings = p.get("holdings", {})
        if holdings:
            rows = []
            net = p["cash"]
            for t, shares in holdings.items():
                if t in stocks:
                    value = shares * stocks[t]["price"]
                    net += value
                    rows.append({
                        "Ticker": t,
                        "Company": stocks[t]["name"],
                        "Shares": shares,
                        "Price": f"{stocks[t]['price']:,.2f}",
                        "Value": f"{value:,.2f}"
                    })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            st.write(f"**Net Worth**: {net:,.2f} GC")
        else:
            st.info("You currently hold no shares.")

        # Trade
        st.subheader("Execute Trade")
        c1, c2, c3 = st.columns(3)
        with c1: tr_ticker = st.selectbox("Select Stock", list(stocks.keys()), key="trade_ticker")
        with c2: action = st.radio("Action", ["Buy", "Sell"])
        with c3: qty = st.number_input("Quantity", min_value=1, value=100)
        
        if st.button(action, type="primary"):
            price = stocks[tr_ticker]["price"]
            if action == "Buy":
                total_cost = round(price * qty * 1.015, 2)
                if p["cash"] >= total_cost:
                    p["cash"] -= total_cost
                    p["holdings"][tr_ticker] = p["holdings"].get(tr_ticker, 0) + qty
                    p["transactions"].append({
                        "date": st.session_state.current_date.strftime('%Y-%m-%d'),
                        "ticker": tr_ticker, "action": "Buy", "shares": qty,
                        "price": price, "total": total_cost
                    })
                    st.success(f"✅ Bought {qty} {tr_ticker}")
                else:
                    st.error("Insufficient funds!")
            else:
                if tr_ticker in p.get("holdings", {}) and p["holdings"][tr_ticker] >= qty:
                    revenue = round(price * qty * 0.985, 2)
                    p["cash"] += revenue
                    p["holdings"][tr_ticker] -= qty
                    if p["holdings"][tr_ticker] <= 0:
                        del p["holdings"][tr_ticker]
                    p["transactions"].append({
                        "date": st.session_state.current_date.strftime('%Y-%m-%d'),
                        "ticker": tr_ticker, "action": "Sell", "shares": qty,
                        "price": price, "total": revenue, "realized_gain": 0
                    })
                    st.success(f"✅ Sold {qty} {tr_ticker}")
                else:
                    st.error("Not enough shares!")
            st.rerun()

# Tab 4: Detailed Report
with tab4:
    st.subheader("📋 GTN Portfolio Intelligence Report")
    report_player = st.text_input("Character Name", "Jedi Knight Sera", key="report_player")
    
    if report_player in portfolios:
        report = generate_portfolio_report(report_player)
        if report:
            c1, c2, c3, c4 = st.columns(4)
            with c1: st.metric("Net Worth", f"{report['net_worth']:,.0f} GC")
            with c2: st.metric("Total P&L", f"{report['overall_pnl']:,.0f} GC", 
                              delta=f"{report['overall_pnl']/report['total_cost_basis']*100:+.1f}%" if report['total_cost_basis'] > 0 else None)
            with c3: st.metric("Realized Gains", f"{report['realized_gains']:,.0f} GC")
            with c4: st.metric("Dividends", f"{report['total_dividends']:,.0f} GC")
            
            col1, col2 = st.columns(2)
            with col1:
                if report["holdings"]:
                    fig = px.pie(pd.DataFrame(report["holdings"]), names="Ticker", values="Market Value", title="Portfolio Allocation")
                    st.plotly_chart(fig, use_container_width=True)
            with col2:
                if report["holdings"]:
                    df_hold = pd.DataFrame(report["holdings"])
                    fig2 = px.bar(df_hold, x="Ticker", y="Unrealized P&L", title="Unrealized P&L per Stock", color="Unrealized P&L")
                    st.plotly_chart(fig2, use_container_width=True)
            
            st.subheader("Current Holdings")
            st.dataframe(pd.DataFrame(report["holdings"]), use_container_width=True, hide_index=True)
            
            st.subheader("Transaction History")
            if report["transactions"]:
                st.dataframe(pd.DataFrame(report["transactions"]), use_container_width=True, hide_index=True)
            else:
                st.info("No transactions yet.")
    else:
        st.warning("Create a portfolio first.")

# Tab 5: Performance
with tab5:
    st.subheader("📈 Portfolio Performance")
    if portfolio_history:
        player_sel = st.selectbox("Select Player", list(portfolio_history.keys()), key="perf_player")
        hist = portfolio_history.get(player_sel, [])
        if len(hist) > 1:
            df = pd.DataFrame(hist)
            df["date"] = pd.to_datetime(df["date"])
            fig = go.Figure(go.Scatter(x=df["date"], y=df["net_worth"], mode='lines+markers'))
            fig.update_layout(title=f"{player_sel}'s Net Worth Over Time", height=600)
            st.plotly_chart(fig, use_container_width=True)

# Tab 6: Simulate
with tab6:
    st.subheader("Advance the Market")
    weeks = st.slider("Number of weeks", 1, 12, 1)
    if st.button("🚀 Simulate Weeks", type="primary"):
        for _ in range(weeks):
            simulate_week()
        st.success(f"Advanced {weeks} weeks!")
        st.rerun()

# Tab 7: Takeover
with tab7:
    st.info("🏦 Corporate Takeover & Hostile Acquisition module coming soon...")

# ====================== SIDEBAR ======================
with st.sidebar:
    if st.button("💾 Save Game"):
        save_data(portfolios, st.session_state.current_date, price_history, portfolio_history)
        st.success("Game Saved!")

save_data(portfolios, st.session_state.current_date, price_history, portfolio_history)
