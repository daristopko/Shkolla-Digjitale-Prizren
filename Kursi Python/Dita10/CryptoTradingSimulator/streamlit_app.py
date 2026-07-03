from __future__ import annotations

from datetime import datetime
from typing import Any

import streamlit as st

from crypto_trading_simulator import (
    COINS,
    SAVE_FILE,
    ai_market_signal,
    default_state,
    format_money,
    get_prices,
    load_state,
    portfolio_value,
    save_state,
)


st.set_page_config(
    page_title="Crypto Trading Simulator",
    page_icon="BTC",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(
    """
<style>
    .block-container { padding-top: 1.75rem; padding-bottom: 2rem; }
    [data-testid="stMetricValue"] { font-weight: 800; }
    [data-testid="stMetricLabel"] { color: #475569; }
    div[data-testid="stDataFrame"] { border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden; }
    .status-line {
        border-left: 4px solid #0f766e;
        background: #f8fafc;
        padding: .65rem .85rem;
        border-radius: 6px;
        color: #334155;
        margin-bottom: 1rem;
    }
</style>
""",
    unsafe_allow_html=True,
)


def ensure_price_history(state: dict[str, Any], prices: dict[str, float]) -> None:
    history = state.setdefault("price_history", {})
    for coin in COINS:
        coin_history = list(history.get(coin, []))[-30:]
        if not coin_history and coin in prices:
            coin_history.append(prices[coin])
        history[coin] = coin_history


def ensure_session_state() -> None:
    if "sim_state" not in st.session_state:
        st.session_state.sim_state = load_state()

    if "use_api" not in st.session_state:
        st.session_state.use_api = False

    if "prices" not in st.session_state:
        prices, source = get_prices(use_api=False)
        st.session_state.prices = prices
        st.session_state.price_source = source
        ensure_price_history(st.session_state.sim_state, prices)

    if "selected_coin" not in st.session_state:
        st.session_state.selected_coin = "bitcoin"

    if "status" not in st.session_state:
        st.session_state.status = "Simulator ready."


def refresh_market() -> None:
    prices, source = get_prices(st.session_state.use_api)
    st.session_state.prices = prices
    st.session_state.price_source = source

    history = st.session_state.sim_state.setdefault("price_history", {})
    for coin, price in prices.items():
        coin_history = list(history.get(coin, []))
        coin_history.append(price)
        history[coin] = coin_history[-30:]

    st.session_state.status = (
        f"Market updated from {source} at {datetime.now().strftime('%H:%M:%S')}."
    )


def reset_simulator() -> None:
    st.session_state.sim_state = default_state()
    prices, source = get_prices(st.session_state.use_api)
    st.session_state.prices = prices
    st.session_state.price_source = source
    ensure_price_history(st.session_state.sim_state, prices)
    st.session_state.status = "Simulator reset to the starting balance."


def add_trade(action: str, coin: str, amount: float, dollars: float) -> None:
    state = st.session_state.sim_state
    state["trades"].append(
        {
            "time": datetime.now().isoformat(timespec="seconds"),
            "action": action,
            "coin": coin,
            "amount": amount,
            "usd": dollars,
            "price": st.session_state.prices[coin],
        }
    )
    state["trades"] = state["trades"][-80:]


def buy_coin(dollars: float) -> None:
    if dollars <= 0:
        st.session_state.status = "Trade value must be greater than zero."
        return

    state = st.session_state.sim_state
    coin = st.session_state.selected_coin
    if dollars > state["cash"]:
        st.session_state.status = "Not enough cash for that buy."
        return

    price = st.session_state.prices[coin]
    amount = dollars / price
    state["cash"] -= dollars
    state["holdings"][coin] += amount
    add_trade("buy", coin, amount, dollars)
    st.session_state.status = (
        f"Bought {amount:.8f} {COINS[coin]['symbol']} for {format_money(dollars)}."
    )


def sell_coin(amount: float) -> None:
    if amount <= 0:
        st.session_state.status = "Trade amount must be greater than zero."
        return

    state = st.session_state.sim_state
    coin = st.session_state.selected_coin
    if amount > state["holdings"][coin]:
        st.session_state.status = f"Not enough {COINS[coin]['symbol']} to sell."
        return

    dollars = amount * st.session_state.prices[coin]
    state["holdings"][coin] -= amount
    state["cash"] += dollars
    add_trade("sell", coin, amount, dollars)
    st.session_state.status = (
        f"Sold {amount:.8f} {COINS[coin]['symbol']} for {format_money(dollars)}."
    )


def add_watchlist_coin() -> None:
    coin = st.session_state.selected_coin
    watchlist = st.session_state.sim_state["watchlist"]
    if coin not in watchlist:
        watchlist.append(coin)
        st.session_state.status = f"{COINS[coin]['symbol']} added to watchlist."
    else:
        st.session_state.status = f"{COINS[coin]['symbol']} is already in watchlist."


def remove_watchlist_coin() -> None:
    coin = st.session_state.selected_coin
    watchlist = st.session_state.sim_state["watchlist"]
    if coin in watchlist:
        watchlist.remove(coin)
        st.session_state.status = f"{COINS[coin]['symbol']} removed from watchlist."
    else:
        st.session_state.status = f"{COINS[coin]['symbol']} is not in watchlist."


def market_rows() -> list[dict[str, str]]:
    rows = []
    state = st.session_state.sim_state
    for coin, meta in COINS.items():
        history = state["price_history"].get(coin, [])
        last_move = 0.0
        if len(history) >= 2 and history[-2]:
            last_move = ((history[-1] - history[-2]) / history[-2]) * 100

        rows.append(
            {
                "Coin": f"{meta['symbol']} - {coin.title()}",
                "Price": format_money(st.session_state.prices[coin]),
                "Last move": f"{last_move:+.2f}%",
            }
        )
    return rows


def portfolio_rows() -> list[dict[str, str]]:
    rows = []
    state = st.session_state.sim_state
    prices = st.session_state.prices
    for coin, amount in state["holdings"].items():
        rows.append(
            {
                "Coin": COINS[coin]["symbol"],
                "Amount": f"{amount:.8f}",
                "Value": format_money(amount * prices[coin]),
            }
        )
    return rows


def watchlist_rows() -> list[dict[str, str]]:
    rows = []
    prices = st.session_state.prices
    for coin in st.session_state.sim_state["watchlist"]:
        rows.append(
            {
                "Coin": COINS[coin]["symbol"],
                "Name": coin.title(),
                "Price": format_money(prices[coin]),
            }
        )
    return rows


def history_rows() -> list[dict[str, str]]:
    rows = []
    for trade in reversed(st.session_state.sim_state["trades"][-30:]):
        rows.append(
            {
                "Time": trade["time"],
                "Action": trade["action"].upper(),
                "Coin": COINS[trade["coin"]]["symbol"],
                "Amount": f"{trade['amount']:.8f}",
                "USD": format_money(trade["usd"]),
            }
        )
    return rows


def render_sidebar() -> None:
    with st.sidebar:
        st.header("Controls")
        st.toggle("Use CoinGecko API", key="use_api")

        action_cols = st.columns(2)
        if action_cols[0].button("Refresh", use_container_width=True):
            refresh_market()
        if action_cols[1].button("Save", use_container_width=True):
            save_state(st.session_state.sim_state)
            st.session_state.status = f"Portfolio saved to {SAVE_FILE.name}."

        st.divider()
        st.selectbox(
            "Coin",
            options=list(COINS),
            key="selected_coin",
            format_func=lambda coin: f"{COINS[coin]['symbol']} - {coin.title()}",
        )

        with st.form("trade_form"):
            trade_value = st.number_input(
                "USD / coin amount",
                min_value=0.0,
                value=100.0,
                step=10.0,
                format="%.8f",
            )
            trade_cols = st.columns(2)
            buy_clicked = trade_cols[0].form_submit_button("Buy USD", use_container_width=True)
            sell_clicked = trade_cols[1].form_submit_button("Sell Coin", use_container_width=True)

        if buy_clicked:
            buy_coin(trade_value)
        if sell_clicked:
            sell_coin(trade_value)

        watch_cols = st.columns(2)
        if watch_cols[0].button("Add Watch", use_container_width=True):
            add_watchlist_coin()
        if watch_cols[1].button("Remove", use_container_width=True):
            remove_watchlist_coin()

        st.divider()
        confirm_reset = st.checkbox("Confirm reset")
        if st.button("Reset Simulator", use_container_width=True, disabled=not confirm_reset):
            reset_simulator()


def render_metrics() -> None:
    state = st.session_state.sim_state
    prices = st.session_state.prices
    selected_coin = st.session_state.selected_coin
    selected_meta = COINS[selected_coin]

    cols = st.columns(4)
    cols[0].metric("Cash", format_money(state["cash"]))
    cols[1].metric("Total Value", format_money(portfolio_value(state, prices)))
    cols[2].metric(
        f"{selected_meta['symbol']} Price",
        format_money(prices[selected_coin]),
    )
    cols[3].metric("Source", st.session_state.price_source)


def render_ai_assistant() -> None:
    state = st.session_state.sim_state
    prices = st.session_state.prices
    coins = state["watchlist"] or list(COINS)[:2]

    for coin in coins:
        signal = ai_market_signal(coin, prices, state["price_history"])
        st.write(
            f"**{COINS[coin]['symbol']}**: {signal['trend']} | "
            f"{signal['action']} | risk={signal['risk']} | "
            f"move={signal['change_percent']:+.2f}%"
        )
        st.caption(signal["reason"])


def render_main() -> None:
    st.title("Crypto Trading Simulator")
    st.caption("Educational paper trading simulator. Not financial advice.")
    st.markdown(
        f'<div class="status-line">{st.session_state.status}</div>',
        unsafe_allow_html=True,
    )
    render_metrics()

    left, right = st.columns([1.55, 1])
    with left:
        st.subheader("Market")
        st.dataframe(market_rows(), use_container_width=True, hide_index=True)

        selected_coin = st.session_state.selected_coin
        selected_symbol = COINS[selected_coin]["symbol"]
        st.subheader(f"{selected_symbol} Price Chart")
        history = st.session_state.sim_state["price_history"].get(selected_coin, [])
        if len(history) >= 2:
            st.line_chart({"Price": history})
        else:
            st.info("Refresh the market a few times to build the chart.")

        st.subheader("Trade History")
        rows = history_rows()
        if rows:
            st.dataframe(rows, use_container_width=True, hide_index=True)
        else:
            st.info("No trades yet.")

    with right:
        st.subheader("Portfolio")
        st.dataframe(portfolio_rows(), use_container_width=True, hide_index=True)

        st.subheader("Watchlist")
        rows = watchlist_rows()
        if rows:
            st.dataframe(rows, use_container_width=True, hide_index=True)
        else:
            st.info("Watchlist is empty.")

        st.subheader("AI Market Assistant")
        render_ai_assistant()


def main() -> None:
    ensure_session_state()
    render_sidebar()
    render_main()


if __name__ == "__main__":
    main()
