from __future__ import annotations

import json
from datetime import datetime, timezone

from rich.console import Console
from rich.prompt import Confirm, IntPrompt, Prompt

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
from app.ui import ai_analysis_screen, dashboard_screen, settings_screen, trade_history_screen, trade_proposals_screen, wallet_screen, watchlist_screen
from app.utils.validators import validate_solana_address


class TerminalApp:
    def __init__(self) -> None:
        self.console = Console()
        self.settings = Settings()
        self.db = Database(self.settings.database_path)
        self.log = setup_logging(ROOT)
        self.wallet = WalletService(SolanaService(self.settings.solana_rpc_url))
        self.market = MarketDataService(TokenMetadataService(), self.settings.birdeye_api_key)
        self.risk = RiskService(self.db, self._risk_config())
        self.proposals = TradeProposalService(self.db, self.risk)
        self.paper = PaperTradingService(self.db, self.settings.dry_run)

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

    def run(self) -> None:
        self.console.print("[bold cyan]Python Phantom AI DEX Agent[/bold cyan]\nConservative analysis and paper trading. No automatic live swaps.")
        actions = {"1": self.dashboard, "2": self.wallet_snapshot, "3": self.watchlist, "4": self.token_analysis, "5": self.ai_analysis, "6": self.trade_proposals, "7": self.portfolio, "8": self.history, "9": self.risk_settings, "10": self.logs}
        while True:
            self.console.print("\n[bold]1[/bold] Dashboard  [bold]2[/bold] Wallet  [bold]3[/bold] Watchlist  [bold]4[/bold] Token Analysis  [bold]5[/bold] AI Agent\n[bold]6[/bold] Proposals  [bold]7[/bold] Dry Run Portfolio  [bold]8[/bold] History  [bold]9[/bold] Risk Settings  [bold]10[/bold] Logs  [bold]0[/bold] Exit")
            choice = Prompt.ask("Select", choices=[str(i) for i in range(11)], default="1")
            if choice == "0":
                return
            try:
                actions[choice]()
            except (ValueError, RuntimeError) as error:
                self.log.warning("Action could not continue: %s", error)
                self.console.print(f"[yellow]{error}[/yellow]")
            except OSError as error:
                self.log.exception("Action failed")
                self.console.print(f"[red]{error}[/red]")

    def dashboard(self) -> None:
        dashboard_screen.render(self.console, self._setting("wallet_address"), self.settings.dry_run)

    def wallet_snapshot(self) -> None:
        current = self._setting("wallet_address")
        address = validate_solana_address(Prompt.ask("Public wallet address", default=current or None))
        self._set_setting("wallet_address", address)
        snapshot = self.wallet.snapshot(address)
        self.db.save_snapshot(snapshot.model_dump(mode="json"))
        wallet_screen.render(self.console, snapshot)

    def watchlist(self) -> None:
        tokens = self.db.query("SELECT * FROM watched_tokens ORDER BY symbol")
        watchlist_screen.render(self.console, tokens)
        action = Prompt.ask("Action", choices=["add", "remove", "back"], default="back")
        if action == "add":
            mint = validate_solana_address(Prompt.ask("Token mint"))
            metadata = self.market.metadata.fetch(mint)
            token = WatchedToken(mint_address=mint, symbol=Prompt.ask("Symbol", default=metadata.get("symbol", "UNKNOWN")), name=Prompt.ask("Name", default=metadata.get("name", "Unknown token")), category=Prompt.ask("Category", default="uncategorized"), notes=Prompt.ask("Notes", default=""), allowed_for_trading=Confirm.ask("Allowed for proposals?", default=True), blocked=Confirm.ask("Block token?", default=False))
            values = token.model_dump(mode="json")
            self.db.execute("INSERT OR REPLACE INTO watched_tokens VALUES(?,?,?,?,?,?,?,?,?,?,?)", tuple(values[k] for k in ["mint_address", "symbol", "name", "category", "notes", "allowed_for_trading", "blocked", "risk_level", "reason_for_blocking", "created_at", "updated_at"]))
        elif action == "remove":
            self.db.execute("DELETE FROM watched_tokens WHERE mint_address=?", (Prompt.ask("Mint to remove"),))

    def token_analysis(self) -> None:
        mint = Prompt.ask("Watched token mint")
        data = self.market.fetch(mint)
        self.console.print_json(data=data)

    def _latest_wallet(self) -> dict:
        rows = self.db.query("SELECT payload FROM wallet_snapshots ORDER BY id DESC LIMIT 1")
        return json.loads(rows[0]["payload"]) if rows else {"public_address": self._setting("wallet_address"), "total_value_usd": 0, "sol_balance": 0, "tokens": []}

    def ai_analysis(self) -> None:
        tokens = self.db.query("SELECT * FROM watched_tokens ORDER BY symbol")
        if not tokens:
            self.console.print("[yellow]Watchlist is empty. Open Watchlist and add a token mint before running AI analysis.[/yellow]")
            return
        watchlist_screen.render(self.console, tokens)
        mint = Prompt.ask("Mint to analyze")
        token = next((item for item in tokens if item["mint_address"] == mint), None)
        if not token:
            raise ValueError("Token is not in the watchlist")
        market = self.market.fetch(mint)
        context = AnalysisContext(wallet=self._latest_wallet(), watchlist=tokens, market_data=[market], risk_settings=self._risk_config(), trading_rules={"manual_approval_required": True, "never_all_in": True, "partial_profit_taking": True}, previous_trades=self.db.query("SELECT * FROM dry_run_trades ORDER BY id DESC LIMIT 20"), open_positions=self.db.query("SELECT * FROM paper_portfolio"))
        agent = AIAgentService(OpenAIService(self.settings.openai_api_key, self.settings.openai_model, self.settings.openai_base_url), self.db)
        decision = agent.analyze(context)
        ai_analysis_screen.render(self.console, decision)
        proposal_id = self.proposals.create(decision, market, token, context.wallet)
        self.console.print(f"Proposal #{proposal_id} created and awaits manual approval." if proposal_id else "[yellow]No proposal created; decision was non-actionable or failed risk checks.[/yellow]")

    def trade_proposals(self) -> None:
        rows = self.db.query("SELECT * FROM trade_proposals ORDER BY id DESC")
        trade_proposals_screen.render(self.console, rows)
        if not self.proposals.pending():
            return
        proposal_id = IntPrompt.ask("Pending proposal ID to review (0 to return)", default=0)
        if not proposal_id:
            return
        approved = Confirm.ask("Manually approve this proposal?", default=False)
        self.proposals.set_status(proposal_id, approved, "Rejected from terminal")
        if approved and Confirm.ask("Execute as a paper trade now?", default=True):
            self.console.print(self.paper.execute_approved(proposal_id))

    def portfolio(self) -> None:
        self.console.print_json(data=self.paper.performance())
        watchlist_screen.render(self.console, self.db.query("SELECT mint_address,symbol,symbol AS name,'paper' AS risk_level,1 AS allowed_for_trading,0 AS blocked,'' AS notes FROM paper_portfolio"))

    def history(self) -> None:
        trade_history_screen.render(self.console, self.db.query("SELECT * FROM dry_run_trades ORDER BY id DESC"))

    def risk_settings(self) -> None:
        config = self._risk_config()
        settings_screen.render(self.console, config)
        if not Confirm.ask("Edit a risk setting?", default=False):
            return
        editable = [key for key in config if key not in {"dry_run", "manual_approval_required"}]
        key = Prompt.ask("Setting", choices=editable)
        value = Prompt.ask("New numeric value", default=str(config[key]))
        float(value)
        self._set_setting(f"risk.{key}", value)
        self.risk.settings = self._risk_config()
        self.console.print("[green]Risk setting updated.[/green]")

    def logs(self) -> None:
        path = ROOT / "data" / "app.log"
        lines = path.read_text(encoding="utf-8").splitlines()[-30:] if path.exists() else []
        self.console.print("\n".join(lines) or "No log entries yet.")
