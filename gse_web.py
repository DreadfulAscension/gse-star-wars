import streamlit as st
import random
import json
from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os

st.set_page_config(page_title="Galactic Trade Network", layout="wide", page_icon="🌌", initial_sidebar_state="expanded")

# ====================== CSS ======================
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
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header"><h1>GALACTIC TRADE NETWORK</h1><div class="subtitle">THE OLD REPUBLIC ERA • SECURE TRADING TERMINAL</div></div>', unsafe_allow_html=True)
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

def load_from_file():
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

def save_to_file():
    try:
        data = {
            "stocks": {t: stocks[t]["price"] for t in stocks},
            "portfolios": st.session_state.portfolios,
            "current_date": st.session_state.current_date.isoformat(),
            "price_history": st.session_state.price_history,
            "portfolio_history": st.session_state.portfolio_history
        }
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)
        return True
    except:
        return False

# ====================== SESSION STATE ======================
if 'initialized' not in st.session_state:
    portfolios, current_date, price_history, portfolio_history = load_from_file()
    st.session_state.portfolios = portfolios
    st.session_state.current_date = current_date
    st.session_state.price_history = price_history
    st.session_state.portfolio_history = portfolio_history
    st.session_state.initialized = True

portfolios = st.session_state.portfolios
price_history = st.session_state.price_history
portfolio_history = st.session_state.portfolio_history

for ticker in stocks:
    if ticker not in price_history or not price_history[ticker]:
        price_history[ticker] = [{"date": st.session_state.current_date.strftime('%Y-%m-%d'), "price": stocks[ticker]["price"]}]

def ensure_portfolio_structure(player):
    if player not in portfolios:
        return False
    p = portfolios[player]
    if "holdings" not in p: p["holdings"] = {}
    if "transactions" not in p: p["transactions"] = []
    if "total_dividends" not in p: p["total_dividends"] = 0.0
    if "controlled_companies" not in p: p["controlled_companies"] = []
    if "cash" not in p: p["cash"] = 250000.0
    return True

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
        if player not in portfolio_history: portfolio_history[player] = []
        net_worth = p.get("cash", 0) + sum(sh * stocks.get(t, {}).get("price", 0) for t, sh in p.get("holdings", {}).items())
        portfolio_history[player].append({"date": st.session_state.current_date.strftime('%Y-%m-%d'), "net_worth": round(net_worth, 2)})
    
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

def generate_portfolio_report(player):
    if not ensure_portfolio_structure(player): return None
    p = portfolios[player]
    holdings = p.get("holdings", {})
    transactions = p.get("transactions", [])
    
    total_value = 0
    unrealized_pnl = 0
    report_rows = []
    
    for ticker, shares in holdings.items():
        if ticker not in stocks: continue
        curr_price = stocks[ticker]["price"]
        value = shares * curr_price
        buys = [tx for tx in transactions if tx.get("ticker") == ticker and tx.get("action") == "Buy"]
        avg_cost = curr_price
        if buys:
            total_bought = sum(tx["shares"] for tx in buys)
            total_spent = sum(tx["total"] for tx in buys)
            avg_cost = total_spent / total_bought if total_bought > 0 else curr_price
        cost_basis = shares * avg_cost
        pnl = value - cost_basis
        unrealized_pnl += pnl
        total_value += value
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
    
    realized_gains = sum(tx.get("realized_gain", 0) for tx in transactions if tx.get("action") == "Sell")
    
    return {
        "player": player,
        "cash": p.get("cash", 0),
        "net_worth": p.get("cash", 0) + total_value,
        "overall_pnl": realized_gains + unrealized_pnl,
        "realized_gains": realized_gains,
        "total_dividends": p.get("total_dividends", 0),
        "holdings": report_rows,
        "transactions": transactions
    }

