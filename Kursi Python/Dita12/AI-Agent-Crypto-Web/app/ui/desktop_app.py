from __future__ import annotations

import json
import os
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, simpledialog, ttk
from typing import Callable

from dotenv import set_key

from app.config import ROOT, Settings
from app.database import Database
from app.logger import setup_logging
from app.schemas import AnalysisContext, WatchedToken
from app.services.ai_agent_service import AIAgentService
from app.services.market_data_service import MarketDataService
from app.services.openai_service import OpenAIService
from app.services.paper_trading_service import PaperTradingService
from app.services.risk_service import RiskService
from app.services.solana_service import SolanaService
from app.services.token_metadata_service import TokenMetadataService
from app.services.trade_proposal_service import TradeProposalService
from app.services.wallet_service import WalletService
from app.utils.constants import SOL_MINT
from app.utils.validators import validate_solana_address

BG = "#0B1120"
SIDEBAR = "#111827"
CARD = "#172033"
CARD_ALT = "#1F2A3D"
TEXT = "#F8FAFC"
MUTED = "#94A3B8"
PRIMARY = "#6366F1"
PRIMARY_HOVER = "#4F46E5"
GREEN = "#22C55E"
YELLOW = "#F59E0B"
RED = "#EF4444"
BORDER = "#2A3850"


class DesktopApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Python Phantom AI DEX Agent")
        self.root.geometry("1280x800")
        self.root.minsize(1040, 680)
        self.root.configure(bg=BG)

        self.settings = Settings()
        self.db = Database(self.settings.database_path)
        self.log = setup_logging(ROOT)
        self.wallet_service = WalletService(SolanaService(self.settings.solana_rpc_url))
        self.market_service = MarketDataService(TokenMetadataService(), self.settings.birdeye_api_key)
        self.risk = RiskService(self.db, self._risk_config())
        self.proposals = TradeProposalService(self.db, self.risk)
        self.paper = PaperTradingService(self.db, self.settings.dry_run)
        self.current_page = "dashboard"
        self.nav_buttons: dict[str, tk.Button] = {}
        self.dex_market_cache: list[dict] = []
        self.last_ai_result: dict = {}

        self._configure_styles()
        self._build_shell()
        self.show_page("dashboard")

    def run(self) -> None:
        self.root.mainloop()

    def _configure_styles(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("App.Treeview", background=CARD, fieldbackground=CARD, foreground=TEXT, rowheight=34, borderwidth=0, font=("Segoe UI", 10))
        style.configure("App.Treeview.Heading", background=CARD_ALT, foreground=TEXT, relief="flat", font=("Segoe UI Semibold", 10))
        style.map("App.Treeview", background=[("selected", PRIMARY)], foreground=[("selected", "white")])
        style.configure("App.TCombobox", fieldbackground=CARD_ALT, background=CARD_ALT, foreground=TEXT, arrowcolor=TEXT)
        style.configure("App.TNotebook", background=BG, borderwidth=0)
        style.configure("App.TNotebook.Tab", background=CARD_ALT, foreground=MUTED, padding=(18, 9), font=("Segoe UI Semibold", 10))
        style.map("App.TNotebook.Tab", background=[("selected", PRIMARY)], foreground=[("selected", "white")])

    def _build_shell(self) -> None:
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        sidebar = tk.Frame(self.root, bg=SIDEBAR, width=245)
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.grid_propagate(False)

        brand = tk.Frame(sidebar, bg=SIDEBAR)
        brand.pack(fill="x", padx=20, pady=(24, 26))
        tk.Label(brand, text="SOL", bg=PRIMARY, fg="white", font=("Segoe UI Semibold", 12), width=4, height=2).pack(side="left")
        text = tk.Frame(brand, bg=SIDEBAR)
        text.pack(side="left", padx=11)
        tk.Label(text, text="Phantom AI", bg=SIDEBAR, fg=TEXT, font=("Segoe UI Semibold", 15)).pack(anchor="w")
        tk.Label(text, text="DEX Assistant", bg=SIDEBAR, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w")

        pages = [
            ("dashboard", "Dashboard"), ("wallet", "Wallet Snapshot"),
            ("watchlist", "Watchlist"), ("analysis", "Token Analysis"),
            ("ai", "AI Agent"), ("proposals", "Trade Proposals"),
            ("portfolio", "Dry Run Portfolio"), ("history", "Trade History"),
            ("settings", "Settings"), ("logs", "Logs"),
        ]
        for key, label in pages:
            button = tk.Button(sidebar, text=label, anchor="w", command=lambda name=key: self.show_page(name), bg=SIDEBAR, fg=MUTED, activebackground=CARD_ALT, activeforeground=TEXT, relief="flat", borderwidth=0, font=("Segoe UI Semibold", 10), padx=22, pady=11, cursor="hand2")
            button.pack(fill="x", padx=10, pady=1)
            self.nav_buttons[key] = button

        mode_color = GREEN if self.settings.dry_run else YELLOW
        mode = "DRY RUN" if self.settings.dry_run else "REVIEW ONLY"
        tk.Label(sidebar, text=f"  {mode}  ", bg=mode_color, fg="#071018", font=("Segoe UI Semibold", 9), padx=6, pady=5).pack(side="bottom", pady=22)

        self.content = tk.Frame(self.root, bg=BG)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(1, weight=1)

        header = tk.Frame(self.content, bg=BG, height=88)
        header.grid(row=0, column=0, sticky="ew", padx=32, pady=(18, 0))
        self.page_title = tk.Label(header, text="", bg=BG, fg=TEXT, font=("Segoe UI Semibold", 24))
        self.page_title.pack(side="left", anchor="s")
        self.status = tk.Label(header, text="Ready", bg=BG, fg=MUTED, font=("Segoe UI", 10))
        self.status.pack(side="right", anchor="s", pady=7)

        self.page = tk.Frame(self.content, bg=BG)
        self.page.grid(row=1, column=0, sticky="nsew", padx=32, pady=(16, 28))

    def show_page(self, name: str) -> None:
        self.current_page = name
        for key, button in self.nav_buttons.items():
            button.configure(bg=CARD_ALT if key == name else SIDEBAR, fg=TEXT if key == name else MUTED)
        for child in self.page.winfo_children():
            child.destroy()
        builders = {
            "dashboard": self._dashboard_page, "wallet": self._wallet_page,
            "watchlist": self._watchlist_page, "analysis": self._analysis_page,
            "ai": self._ai_page, "proposals": self._proposals_page,
            "portfolio": self._portfolio_page, "history": self._history_page,
            "settings": self._settings_page, "logs": self._logs_page,
        }
        self.page_title.configure(text=dict((k, b.cget("text")) for k, b in self.nav_buttons.items())[name])
        builders[name]()

    def _card(self, parent: tk.Misc, title: str = "") -> tk.Frame:
        frame = tk.Frame(parent, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        if title:
            tk.Label(frame, text=title, bg=CARD, fg=TEXT, font=("Segoe UI Semibold", 13)).pack(anchor="w", padx=20, pady=(17, 8))
        return frame

    def _button(self, parent: tk.Misc, text: str, command: Callable[[], None], color: str = PRIMARY) -> tk.Button:
        return tk.Button(parent, text=text, command=command, bg=color, fg="white", activebackground=PRIMARY_HOVER, activeforeground="white", relief="flat", borderwidth=0, font=("Segoe UI Semibold", 10), padx=16, pady=9, cursor="hand2")

    def _tree(self, parent: tk.Misc, columns: list[tuple[str, str, int]]) -> ttk.Treeview:
        tree = ttk.Treeview(parent, columns=[c[0] for c in columns], show="headings", style="App.Treeview")
        for key, title, width in columns:
            tree.heading(key, text=title)
            tree.column(key, width=width, minwidth=70, anchor="w")
        tree.pack(fill="both", expand=True, padx=20, pady=(8, 20))
        return tree

    def _setting(self, key: str, default: str = "") -> str:
        rows = self.db.query("SELECT value FROM settings WHERE key=?", (key,))
        return rows[0]["value"] if rows else default

    def _set_setting(self, key: str, value: str) -> None:
        self.db.execute("INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, value))

    def _risk_config(self) -> dict[str, object]:
        config = self.settings.risk_dict()
        for row in self.db.query("SELECT key,value FROM settings WHERE key LIKE 'risk.%'"):
            name = row["key"].removeprefix("risk.")
            if name in config and isinstance(config[name], bool):
                config[name] = row["value"].lower() == "true"
            elif name in config and isinstance(config[name], int):
                config[name] = int(float(row["value"]))
            elif name in config:
                config[name] = float(row["value"])
        return config

    def _latest_wallet(self) -> dict:
        rows = self.db.query("SELECT payload FROM wallet_snapshots ORDER BY id DESC LIMIT 1")
        return json.loads(rows[0]["payload"]) if rows else {"public_address": self._setting("wallet_address"), "total_value_usd": 0, "sol_balance": 0, "tokens": []}

    def _run_task(self, label: str, task: Callable[[], object], done: Callable[[object], None], show_error: bool = True) -> None:
        self.status.configure(text=label, fg=YELLOW)

        def worker() -> None:
            try:
                result = task()
                self.root.after(0, lambda: (self.status.configure(text="Ready", fg=MUTED), done(result)))
            except Exception as error:
                self.log.exception("Desktop action failed")
                if show_error:
                    self.root.after(0, lambda err=str(error): (self.status.configure(text="Error", fg=RED), messagebox.showerror("Error", err)))
                else:
                    self.root.after(0, lambda: self.status.configure(text="DEX market unavailable", fg=RED))

        threading.Thread(target=worker, daemon=True).start()

    def _dashboard_page(self) -> None:
        wallet = self._latest_wallet()
        stats = self.paper.performance()
        actions = tk.Frame(self.page, bg=BG)
        actions.pack(fill="x", pady=(0, 12))
        tk.Label(actions, text="Wallet coins and watched tokens are loaded automatically.", bg=BG, fg=MUTED, font=("Segoe UI", 10)).pack(side="left")
        self._button(actions, "Refresh DEX", lambda: self._refresh_dex_market(True)).pack(side="right")
        self._button(actions, "Refresh Wallet", self._refresh_dashboard_coins, CARD_ALT).pack(side="right", padx=(0, 8))
        grid = tk.Frame(self.page, bg=BG)
        grid.pack(fill="x")
        values = [("Wallet value", f"${float(wallet.get('total_value_usd') or 0):,.2f}"), ("SOL balance", f"{float(wallet.get('sol_balance') or 0):,.4f}"), ("Paper trades", str(stats["trades"])), ("Paper PnL", f"${float(stats['pnl'] or 0):,.2f}")]
        self.dashboard_metrics: dict[str, tk.Label] = {}
        for index, (label, value) in enumerate(values):
            card = self._card(grid)
            card.grid(row=0, column=index, sticky="ew", padx=(0 if index == 0 else 7, 0 if index == 3 else 7))
            grid.grid_columnconfigure(index, weight=1)
            tk.Label(card, text=label, bg=CARD, fg=MUTED, font=("Segoe UI", 10)).pack(anchor="w", padx=18, pady=(18, 6))
            value_label = tk.Label(card, text=value, bg=CARD, fg=TEXT, font=("Segoe UI Semibold", 21))
            value_label.pack(anchor="w", padx=18, pady=(0, 18))
            self.dashboard_metrics[label] = value_label

        notebook = ttk.Notebook(self.page, style="App.TNotebook")
        notebook.pack(fill="both", expand=True, pady=(18, 0))
        coins = self._card(notebook)
        market = self._card(notebook)
        notebook.add(coins, text="My Coins")
        notebook.add(market, text="Solana DEX Market")
        self.dashboard_tree = self._tree(coins, [("symbol", "Coin", 90), ("name", "Name", 145), ("balance", "Balance", 120), ("value", "USD Value", 105), ("exposure", "Exposure", 90), ("risk", "Risk", 85), ("source", "Source", 95), ("mint", "Mint Address", 270)])
        market_controls = tk.Frame(market, bg=CARD)
        market_controls.pack(fill="x", padx=20, pady=(14, 4))
        self.dex_search_entry = tk.Entry(market_controls, bg=CARD_ALT, fg=TEXT, insertbackground=TEXT, relief="flat", font=("Segoe UI", 10))
        self.dex_search_entry.pack(side="left", fill="x", expand=True, ipady=8)
        self.dex_search_entry.insert(0, "Search symbol, name, pair, or mint")
        self.dex_search_entry.bind("<FocusIn>", lambda _event: self.dex_search_entry.delete(0, "end") if self.dex_search_entry.get().startswith("Search ") else None)
        self.dex_search_entry.bind("<Return>", lambda _event: self._search_dex_market())
        self._button(market_controls, "Search DEX", self._search_dex_market).pack(side="left", padx=(8, 0))
        self._button(market_controls, "Show Active", lambda: self._refresh_dex_market(True), CARD_ALT).pack(side="left", padx=(8, 0))
        self._button(market_controls, "Add Selected to Watchlist", self._add_selected_dex_to_watchlist, GREEN).pack(side="left", padx=(8, 0))
        self.dex_count_label = tk.Label(market, text="", bg=CARD, fg=MUTED, font=("Segoe UI", 9), padx=20)
        self.dex_count_label.pack(fill="x", anchor="w")
        warning = tk.Label(market, text="Market discovery only. Trending/promoted tokens are not verified, safe, or recommended.", bg=CARD, fg=YELLOW, font=("Segoe UI Semibold", 9), padx=20, pady=8)
        warning.pack(fill="x", anchor="w")
        self.dashboard_market_tree = self._tree(market, [("rank", "#", 40), ("pair", "Pair", 110), ("price", "Price USD", 105), ("change", "24h %", 80), ("volume", "Volume 24h", 115), ("liquidity", "Liquidity", 110), ("dex", "DEX", 90), ("mint", "Mint Address", 260)])
        self.dashboard_market_tree.bind("<Double-1>", lambda _event: self._add_selected_dex_to_watchlist())
        self._fill_dashboard_coins(wallet)
        self._fill_dex_market(self.dex_market_cache)
        if self._setting("wallet_address"):
            self.root.after(250, self._refresh_dashboard_coins)
        self.root.after(500, lambda: self._refresh_dex_market(False))

    def _fill_dashboard_coins(self, wallet: dict) -> None:
        if not hasattr(self, "dashboard_tree") or not self.dashboard_tree.winfo_exists():
            return
        self.dashboard_tree.delete(*self.dashboard_tree.get_children())
        watched = self.db.query("SELECT * FROM watched_tokens ORDER BY symbol")
        watched_by_mint = {row["mint_address"]: row for row in watched}
        holdings = {token["mint"]: token for token in wallet.get("tokens", [])}

        sol_balance = float(wallet.get("sol_balance") or 0)
        self.dashboard_tree.insert("", "end", values=("SOL", "Solana", f"{sol_balance:,.6f}", "N/A", "N/A", "LOW", "Wallet", SOL_MINT))

        for mint, token in holdings.items():
            metadata = watched_by_mint.get(mint, {})
            self.dashboard_tree.insert("", "end", values=(metadata.get("symbol", "UNKNOWN"), metadata.get("name", "Wallet token"), f"{float(token.get('amount') or 0):,.6f}", f"${float(token.get('value_usd') or 0):,.2f}" if token.get("value_usd") else "N/A", f"{float(token.get('exposure_percent') or 0):.2f}%" if token.get("exposure_percent") else "N/A", metadata.get("risk_level", "HIGH"), "Wallet", mint))

        for mint, token in watched_by_mint.items():
            if mint in holdings:
                continue
            self.dashboard_tree.insert("", "end", values=(token["symbol"], token["name"], "0", "N/A", "0.00%", token["risk_level"], "Watchlist", mint))

        if hasattr(self, "dashboard_metrics"):
            self.dashboard_metrics["Wallet value"].configure(text=f"${float(wallet.get('total_value_usd') or 0):,.2f}")
            self.dashboard_metrics["SOL balance"].configure(text=f"{sol_balance:,.4f}")

    def _refresh_dashboard_coins(self) -> None:
        address = self._setting("wallet_address")
        if not address:
            return

        def task() -> dict:
            snapshot = self.wallet_service.snapshot(validate_solana_address(address))
            data = snapshot.model_dump(mode="json")
            self.db.save_snapshot(data)
            return data

        def done(result: object) -> None:
            if self.current_page == "dashboard":
                self._fill_dashboard_coins(dict(result))  # type: ignore[arg-type]

        self._run_task("Refreshing wallet coins...", task, done)

    def _fill_dex_market(self, coins: list[dict]) -> None:
        if not hasattr(self, "dashboard_market_tree") or not self.dashboard_market_tree.winfo_exists():
            return
        self.dashboard_market_tree.delete(*self.dashboard_market_tree.get_children())
        if hasattr(self, "dex_count_label"):
            self.dex_count_label.configure(text=f"{len(coins)} Solana tokens loaded. Use search to find tokens outside this list.")
        for rank, coin in enumerate(coins, start=1):
            price = coin.get("price_usd")
            price_text = "N/A" if price is None else (f"${price:,.8f}" if price < 1 else f"${price:,.4f}")
            change = float(coin.get("price_change_24h") or 0)
            self.dashboard_market_tree.insert("", "end", values=(rank, f"{coin['symbol']}/{coin['quote_symbol']}", price_text, f"{change:+.2f}%", f"${float(coin.get('volume_24h') or 0):,.0f}", f"${float(coin.get('liquidity_usd') or 0):,.0f}", coin.get("dex", ""), coin["mint"]))

    def _refresh_dex_market(self, show_error: bool = False) -> None:
        def done(result: object) -> None:
            self.dex_market_cache = list(result)  # type: ignore[arg-type]
            if self.current_page == "dashboard":
                self._fill_dex_market(self.dex_market_cache)

        self._run_task("Loading Solana DEX market...", self.market_service.fetch_solana_dex_market, done, show_error=show_error)

    def _search_dex_market(self) -> None:
        query = self.dex_search_entry.get().strip()
        if not query or query.startswith("Search "):
            messagebox.showwarning("DEX search", "Enter a symbol, token name, pair, or mint address.")
            return

        def done(result: object) -> None:
            self.dex_market_cache = list(result)  # type: ignore[arg-type]
            self._fill_dex_market(self.dex_market_cache)
            if not self.dex_market_cache:
                messagebox.showinfo("DEX search", "No Solana pairs were found for this search.")

        self._run_task("Searching Solana DEX...", lambda: self.market_service.search_solana_dex(query), done)

    def _add_selected_dex_to_watchlist(self) -> None:
        selected = self.dashboard_market_tree.selection()
        if not selected:
            messagebox.showwarning("DEX market", "Select a token from the DEX table first.")
            return
        values = self.dashboard_market_tree.item(selected[0], "values")
        mint = str(values[-1])
        coin = next((item for item in self.dex_market_cache if item.get("mint") == mint), None)
        if not coin:
            messagebox.showerror("DEX market", "The selected token data is no longer available. Refresh the list.")
            return
        existing = self.db.query("SELECT symbol FROM watched_tokens WHERE mint_address=?", (mint,))
        if existing:
            messagebox.showinfo("Watchlist", f"{existing[0]['symbol']} is already in the watchlist.")
            return
        if not messagebox.askyesno("Add to Watchlist", f"Add {coin['symbol']} ({coin['name']}) to the watchlist?\n\nTrading will remain disabled until you review the token.", default="yes"):
            return
        token = WatchedToken(
            mint_address=mint,
            symbol=coin.get("symbol") or "UNKNOWN",
            name=coin.get("name") or "Unknown token",
            category="dex-discovery",
            notes="Added from DexScreener discovery; verify mint and metadata.",
            allowed_for_trading=False,
        )
        data = token.model_dump(mode="json")
        keys = ["mint_address", "symbol", "name", "category", "notes", "allowed_for_trading", "blocked", "risk_level", "reason_for_blocking", "created_at", "updated_at"]
        self.db.execute("INSERT INTO watched_tokens VALUES(?,?,?,?,?,?,?,?,?,?,?)", tuple(data[key] for key in keys))
        messagebox.showinfo("Watchlist", f"{token.symbol} was added with HIGH risk and trading disabled.")

    def _wallet_page(self) -> None:
        bar = tk.Frame(self.page, bg=BG)
        bar.pack(fill="x", pady=(0, 12))
        self.wallet_entry = tk.Entry(bar, bg=CARD_ALT, fg=TEXT, insertbackground=TEXT, relief="flat", font=("Consolas", 11))
        self.wallet_entry.pack(side="left", fill="x", expand=True, ipady=10)
        self.wallet_entry.insert(0, self._setting("wallet_address"))
        self._button(bar, "Refresh Snapshot", self._refresh_wallet).pack(side="left", padx=(10, 0))
        card = self._card(self.page, "Token balances")
        card.pack(fill="both", expand=True)
        self.wallet_tree = self._tree(card, [("mint", "Mint", 330), ("amount", "Amount", 130), ("value", "USD Value", 120), ("exposure", "Exposure", 100)])
        self._fill_wallet(self._latest_wallet())

    def _fill_wallet(self, snapshot: dict) -> None:
        if not hasattr(self, "wallet_tree"):
            return
        self.wallet_tree.delete(*self.wallet_tree.get_children())
        for token in snapshot.get("tokens", []):
            self.wallet_tree.insert("", "end", values=(token["mint"], f"{token['amount']:,.6f}", f"${token.get('value_usd', 0):,.2f}", f"{token.get('exposure_percent', 0):.2f}%"))

    def _refresh_wallet(self) -> None:
        try:
            address = validate_solana_address(self.wallet_entry.get())
        except ValueError as error:
            messagebox.showerror("Invalid wallet", str(error))
            return
        self._set_setting("wallet_address", address)

        def task() -> dict:
            snapshot = self.wallet_service.snapshot(address)
            data = snapshot.model_dump(mode="json")
            self.db.save_snapshot(data)
            return data

        self._run_task("Reading Solana wallet...", task, lambda data: (self._fill_wallet(data), messagebox.showinfo("Wallet", "Snapshot saved.")))

    def _watchlist_page(self) -> None:
        bar = tk.Frame(self.page, bg=BG)
        bar.pack(fill="x", pady=(0, 12))
        self._button(bar, "Add Token", self._add_token).pack(side="left")
        self._button(bar, "Remove Selected", self._remove_token, RED).pack(side="left", padx=8)
        card = self._card(self.page, "Watched tokens")
        card.pack(fill="both", expand=True)
        self.watch_tree = self._tree(card, [("mint", "Mint", 285), ("symbol", "Symbol", 80), ("name", "Name", 150), ("risk", "Risk", 80), ("allowed", "Allowed", 75), ("blocked", "Blocked", 75), ("notes", "Notes", 170)])
        self._load_watchlist()

    def _load_watchlist(self) -> None:
        self.watch_tree.delete(*self.watch_tree.get_children())
        for row in self.db.query("SELECT * FROM watched_tokens ORDER BY symbol"):
            self.watch_tree.insert("", "end", iid=row["mint_address"], values=(row["mint_address"], row["symbol"], row["name"], row["risk_level"], "Yes" if row["allowed_for_trading"] else "No", "Yes" if row["blocked"] else "No", row["notes"]))

    def _add_token(self) -> None:
        dialog = tk.Toplevel(self.root)
        dialog.title("Add watched token")
        dialog.geometry("500x465")
        dialog.configure(bg=CARD)
        dialog.transient(self.root)
        dialog.grab_set()
        fields: dict[str, tk.Entry] = {}
        for label, key in [("Mint address", "mint"), ("Symbol", "symbol"), ("Name", "name"), ("Category", "category"), ("Notes", "notes")]:
            tk.Label(dialog, text=label, bg=CARD, fg=MUTED, font=("Segoe UI", 10)).pack(anchor="w", padx=24, pady=(12, 4))
            entry = tk.Entry(dialog, bg=CARD_ALT, fg=TEXT, insertbackground=TEXT, relief="flat", font=("Segoe UI", 10))
            entry.pack(fill="x", padx=24, ipady=7)
            fields[key] = entry
        fields["category"].insert(0, "uncategorized")
        allowed = tk.BooleanVar(value=True)
        blocked = tk.BooleanVar(value=False)
        tk.Checkbutton(dialog, text="Allowed for proposals", variable=allowed, bg=CARD, fg=TEXT, selectcolor=CARD_ALT, activebackground=CARD).pack(anchor="w", padx=20, pady=(12, 0))
        tk.Checkbutton(dialog, text="Blocked", variable=blocked, bg=CARD, fg=TEXT, selectcolor=CARD_ALT, activebackground=CARD).pack(anchor="w", padx=20)

        def save() -> None:
            try:
                mint = validate_solana_address(fields["mint"].get())
                token = WatchedToken(mint_address=mint, symbol=fields["symbol"].get().strip() or "UNKNOWN", name=fields["name"].get().strip() or "Unknown token", category=fields["category"].get().strip(), notes=fields["notes"].get().strip(), allowed_for_trading=allowed.get(), blocked=blocked.get())
                data = token.model_dump(mode="json")
                keys = ["mint_address", "symbol", "name", "category", "notes", "allowed_for_trading", "blocked", "risk_level", "reason_for_blocking", "created_at", "updated_at"]
                self.db.execute("INSERT OR REPLACE INTO watched_tokens VALUES(?,?,?,?,?,?,?,?,?,?,?)", tuple(data[key] for key in keys))
                dialog.destroy()
                self._load_watchlist()
            except ValueError as error:
                messagebox.showerror("Invalid token", str(error), parent=dialog)

        self._button(dialog, "Save Token", save).pack(pady=18)

    def _remove_token(self) -> None:
        selected = self.watch_tree.selection()
        if selected and messagebox.askyesno("Remove token", "Remove the selected token from the watchlist?"):
            self.db.execute("DELETE FROM watched_tokens WHERE mint_address=?", (selected[0],))
            self._load_watchlist()

    def _token_selector(self, parent: tk.Misc) -> ttk.Combobox:
        tokens = self.db.query("SELECT mint_address,symbol FROM watched_tokens ORDER BY symbol")
        values = [f"{row['symbol']} | {row['mint_address']}" for row in tokens]
        combo = ttk.Combobox(parent, values=values, state="readonly", style="App.TCombobox", font=("Segoe UI", 10))
        if values:
            combo.current(0)
        return combo

    @staticmethod
    def _mint_from_combo(combo: ttk.Combobox) -> str:
        return combo.get().split(" | ", 1)[1] if " | " in combo.get() else ""

    def _analysis_page(self) -> None:
        bar = tk.Frame(self.page, bg=BG)
        bar.pack(fill="x", pady=(0, 12))
        self.analysis_token = self._token_selector(bar)
        self.analysis_token.pack(side="left", fill="x", expand=True, ipady=7)
        self._button(bar, "Fetch Market Data", self._fetch_market).pack(side="left", padx=(10, 0))
        card = self._card(self.page, "Market and metadata response")
        card.pack(fill="both", expand=True)
        self.market_text = tk.Text(card, bg=CARD, fg=TEXT, insertbackground=TEXT, relief="flat", font=("Consolas", 10), padx=20, pady=15, wrap="word")
        self.market_text.pack(fill="both", expand=True)

    def _fetch_market(self) -> None:
        mint = self._mint_from_combo(self.analysis_token)
        if not mint:
            messagebox.showwarning("Watchlist", "Add a token to the watchlist first.")
            return
        self._run_task("Fetching DEX data...", lambda: self.market_service.fetch(mint), lambda data: (self.market_text.delete("1.0", "end"), self.market_text.insert("1.0", json.dumps(data, indent=2))))

    def _ai_page(self) -> None:
        bar = tk.Frame(self.page, bg=BG)
        bar.pack(fill="x", pady=(0, 12))
        self.ai_token = self._token_selector(bar)
        self.ai_token.pack(side="left", fill="x", expand=True, ipady=7)
        self._button(bar, "Generate Decision", self._generate_ai).pack(side="left", padx=(10, 0))
        self.ai_raw_button = self._button(bar, "View Raw JSON", self._show_raw_ai, CARD_ALT)
        self.ai_raw_button.pack(side="left", padx=(8, 0))
        self.ai_raw_button.configure(state="normal" if self.last_ai_result else "disabled")

        summary = tk.Frame(self.page, bg=BG)
        summary.pack(fill="x", pady=(0, 12))
        self.ai_summary_labels: dict[str, tk.Label] = {}
        for index, title in enumerate(("Decision", "Confidence", "Risk", "Proposal")):
            card = self._card(summary)
            card.grid(row=0, column=index, sticky="ew", padx=(0 if index == 0 else 6, 0 if index == 3 else 6))
            summary.grid_columnconfigure(index, weight=1)
            tk.Label(card, text=title, bg=CARD, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", padx=16, pady=(13, 4))
            value = tk.Label(card, text="-", bg=CARD, fg=TEXT, font=("Segoe UI Semibold", 17))
            value.pack(anchor="w", padx=16, pady=(0, 13))
            self.ai_summary_labels[title] = value

        body = tk.PanedWindow(self.page, orient="horizontal", bg=BG, sashwidth=8, sashrelief="flat", borderwidth=0)
        body.pack(fill="both", expand=True)
        left = tk.Frame(body, bg=BG)
        right = tk.Frame(body, bg=BG)
        body.add(left, stretch="always", minsize=390)
        body.add(right, stretch="always", minsize=390)

        reasoning_card = self._card(left, "Reasoning summary")
        reasoning_card.pack(fill="both", expand=True, pady=(0, 10))
        self.ai_reasoning = tk.Text(reasoning_card, bg=CARD, fg=TEXT, relief="flat", font=("Segoe UI", 10), padx=18, pady=10, height=7, wrap="word")
        self.ai_reasoning.pack(fill="both", expand=True)
        self.ai_reasoning.configure(state="disabled")

        trade_card = self._card(left, "Suggested trade")
        trade_card.pack(fill="both", expand=True)
        self.ai_trade_tree = self._tree(trade_card, [("field", "Field", 175), ("value", "Value", 235)])

        details_card = self._card(right, "Risk plan and warnings")
        details_card.pack(fill="both", expand=True)
        self.ai_details_tree = self._tree(details_card, [("category", "Category", 145), ("detail", "Detail", 330)])

        self.ai_result_status = tk.Label(self.page, text="Select a token and generate a decision.", bg=BG, fg=MUTED, font=("Segoe UI Semibold", 10), anchor="w")
        self.ai_result_status.pack(fill="x", pady=(10, 0))
        if self.last_ai_result:
            self._render_ai_result(self.last_ai_result)

    def _generate_ai(self) -> None:
        if not self.settings.openai_api_key:
            messagebox.showwarning(
                "OpenAI setup required",
                "OPENAI_API_KEY is not configured. Open Settings, enter your API key, and save it locally before running AI analysis.",
            )
            return
        mint = self._mint_from_combo(self.ai_token)
        tokens = self.db.query("SELECT * FROM watched_tokens ORDER BY symbol")
        token = next((row for row in tokens if row["mint_address"] == mint), None)
        if not token:
            messagebox.showwarning("Watchlist", "Select a watched token first.")
            return

        def task() -> dict:
            market = self.market_service.fetch(mint)
            wallet = self._latest_wallet()
            context = AnalysisContext(wallet=wallet, watchlist=tokens, market_data=[market], risk_settings=self._risk_config(), trading_rules={"manual_approval_required": True, "never_all_in": True, "partial_profit_taking": True}, previous_trades=self.db.query("SELECT * FROM dry_run_trades ORDER BY id DESC LIMIT 20"), open_positions=self.db.query("SELECT * FROM paper_portfolio"))
            decision = AIAgentService(OpenAIService(self.settings.openai_api_key, self.settings.openai_model, self.settings.openai_base_url), self.db).analyze(context)
            proposal_id = self.proposals.create(decision, market, token, wallet)
            return {"decision": decision.model_dump(mode="json"), "proposal_id": proposal_id}

        def done(result: object) -> None:
            data = dict(result)  # type: ignore[arg-type]
            self.last_ai_result = data
            self._render_ai_result(data)

        self._run_task("AI is analyzing...", task, done)

    def _render_ai_result(self, result: dict) -> None:
        if not hasattr(self, "ai_summary_labels"):
            return
        decision = result.get("decision") or {}
        decision_name = str(decision.get("decision", "UNKNOWN"))
        decision_colors = {"BUY": GREEN, "DCA": GREEN, "SELL": YELLOW, "TAKE_PROFIT": YELLOW, "HOLD": PRIMARY, "AVOID": RED}
        risk_name = str(decision.get("risk_level", "UNKNOWN"))
        risk_colors = {"LOW": GREEN, "MEDIUM": YELLOW, "HIGH": RED, "EXTREME": RED}
        proposal_id = result.get("proposal_id")
        self.ai_summary_labels["Decision"].configure(text=decision_name, fg=decision_colors.get(decision_name, TEXT))
        self.ai_summary_labels["Confidence"].configure(text=f"{decision.get('confidence', 0)}%", fg=TEXT)
        self.ai_summary_labels["Risk"].configure(text=risk_name, fg=risk_colors.get(risk_name, TEXT))
        self.ai_summary_labels["Proposal"].configure(text=f"#{proposal_id}" if proposal_id else "Not created", fg=GREEN if proposal_id else MUTED)

        self.ai_reasoning.configure(state="normal")
        self.ai_reasoning.delete("1.0", "end")
        self.ai_reasoning.insert("1.0", decision.get("reasoning_summary") or "No reasoning was returned.")
        self.ai_reasoning.configure(state="disabled")

        self.ai_trade_tree.delete(*self.ai_trade_tree.get_children())
        trade = decision.get("suggested_trade") or {}
        trade_rows = [
            ("Input token", trade.get("input_token") or "N/A"),
            ("Output token", trade.get("output_token") or "N/A"),
            ("Input mint", trade.get("input_mint") or "N/A"),
            ("Output mint", trade.get("output_mint") or "N/A"),
            ("Amount USD", f"${float(trade.get('amount_usd') or 0):,.2f}"),
            ("Wallet allocation", f"{float(trade.get('amount_percentage_of_wallet') or 0):.2f}%"),
            ("Max slippage", f"{int(trade.get('max_slippage_bps') or 0)} bps"),
        ]
        for field, value in trade_rows:
            self.ai_trade_tree.insert("", "end", values=(field, value))

        self.ai_details_tree.delete(*self.ai_details_tree.get_children())

        def add_items(category: str, items: object) -> None:
            if not items:
                return
            values = items if isinstance(items, list) else [items]
            for item in values:
                text = json.dumps(item, ensure_ascii=True) if isinstance(item, (dict, list)) else str(item)
                self.ai_details_tree.insert("", "end", values=(category, text))

        add_items("Stop / invalidation", decision.get("stop_loss_zone"))
        add_items("Entry zone", decision.get("entry_zones"))
        add_items("DCA zone", decision.get("dca_zones"))
        add_items("Take profit", decision.get("take_profit_zones"))
        add_items("Invalid condition", decision.get("invalid_trade_conditions"))
        add_items("Warning", decision.get("warnings"))

        if proposal_id:
            status_text = f"Proposal #{proposal_id} was created and is waiting for manual approval."
            status_color = GREEN
        elif decision_name in {"HOLD", "AVOID"}:
            status_text = f"{decision_name} is a valid non-trading decision. No proposal is needed."
            status_color = YELLOW
        else:
            status_text = "No proposal was created because deterministic risk checks blocked the trade."
            status_color = RED
        self.ai_result_status.configure(text=status_text, fg=status_color)
        self.ai_raw_button.configure(state="normal")

    def _show_raw_ai(self) -> None:
        if not self.last_ai_result:
            return
        dialog = tk.Toplevel(self.root)
        dialog.title("Raw AI JSON")
        dialog.geometry("760x620")
        dialog.configure(bg=CARD)
        text = tk.Text(dialog, bg=CARD, fg=TEXT, insertbackground=TEXT, relief="flat", font=("Consolas", 10), padx=18, pady=15, wrap="word")
        text.pack(fill="both", expand=True)
        text.insert("1.0", json.dumps(self.last_ai_result, indent=2))
        text.configure(state="disabled")

    def _proposals_page(self) -> None:
        bar = tk.Frame(self.page, bg=BG)
        bar.pack(fill="x", pady=(0, 12))
        self._button(bar, "Approve", lambda: self._proposal_action("approve"), GREEN).pack(side="left")
        self._button(bar, "Reject", lambda: self._proposal_action("reject"), RED).pack(side="left", padx=8)
        self._button(bar, "Execute Paper Trade", lambda: self._proposal_action("execute"), PRIMARY).pack(side="left")
        card = self._card(self.page, "All trade proposals")
        card.pack(fill="both", expand=True)
        self.proposal_tree = self._tree(card, [("id", "ID", 50), ("decision", "Decision", 100), ("confidence", "Confidence", 90), ("amount", "Amount", 100), ("risk", "Risk Score", 90), ("status", "Status", 160), ("created", "Created", 145)])
        self._load_proposals()

    def _load_proposals(self) -> None:
        self.proposal_tree.delete(*self.proposal_tree.get_children())
        for row in self.db.query("SELECT * FROM trade_proposals ORDER BY id DESC"):
            payload = json.loads(row["payload"])
            self.proposal_tree.insert("", "end", iid=str(row["id"]), values=(row["id"], row["decision"], f"{payload['confidence']}%", f"${payload['suggested_trade']['amount_usd']:,.2f}", row["risk_score"], row["status"], row["created_at"]))

    def _proposal_action(self, action: str) -> None:
        selected = self.proposal_tree.selection()
        if not selected:
            messagebox.showwarning("Proposal", "Select a proposal first.")
            return
        proposal_id = int(selected[0])
        try:
            if action == "approve":
                if messagebox.askyesno("Manual approval", "Approve this proposal for paper execution?", default="no"):
                    self.proposals.set_status(proposal_id, True)
            elif action == "reject":
                if messagebox.askyesno("Reject proposal", "Reject this proposal?", default="yes"):
                    self.proposals.set_status(proposal_id, False, "Rejected from desktop interface")
            elif messagebox.askyesno("Paper trade", "Execute this approved proposal in DRY RUN mode?", default="no"):
                result = self.paper.execute_approved(proposal_id)
                messagebox.showinfo("Paper trade", json.dumps(result, indent=2))
            self._load_proposals()
        except (ValueError, RuntimeError) as error:
            messagebox.showerror("Proposal", str(error))

    def _portfolio_page(self) -> None:
        stats = self.paper.performance()
        card = self._card(self.page, "Paper trading performance")
        card.pack(fill="x")
        text = f"Trades: {stats['trades']}     Wins: {stats['wins'] or 0}     Losses: {stats['losses'] or 0}     Rejected: {stats['rejected']}     PnL: ${float(stats['pnl'] or 0):,.2f}     Max drawdown: ${float(stats['max_drawdown_usd'] or 0):,.2f}"
        tk.Label(card, text=text, bg=CARD, fg=TEXT, font=("Segoe UI Semibold", 12), padx=20, pady=24).pack(anchor="w")
        positions = self._card(self.page, "Paper positions")
        positions.pack(fill="both", expand=True, pady=(16, 0))
        tree = self._tree(positions, [("mint", "Mint", 320), ("symbol", "Symbol", 100), ("quantity", "Quantity", 120), ("cost", "Average Cost", 120), ("pnl", "Realized PnL", 120)])
        for row in self.db.query("SELECT * FROM paper_portfolio"):
            tree.insert("", "end", values=(row["mint_address"], row["symbol"], row["quantity"], f"${row['average_cost_usd']:,.4f}", f"${row['realized_pnl_usd']:,.2f}"))

    def _history_page(self) -> None:
        card = self._card(self.page, "Dry-run trade history")
        card.pack(fill="both", expand=True)
        tree = self._tree(card, [("id", "ID", 60), ("proposal", "Proposal", 90), ("pnl", "PnL", 100), ("details", "Details", 380), ("created", "Created", 160)])
        for row in self.db.query("SELECT * FROM dry_run_trades ORDER BY id DESC"):
            tree.insert("", "end", values=(row["id"], row["proposal_id"], f"${row['pnl_usd']:,.2f}", row["payload"], row["created_at"]))

    def _settings_page(self) -> None:
        openai_card = self._card(self.page, "AI provider configuration")
        openai_card.pack(fill="x", pady=(0, 14))
        openai_form = tk.Frame(openai_card, bg=CARD)
        openai_form.pack(fill="x", padx=20, pady=(4, 18))
        tk.Label(openai_form, text="API key", bg=CARD, fg=MUTED, font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w", padx=(0, 12))
        self.openai_key_entry = tk.Entry(openai_form, bg=CARD_ALT, fg=TEXT, insertbackground=TEXT, relief="flat", show="*", font=("Segoe UI", 10))
        self.openai_key_entry.grid(row=0, column=1, sticky="ew", ipady=7)
        if self.settings.openai_api_key:
            self.openai_key_entry.insert(0, self.settings.openai_api_key)
        tk.Label(openai_form, text="Model", bg=CARD, fg=MUTED, font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w", padx=(0, 12), pady=(10, 0))
        self.openai_model_entry = tk.Entry(openai_form, bg=CARD_ALT, fg=TEXT, insertbackground=TEXT, relief="flat", font=("Segoe UI", 10))
        self.openai_model_entry.grid(row=1, column=1, sticky="ew", ipady=7, pady=(10, 0))
        self.openai_model_entry.insert(0, self.settings.openai_model)
        tk.Label(openai_form, text="Base URL", bg=CARD, fg=MUTED, font=("Segoe UI", 10)).grid(row=2, column=0, sticky="w", padx=(0, 12), pady=(10, 0))
        self.openai_base_url_entry = tk.Entry(openai_form, bg=CARD_ALT, fg=TEXT, insertbackground=TEXT, relief="flat", font=("Segoe UI", 10))
        self.openai_base_url_entry.grid(row=2, column=1, sticky="ew", ipady=7, pady=(10, 0))
        self.openai_base_url_entry.insert(0, self.settings.openai_base_url)
        tk.Label(openai_form, text="Leave empty for OpenAI. Use https://integrate.api.nvidia.com/v1 for NVIDIA nvapi keys.", bg=CARD, fg=MUTED, font=("Segoe UI", 9)).grid(row=3, column=1, sticky="w", pady=(7, 0))
        self._button(openai_form, "Save AI Settings", self._save_openai_settings).grid(row=0, column=2, rowspan=3, padx=(12, 0))
        openai_form.grid_columnconfigure(1, weight=1)

        card = self._card(self.page, "Risk limits")
        card.pack(fill="both", expand=True)
        form = tk.Frame(card, bg=CARD)
        form.pack(fill="both", expand=True)
        self.risk_entries: dict[str, tk.Entry] = {}
        for row, (key, value) in enumerate(self._risk_config().items()):
            tk.Label(form, text=key.replace("_", " ").title(), bg=CARD, fg=MUTED, font=("Segoe UI", 10)).grid(row=row, column=0, sticky="w", padx=24, pady=8)
            entry = tk.Entry(form, bg=CARD_ALT, fg=TEXT, insertbackground=TEXT, relief="flat", font=("Segoe UI", 10), width=24)
            entry.grid(row=row, column=1, sticky="ew", padx=20, pady=8, ipady=6)
            entry.insert(0, str(value))
            if key in {"dry_run", "manual_approval_required"}:
                entry.configure(state="disabled", disabledbackground=CARD_ALT, disabledforeground=MUTED)
            self.risk_entries[key] = entry
        form.grid_columnconfigure(1, weight=1)
        self._button(form, "Save Risk Settings", self._save_risk).grid(row=len(self.risk_entries), column=1, sticky="e", padx=20, pady=20)

    def _save_openai_settings(self) -> None:
        api_key = self.openai_key_entry.get().strip()
        model = self.openai_model_entry.get().strip() or "gpt-4.1-mini"
        base_url = self.openai_base_url_entry.get().strip()
        if not api_key:
            messagebox.showwarning("OpenAI settings", "Enter a valid OpenAI API key. It will only be stored in the local .env file.")
            return
        if api_key.startswith("nvapi-") and not base_url:
            base_url = "https://integrate.api.nvidia.com/v1"
        env_path = ROOT / ".env"
        env_path.touch(exist_ok=True)
        set_key(str(env_path), "OPENAI_API_KEY", api_key, quote_mode="never")
        set_key(str(env_path), "OPENAI_MODEL", model, quote_mode="never")
        set_key(str(env_path), "OPENAI_BASE_URL", base_url, quote_mode="never")
        os.environ["OPENAI_API_KEY"] = api_key
        os.environ["OPENAI_MODEL"] = model
        os.environ["OPENAI_BASE_URL"] = base_url
        self.settings = Settings()
        if hasattr(self, "openai_base_url_entry"):
            self.openai_base_url_entry.delete(0, "end")
            self.openai_base_url_entry.insert(0, base_url)
        messagebox.showinfo("AI settings", "AI provider configuration was saved locally. AI Agent is ready to use.")

    def _save_risk(self) -> None:
        try:
            for key, entry in self.risk_entries.items():
                if key in {"dry_run", "manual_approval_required"}:
                    continue
                float(entry.get())
                self._set_setting(f"risk.{key}", entry.get())
            self.risk.settings = self._risk_config()
            messagebox.showinfo("Risk settings", "Risk limits saved.")
        except ValueError:
            messagebox.showerror("Risk settings", "All editable values must be numeric.")

    def _logs_page(self) -> None:
        card = self._card(self.page, "Recent application logs")
        card.pack(fill="both", expand=True)
        text = tk.Text(card, bg=CARD, fg=MUTED, relief="flat", font=("Consolas", 9), padx=20, pady=15, wrap="none")
        text.pack(fill="both", expand=True)
        path = Path(ROOT) / "data" / "app.log"
        lines = path.read_text(encoding="utf-8").splitlines()[-200:] if path.exists() else []
        text.insert("1.0", "\n".join(lines) or "No log entries yet.")
        text.configure(state="disabled")
