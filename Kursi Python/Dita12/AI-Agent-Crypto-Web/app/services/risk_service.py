from __future__ import annotations

from typing import Any

from app.database import Database
from app.models import RiskResult
from app.schemas import AIDecision, Decision


class RiskService:
    def __init__(self, database: Database, settings: dict[str, Any]):
        self.database = database
        self.settings = settings

    def evaluate(self, decision: AIDecision, market: dict[str, Any], token: dict[str, Any], wallet: dict[str, Any]) -> RiskResult:
        trade = decision.suggested_trade
        events: list[str] = []
        if decision.decision in {Decision.HOLD, Decision.AVOID}:
            return RiskResult(False, 0, ["Decision does not require a trade proposal"])
        if token.get("blocked"):
            events.append("Token is blocklisted")
        if not token.get("allowed_for_trading", True):
            events.append("Token is not on the trading allowlist")
        if token.get("risk_level") == "EXTREME":
            events.append("Token risk is EXTREME")
        if market.get("suspicious_metadata") or market.get("missing_metadata"):
            events.append("Token metadata is missing or suspicious")
        liquidity = market.get("liquidity_usd")
        if liquidity is None or liquidity < self.settings["minimum_liquidity_usd"]:
            events.append("Liquidity is missing or below the configured minimum")
        impact = market.get("price_impact_percent")
        if impact is not None and impact > self.settings["max_price_impact_percent"]:
            events.append("Price impact exceeds the configured maximum")
        if trade.max_slippage_bps > self.settings["max_slippage_bps"]:
            events.append("Slippage exceeds the configured maximum")
        if trade.amount_percentage_of_wallet > self.settings["max_trade_percent_of_wallet"]:
            events.append("Trade size exceeds the configured wallet percentage")
        exposure = next((float(t.get("exposure_percent", 0)) for t in wallet.get("tokens", []) if t.get("mint") == trade.output_mint), 0)
        if exposure + trade.amount_percentage_of_wallet > self.settings["max_exposure_per_token_percent"]:
            events.append("Post-trade token exposure would exceed the configured maximum")
        trades_today = self.database.query("SELECT COUNT(*) AS n FROM dry_run_trades WHERE date(created_at)=date('now')")[0]["n"]
        if trades_today >= self.settings["max_trades_per_day"]:
            events.append("Maximum trades per day reached")
        pnl_today = self.database.query("SELECT COALESCE(SUM(pnl_usd),0) AS pnl FROM dry_run_trades WHERE date(created_at)=date('now')")[0]["pnl"]
        value = float(wallet.get("total_value_usd") or 0)
        if value and pnl_today < -(value * self.settings["max_daily_loss_percent"] / 100):
            events.append("Maximum daily loss reached")
        score = min(100, len(events) * 20 + (25 if decision.risk_level.value in {"HIGH", "EXTREME"} else 0))
        return RiskResult(not events, score, events)