def generate_monthly_report(player, target_month=None):
    if not ensure_portfolio_structure(player):
        return None
    p = portfolios[player]
    transactions = p.get("transactions", [])
    if not transactions:
        return None
    df_tx = pd.DataFrame(transactions)
    df_tx['date'] = pd.to_datetime(df_tx['date'])
    if target_month:
        df_tx = df_tx[df_tx['date'].dt.to_period('M') == target_month]
    if df_tx.empty:
        return None
    total_trades = len(df_tx)
    buys = df_tx[df_tx['action'] == 'Buy']
    sells = df_tx[df_tx['action'] == 'Sell']
    total_invested = buys['total'].sum() if not buys.empty else 0
    total_received = sells['total'].sum() if not sells.empty else 0
    current_value = sum(sh * stocks[t]["price"] for t, sh in p.get("holdings", {}).items() if t in stocks)
    net_worth = p.get("cash", 0) + current_value
    
    html = f"""
    <h1 style="color:#00ffff; text-align:center;">GALACTIC TRADE NETWORK - MONTHLY REPORT</h1>
    <h2 style="color:#aaccff;">Player: {player} | Period: {target_month if target_month else 'All Time'}</h2>
    <hr>
    <h3>Summary Statistics</h3>
    <p><strong>Net Worth:</strong> {net_worth:,.2f} GC</p>
    <p><strong>Total Trades:</strong> {total_trades} | Buys: {len(buys)} | Sells: {len(sells)}</p>
    <p><strong>Total Invested:</strong> {total_invested:,.2f} GC | Total Received: {total_received:,.2f} GC</p>
    <p><strong>Dividends Received:</strong> {p.get("total_dividends", 0):,.2f} GC</p>
    <h3>Current Holdings</h3>
    {pd.DataFrame(generate_portfolio_report(player)["holdings"]).to_html(index=False)}
    <h3>Transaction History</h3>
    {df_tx.to_html(index=False)}
    """
    return html

# ====================== TABS ======================
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📊 Market", "📈 Charts", "💼 Portfolio", "📋 Detailed Report", 
    "📈 Performance", "🚀 Simulate", "🏦 Corporate Takeover"
])

with tab1:
    st.subheader("Current Market Prices")
    market_data = [{"Ticker": t, "Company": info["name"], "Price (GC)": f"{info['price']:,.2f}", 
                    "Div Yield": f"{info['div_yield']*100:.1f}%", "Sector": info.get("sector", "")} 
                   for t, info in stocks.items()]
    st.dataframe(pd.DataFrame(market_data), use_container_width=True, hide_index=True)

with tab2:
    st.subheader("Stock Price Charts")
    ticker = st.selectbox("Select Company", list(stocks.keys()))
    weeks = st.slider("Show last N weeks", 5, 100, 40)
    history = price_history.get(ticker, [])
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
            portfolios[player] = {"cash": 250000.0, "holdings": {}, "transactions": [], "total_dividends": 0.0, "controlled_companies": []}
            save_to_file()
            st.rerun()
    
    if ensure_portfolio_structure(player):
        p = portfolios[player]
        st.write(f"**Cash Balance**: {p.get('cash', 0):,.2f} GC")
        
        holdings = p.get("holdings", {})
        if holdings:
            rows = []
            net = p.get("cash", 0)
            for t, shares in holdings.items():
                if t in stocks:
                    value = shares * stocks[t]["price"]
                    net += value
                    rows.append({"Ticker": t, "Company": stocks[t]["name"], "Shares": shares,
                                 "Price": f"{stocks[t]['price']:,.2f}", "Value": f"{value:,.2f}"})
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            st.write(f"**Net Worth**: {net:,.2f} GC")
        else:
            st.info("No holdings yet.")

        st.subheader("Execute Trade")
        c1, c2, c3 = st.columns(3)
        with c1: tr_ticker = st.selectbox("Select Stock", list(stocks.keys()), key="trade_ticker")
        with c2: action = st.radio("Action", ["Buy", "Sell"])
        with c3: qty = st.number_input("Quantity", min_value=1, value=100, step=10)
        
        current_price = stocks[tr_ticker]["price"]
        fee_rate = 0.013
        st.info(f"**Current Price**: {current_price:,.2f} GC")
        
        if st.button(action, type="primary"):
            if action == "Buy":
                cost = round(current_price * qty * (1 + fee_rate), 2)
                if p["cash"] >= cost:
                    p["cash"] -= cost
                    p["holdings"][tr_ticker] = p["holdings"].get(tr_ticker, 0) + qty
                    p["transactions"].append({"date": st.session_state.current_date.strftime('%Y-%m-%d'), "ticker": tr_ticker, "action": "Buy", "shares": qty, "price": current_price, "total": cost})
                    st.success(f"Bought {qty} {tr_ticker}")
                    save_to_file()
                else:
                    st.error("Insufficient funds!")
            else:
                if p["holdings"].get(tr_ticker, 0) >= qty:
                    revenue = round(current_price * qty * (1 - fee_rate), 2)
                    p["cash"] += revenue
                    p["holdings"][tr_ticker] -= qty
                    if p["holdings"][tr_ticker] <= 0:
                        del p["holdings"][tr_ticker]
                    p["transactions"].append({"date": st.session_state.current_date.strftime('%Y-%m-%d'), "ticker": tr_ticker, "action": "Sell", "shares": qty, "price": current_price, "total": revenue})
                    st.success(f"Sold {qty} {tr_ticker}")
                    save_to_file()
                else:
                    st.error("Not enough shares!")
            st.rerun()

