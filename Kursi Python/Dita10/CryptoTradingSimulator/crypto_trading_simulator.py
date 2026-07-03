"""
Crypto Trading Simulator

Nje projekt i plote edukativ me interface:
- market prices
- buy/sell simulator
- portfolio tracker
- watchlist
- trade history
- AI market assistant
- ruajtje/load me JSON

Ky nuk eshte keshille financiare. Eshte simulator per te mesuar Python,
logjike programimi, GUI dhe menaxhim te te dhenave.
"""

import json
import random
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import messagebox, ttk
from urllib.error import URLError
from urllib.request import urlopen


APP_DIR = Path(__file__).resolve().parent
SAVE_FILE = APP_DIR / "portfolio.json"

COINS = {
    "bitcoin": {"symbol": "BTC", "base": 68000, "color": "#f59e0b"},
    "ethereum": {"symbol": "ETH", "base": 3600, "color": "#6366f1"},
    "solana": {"symbol": "SOL", "base": 170, "color": "#10b981"},
    "cardano": {"symbol": "ADA", "base": 0.65, "color": "#2563eb"},
}

COINGECKO_IDS = ",".join(COINS)
COINGECKO_URL = (
    "https://api.coingecko.com/api/v3/simple/price"
    f"?ids={COINGECKO_IDS}&vs_currencies=usd"
)


def default_state():
    return {
        "cash": 10000.0,
        "holdings": {coin: 0.0 for coin in COINS},
        "watchlist": ["bitcoin", "ethereum"],
        "trades": [],
        "price_history": {coin: [] for coin in COINS},
    }


def load_state():
    if not SAVE_FILE.exists():
        return default_state()

    try:
        with SAVE_FILE.open("r", encoding="utf-8") as file:
            state = json.load(file)
    except (json.JSONDecodeError, OSError):
        return default_state()

    fresh = default_state()
    fresh.update(state)
    fresh["holdings"] = {coin: float(fresh["holdings"].get(coin, 0.0)) for coin in COINS}
    fresh["price_history"] = {
        coin: list(fresh.get("price_history", {}).get(coin, []))[-30:] for coin in COINS
    }
    fresh["watchlist"] = [coin for coin in fresh.get("watchlist", []) if coin in COINS]
    fresh["trades"] = list(fresh.get("trades", []))[-80:]
    fresh["cash"] = float(fresh.get("cash", 10000.0))
    return fresh


def save_state(state):
    with SAVE_FILE.open("w", encoding="utf-8") as file:
        json.dump(state, file, indent=2)


def demo_prices():
    prices = {}
    for coin, meta in COINS.items():
        movement = random.uniform(0.92, 1.08)
        prices[coin] = round(meta["base"] * movement, 4)
    return prices


def get_prices(use_api=True):
    if not use_api:
        return demo_prices(), "Demo"

    try:
        with urlopen(COINGECKO_URL, timeout=8) as response:
            data = json.loads(response.read().decode("utf-8"))
        prices = {coin: float(data[coin]["usd"]) for coin in COINS}
        return prices, "CoinGecko API"
    except (KeyError, TypeError, ValueError, TimeoutError, URLError, OSError):
        return demo_prices(), "Demo"


def portfolio_value(state, prices):
    total = state["cash"]
    for coin, amount in state["holdings"].items():
        total += amount * prices[coin]
    return total


def format_money(value):
    return f"${value:,.2f}"


def ai_market_signal(coin, prices, history):
    price = prices[coin]
    previous = history[coin][-2] if len(history[coin]) >= 2 else price
    change_percent = ((price - previous) / previous) * 100 if previous else 0

    if change_percent > 2:
        trend = "bullish"
        action = "Hold or buy small"
        risk = "medium"
        reason = "cmimi po rritet shpejt, por duhet kujdes me FOMO"
    elif change_percent < -2:
        trend = "bearish"
        action = "Wait"
        risk = "high"
        reason = "ka renie te forte dhe tregu mund te jete i paqendrueshem"
    else:
        trend = "neutral"
        action = "Observe"
        risk = "low"
        reason = "levizja eshte e vogel dhe sinjali nuk eshte ende i qarte"

    return {
        "coin": coin,
        "trend": trend,
        "action": action,
        "risk": risk,
        "change_percent": change_percent,
        "reason": reason,
    }


class CryptoTradingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Crypto Trading Simulator")
        self.root.geometry("1080x700")
        self.root.minsize(960, 620)

        self.state = load_state()
        self.prices, self.price_source = get_prices(use_api=False)
        self.selected_coin = tk.StringVar(value="bitcoin")
        self.trade_amount = tk.StringVar(value="100")
        self.use_api = tk.BooleanVar(value=False)
        self.status = tk.StringVar(value="Simulator gati.")

        self.setup_styles()
        self.build_layout()
        self.refresh_market()

    def setup_styles(self):
        self.root.configure(bg="#eef2f7")
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("App.TFrame", background="#eef2f7")
        style.configure("Panel.TFrame", background="#ffffff")
        style.configure("Title.TLabel", background="#eef2f7", foreground="#111827", font=("Segoe UI", 22, "bold"))
        style.configure("Sub.TLabel", background="#eef2f7", foreground="#526070", font=("Segoe UI", 10))
        style.configure("PanelTitle.TLabel", background="#ffffff", foreground="#111827", font=("Segoe UI", 13, "bold"))
        style.configure("Body.TLabel", background="#ffffff", foreground="#334155", font=("Segoe UI", 10))
        style.configure("Value.TLabel", background="#ffffff", foreground="#111827", font=("Segoe UI", 16, "bold"))
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"), padding=8)
        style.configure("TButton", padding=7)
        style.configure("Treeview", rowheight=26, font=("Segoe UI", 9))
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))

    def build_layout(self):
        outer = ttk.Frame(self.root, padding=18, style="App.TFrame")
        outer.pack(fill="both", expand=True)
        outer.columnconfigure(0, weight=3)
        outer.columnconfigure(1, weight=2)
        outer.rowconfigure(1, weight=1)

        header = ttk.Frame(outer, style="App.TFrame")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 14))
        header.columnconfigure(0, weight=1)

        ttk.Label(header, text="Crypto Trading Simulator", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            header,
            text="Blej, shit, ndiq portofolin dhe lexo sinjale nga AI Market Assistant.",
            style="Sub.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(3, 0))

        actions = ttk.Frame(header, style="App.TFrame")
        actions.grid(row=0, column=1, rowspan=2, sticky="e")
        ttk.Checkbutton(actions, text="Use API", variable=self.use_api).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Refresh", command=self.refresh_market).pack(side="left", padx=4)
        ttk.Button(actions, text="Save", command=self.save).pack(side="left", padx=4)
        ttk.Button(actions, text="Reset", command=self.reset).pack(side="left", padx=4)

        left = ttk.Frame(outer, padding=16, style="Panel.TFrame")
        left.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        left.rowconfigure(2, weight=1)
        left.columnconfigure(0, weight=1)

        right = ttk.Frame(outer, padding=16, style="Panel.TFrame")
        right.grid(row=1, column=1, sticky="nsew", padx=(10, 0))
        right.rowconfigure(4, weight=1)
        right.columnconfigure(0, weight=1)

        self.build_market_panel(left)
        self.build_chart_panel(left)
        self.build_history_panel(left)
        self.build_portfolio_panel(right)
        self.build_trade_panel(right)
        self.build_ai_panel(right)
        self.build_watchlist_panel(right)

        status_label = ttk.Label(outer, textvariable=self.status, style="Sub.TLabel")
        status_label.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))

    def build_market_panel(self, parent):
        top = ttk.Frame(parent, style="Panel.TFrame")
        top.grid(row=0, column=0, sticky="ew")
        top.columnconfigure(0, weight=1)

        ttk.Label(top, text="Market Prices", style="PanelTitle.TLabel").grid(row=0, column=0, sticky="w")
        self.source_label = ttk.Label(top, text="", style="Body.TLabel")
        self.source_label.grid(row=0, column=1, sticky="e")

        self.market_tree = ttk.Treeview(top, columns=("symbol", "price", "change"), show="headings", height=4)
        self.market_tree.heading("symbol", text="Coin")
        self.market_tree.heading("price", text="Price")
        self.market_tree.heading("change", text="Last move")
        self.market_tree.column("symbol", width=120)
        self.market_tree.column("price", width=120, anchor="e")
        self.market_tree.column("change", width=120, anchor="e")
        self.market_tree.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        self.market_tree.bind("<<TreeviewSelect>>", self.select_coin_from_market)

    def build_chart_panel(self, parent):
        chart_frame = ttk.Frame(parent, style="Panel.TFrame")
        chart_frame.grid(row=1, column=0, sticky="ew", pady=(16, 0))
        chart_frame.columnconfigure(0, weight=1)

        ttk.Label(chart_frame, text="Price Chart", style="PanelTitle.TLabel").grid(row=0, column=0, sticky="w")
        self.chart_canvas = tk.Canvas(chart_frame, height=170, bg="#111827", highlightthickness=0)
        self.chart_canvas.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        self.chart_canvas.bind("<Configure>", lambda event: self.draw_chart())

    def build_history_panel(self, parent):
        history_frame = ttk.Frame(parent, style="Panel.TFrame")
        history_frame.grid(row=2, column=0, sticky="nsew", pady=(16, 0))
        history_frame.rowconfigure(1, weight=1)
        history_frame.columnconfigure(0, weight=1)

        ttk.Label(history_frame, text="Trade History", style="PanelTitle.TLabel").grid(row=0, column=0, sticky="w")

        self.history_tree = ttk.Treeview(
            history_frame,
            columns=("time", "action", "coin", "amount", "usd"),
            show="headings",
            height=8,
        )
        for column, title, width in (
            ("time", "Time", 145),
            ("action", "Action", 70),
            ("coin", "Coin", 80),
            ("amount", "Amount", 120),
            ("usd", "USD", 100),
        ):
            self.history_tree.heading(column, text=title)
            self.history_tree.column(column, width=width)
        self.history_tree.grid(row=1, column=0, sticky="nsew", pady=(10, 0))

    def build_portfolio_panel(self, parent):
        ttk.Label(parent, text="Portfolio", style="PanelTitle.TLabel").grid(row=0, column=0, sticky="w")

        summary = ttk.Frame(parent, style="Panel.TFrame")
        summary.grid(row=1, column=0, sticky="ew", pady=(10, 12))
        summary.columnconfigure(0, weight=1)
        summary.columnconfigure(1, weight=1)

        ttk.Label(summary, text="Cash", style="Body.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(summary, text="Total Value", style="Body.TLabel").grid(row=0, column=1, sticky="w")
        self.cash_label = ttk.Label(summary, text="$0.00", style="Value.TLabel")
        self.cash_label.grid(row=1, column=0, sticky="w")
        self.total_label = ttk.Label(summary, text="$0.00", style="Value.TLabel")
        self.total_label.grid(row=1, column=1, sticky="w")

        self.portfolio_tree = ttk.Treeview(
            parent,
            columns=("coin", "amount", "value"),
            show="headings",
            height=5,
        )
        self.portfolio_tree.heading("coin", text="Coin")
        self.portfolio_tree.heading("amount", text="Amount")
        self.portfolio_tree.heading("value", text="Value")
        self.portfolio_tree.column("coin", width=90)
        self.portfolio_tree.column("amount", width=120, anchor="e")
        self.portfolio_tree.column("value", width=120, anchor="e")
        self.portfolio_tree.grid(row=2, column=0, sticky="ew")

    def build_trade_panel(self, parent):
        trade = ttk.Frame(parent, style="Panel.TFrame")
        trade.grid(row=3, column=0, sticky="ew", pady=(16, 0))
        trade.columnconfigure(1, weight=1)

        ttk.Label(trade, text="Trade", style="PanelTitle.TLabel").grid(row=0, column=0, columnspan=2, sticky="w")
        ttk.Label(trade, text="Coin", style="Body.TLabel").grid(row=1, column=0, sticky="w", pady=(10, 4))
        ttk.Combobox(trade, textvariable=self.selected_coin, values=list(COINS), state="readonly").grid(
            row=1, column=1, sticky="ew", pady=(10, 4)
        )
        ttk.Label(trade, text="USD / Amount", style="Body.TLabel").grid(row=2, column=0, sticky="w", pady=4)
        ttk.Entry(trade, textvariable=self.trade_amount).grid(row=2, column=1, sticky="ew", pady=4)

        buttons = ttk.Frame(trade, style="Panel.TFrame")
        buttons.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        buttons.columnconfigure(0, weight=1)
        buttons.columnconfigure(1, weight=1)
        ttk.Button(buttons, text="Buy USD", command=self.buy, style="Accent.TButton").grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ttk.Button(buttons, text="Sell Coin", command=self.sell).grid(row=0, column=1, sticky="ew", padx=(5, 0))

    def build_ai_panel(self, parent):
        ai = ttk.Frame(parent, style="Panel.TFrame")
        ai.grid(row=4, column=0, sticky="nsew", pady=(16, 0))
        ai.rowconfigure(1, weight=1)
        ai.columnconfigure(0, weight=1)

        ttk.Label(ai, text="AI Market Assistant", style="PanelTitle.TLabel").grid(row=0, column=0, sticky="w")
        self.ai_text = tk.Text(
            ai,
            height=7,
            wrap="word",
            bg="#f8fafc",
            fg="#1f2937",
            relief="flat",
            padx=10,
            pady=10,
            font=("Segoe UI", 10),
        )
        self.ai_text.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        self.ai_text.configure(state="disabled")

    def build_watchlist_panel(self, parent):
        watch = ttk.Frame(parent, style="Panel.TFrame")
        watch.grid(row=5, column=0, sticky="ew", pady=(16, 0))
        watch.columnconfigure(0, weight=1)

        ttk.Label(watch, text="Watchlist", style="PanelTitle.TLabel").grid(row=0, column=0, sticky="w")
        watch_buttons = ttk.Frame(watch, style="Panel.TFrame")
        watch_buttons.grid(row=0, column=1, sticky="e")
        ttk.Button(watch_buttons, text="Add", command=self.add_watchlist).pack(side="left", padx=3)
        ttk.Button(watch_buttons, text="Remove", command=self.remove_watchlist).pack(side="left", padx=3)
        self.watchlist_text = ttk.Label(watch, text="", style="Body.TLabel", wraplength=360)
        self.watchlist_text.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))

    def refresh_market(self):
        self.prices, self.price_source = get_prices(self.use_api.get())
        for coin, price in self.prices.items():
            self.state["price_history"].setdefault(coin, []).append(price)
            self.state["price_history"][coin] = self.state["price_history"][coin][-30:]

        self.status.set(f"Market u perditesua nga {self.price_source} ne {datetime.now().strftime('%H:%M:%S')}.")
        self.update_all_views()

    def update_all_views(self):
        self.update_market()
        self.update_portfolio()
        self.update_history()
        self.update_watchlist()
        self.update_ai()
        self.draw_chart()

    def update_market(self):
        self.source_label.configure(text=f"Source: {self.price_source}")
        self.market_tree.delete(*self.market_tree.get_children())

        for coin, meta in COINS.items():
            history = self.state["price_history"][coin]
            last_move = 0
            if len(history) >= 2 and history[-2]:
                last_move = ((history[-1] - history[-2]) / history[-2]) * 100
            self.market_tree.insert(
                "",
                tk.END,
                iid=coin,
                values=(f"{meta['symbol']} - {coin.title()}", format_money(self.prices[coin]), f"{last_move:+.2f}%"),
            )

        self.market_tree.selection_set(self.selected_coin.get())

    def update_portfolio(self):
        self.cash_label.configure(text=format_money(self.state["cash"]))
        self.total_label.configure(text=format_money(portfolio_value(self.state, self.prices)))
        self.portfolio_tree.delete(*self.portfolio_tree.get_children())

        for coin, amount in self.state["holdings"].items():
            self.portfolio_tree.insert(
                "",
                tk.END,
                values=(
                    COINS[coin]["symbol"],
                    f"{amount:.8f}",
                    format_money(amount * self.prices[coin]),
                ),
            )

    def update_history(self):
        self.history_tree.delete(*self.history_tree.get_children())
        for trade in reversed(self.state["trades"][-30:]):
            self.history_tree.insert(
                "",
                tk.END,
                values=(
                    trade["time"],
                    trade["action"].upper(),
                    COINS[trade["coin"]]["symbol"],
                    f"{trade['amount']:.8f}",
                    format_money(trade["usd"]),
                ),
            )

    def update_watchlist(self):
        if not self.state["watchlist"]:
            self.watchlist_text.configure(text="Watchlist eshte bosh.")
            return

        items = []
        for coin in self.state["watchlist"]:
            items.append(f"{COINS[coin]['symbol']} {format_money(self.prices[coin])}")
        self.watchlist_text.configure(text="  |  ".join(items))

    def update_ai(self):
        lines = []
        for coin in self.state["watchlist"] or list(COINS)[:2]:
            signal = ai_market_signal(coin, self.prices, self.state["price_history"])
            lines.append(
                f"{COINS[coin]['symbol']}: {signal['trend']} | {signal['action']} | "
                f"risk={signal['risk']} | move={signal['change_percent']:+.2f}%\n"
                f"Arsyeja: {signal['reason']}"
            )

        self.ai_text.configure(state="normal")
        self.ai_text.delete("1.0", tk.END)
        self.ai_text.insert(tk.END, "\n\n".join(lines))
        self.ai_text.configure(state="disabled")

    def draw_chart(self):
        canvas = self.chart_canvas
        canvas.delete("all")
        width = max(canvas.winfo_width(), 320)
        height = max(canvas.winfo_height(), 150)
        coin = self.selected_coin.get()
        values = self.state["price_history"].get(coin, [])

        canvas.create_text(16, 16, anchor="w", fill="#e5e7eb", font=("Segoe UI", 10, "bold"), text=f"{coin.title()} price movement")

        if len(values) < 2:
            canvas.create_text(width / 2, height / 2, fill="#94a3b8", font=("Segoe UI", 10), text="Kliko Refresh disa here per te pare grafikun.")
            return

        min_price = min(values)
        max_price = max(values)
        price_range = max(max_price - min_price, 0.0001)
        left, right, top, bottom = 28, width - 20, 38, height - 24

        canvas.create_line(left, bottom, right, bottom, fill="#334155")
        canvas.create_line(left, top, left, bottom, fill="#334155")

        points = []
        for index, value in enumerate(values):
            x = left + (index / (len(values) - 1)) * (right - left)
            y = bottom - ((value - min_price) / price_range) * (bottom - top)
            points.extend([x, y])

        canvas.create_line(points, fill=COINS[coin]["color"], width=3, smooth=True)
        canvas.create_text(left, top, anchor="w", fill="#94a3b8", text=format_money(max_price), font=("Segoe UI", 8))
        canvas.create_text(left, bottom - 12, anchor="w", fill="#94a3b8", text=format_money(min_price), font=("Segoe UI", 8))

    def select_coin_from_market(self, _event):
        selection = self.market_tree.selection()
        if selection:
            self.selected_coin.set(selection[0])
            self.draw_chart()

    def get_trade_number(self):
        try:
            value = float(self.trade_amount.get())
        except ValueError:
            messagebox.showerror("Gabim", "Shkruaj nje numer te vlefshem.")
            return None

        if value <= 0:
            messagebox.showerror("Gabim", "Vlera duhet te jete me e madhe se zero.")
            return None
        return value

    def buy(self):
        dollars = self.get_trade_number()
        if dollars is None:
            return

        if dollars > self.state["cash"]:
            messagebox.showerror("Cash i pamjaftueshem", "Nuk ke cash te mjaftueshem per kete blerje.")
            return

        coin = self.selected_coin.get()
        amount = dollars / self.prices[coin]
        self.state["cash"] -= dollars
        self.state["holdings"][coin] += amount
        self.add_trade("buy", coin, amount, dollars)
        self.status.set(f"Bleve {amount:.8f} {COINS[coin]['symbol']} per {format_money(dollars)}.")
        self.update_all_views()

    def sell(self):
        amount = self.get_trade_number()
        if amount is None:
            return

        coin = self.selected_coin.get()
        if amount > self.state["holdings"][coin]:
            messagebox.showerror("Sasi e pamjaftueshme", "Nuk ke mjaftueshem coin per kete shitje.")
            return

        dollars = amount * self.prices[coin]
        self.state["holdings"][coin] -= amount
        self.state["cash"] += dollars
        self.add_trade("sell", coin, amount, dollars)
        self.status.set(f"Shite {amount:.8f} {COINS[coin]['symbol']} per {format_money(dollars)}.")
        self.update_all_views()

    def add_trade(self, action, coin, amount, dollars):
        self.state["trades"].append(
            {
                "time": datetime.now().isoformat(timespec="seconds"),
                "action": action,
                "coin": coin,
                "amount": amount,
                "usd": dollars,
                "price": self.prices[coin],
            }
        )
        self.state["trades"] = self.state["trades"][-80:]

    def add_watchlist(self):
        coin = self.selected_coin.get()
        if coin not in self.state["watchlist"]:
            self.state["watchlist"].append(coin)
            self.status.set(f"{COINS[coin]['symbol']} u shtua ne watchlist.")
        else:
            self.status.set(f"{COINS[coin]['symbol']} eshte tashme ne watchlist.")
        self.update_all_views()

    def remove_watchlist(self):
        coin = self.selected_coin.get()
        if coin in self.state["watchlist"]:
            self.state["watchlist"].remove(coin)
            self.status.set(f"{COINS[coin]['symbol']} u hoq nga watchlist.")
        else:
            self.status.set(f"{COINS[coin]['symbol']} nuk eshte ne watchlist.")
        self.update_all_views()

    def save(self):
        save_state(self.state)
        self.status.set(f"Portfolio u ruajt te {SAVE_FILE.name}.")

    def reset(self):
        if not messagebox.askyesno("Reset", "A deshiron ta kthesh simulatorin ne gjendjen fillestare?"):
            return
        self.state = default_state()
        self.prices, self.price_source = get_prices(use_api=False)
        self.refresh_market()
        self.status.set("Simulatori u resetua.")


def main():
    root = tk.Tk()
    app = CryptoTradingApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