with tab4:
    st.subheader("📋 Detailed Report")
    report_player = st.text_input("Character Name", "Jedi Knight Sera", key="report_player")
    if report_player in portfolios:
        report = generate_portfolio_report(report_player)
        if report:
            c1, c2, c3, c4 = st.columns(4)
            with c1: st.metric("Net Worth", f"{report['net_worth']:,.0f} GC")
            with c2: st.metric("Total P&L", f"{report['overall_pnl']:,.0f} GC")
            with c3: st.metric("Realized Gains", f"{report['realized_gains']:,.0f} GC")
            with c4: st.metric("Dividends", f"{report['total_dividends']:,.0f} GC")
            
            if report["holdings"]:
                col1, col2 = st.columns(2)
                with col1:
                    fig = px.pie(pd.DataFrame(report["holdings"]), names="Ticker", values="Market Value", title="Allocation")
                    st.plotly_chart(fig, use_container_width=True)
                with col2:
                    df_hold = pd.DataFrame(report["holdings"])
                    fig2 = px.bar(df_hold, x="Ticker", y="Unrealized P&L", title="Unrealized P&L")
                    st.plotly_chart(fig2, use_container_width=True)
            
            st.dataframe(pd.DataFrame(report["holdings"]), use_container_width=True, hide_index=True)
            st.subheader("Transactions")
            st.dataframe(pd.DataFrame(report["transactions"]), use_container_width=True, hide_index=True)
            
            # Monthly Export
            st.subheader("Monthly Report Export")
            available_months = ["All Time"] + sorted({pd.to_datetime(tx["date"]).strftime('%Y-%m') for tx in report["transactions"]})
            selected_month = st.selectbox("Select Period", available_months)
            if st.button("📤 Export Full Monthly Report", type="primary"):
                html_content = generate_monthly_report(report_player, None if selected_month == "All Time" else selected_month)
                if html_content:
                    st.download_button(
                        label="Download HTML Report",
                        data=html_content,
                        file_name=f"{report_player.replace(' ', '_')}_GTN_Report_{selected_month}.html",
                        mime="text/html"
                    )
                    st.success("Report downloaded!")

with tab5:
    st.subheader("📈 Portfolio Performance")
    if portfolio_history:
        player_sel = st.selectbox("Select Player", list(portfolio_history.keys()), key="perf")
        hist = portfolio_history.get(player_sel, [])
        if len(hist) > 1:
            df = pd.DataFrame(hist)
            df["date"] = pd.to_datetime(df["date"])
            fig = go.Figure(go.Scatter(x=df["date"], y=df["net_worth"], mode='lines+markers'))
            fig.update_layout(title=f"{player_sel}'s Net Worth Over Time", height=600)
            st.plotly_chart(fig, use_container_width=True)

with tab6:
    st.subheader("🚀 Advance Market")
    weeks = st.slider("Number of weeks", 1, 12, 1)
    if st.button("Simulate Weeks", type="primary"):
        for _ in range(weeks):
            simulate_week()
        save_to_file()
        st.success(f"Advanced {weeks} weeks!")
        st.rerun()

with tab7:
    st.subheader("🏦 Corporate Takeover")
    player = st.text_input("Character Name", "Jedi Knight Sera", key="takeover_player")
    if ensure_portfolio_structure(player):
        ticker = st.selectbox("Target Company", list(stocks.keys()), key="takeover_ticker")
        if st.button("🚀 Launch Takeover", type="primary"):
            # Call your attempt_takeover function here
            st.info("Takeover logic placeholder - add your function")
            save_to_file()

# ====================== SIDEBAR ======================
with st.sidebar:
    st.subheader("💾 Save System")
    if st.button("💾 Save Game"):
        if save_to_file():
            st.success("Game Saved!")
    if st.button("🗑️ New Game"):
        if st.checkbox("Confirm?"):
            if os.path.exists(DATA_FILE):
                os.remove(DATA_FILE)
            st.session_state.clear()
            st.success("New Game Started!")
            st.rerun()

save_to_file()
