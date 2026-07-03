from __future__ import annotations

import json
from typing import Any

from app.database import Database


class PaperTradingService:
    def __init__(self, database: Database, dry_run: bool):
        self.database = database
        self.dry_run = dry_run

    def execute_approved(self, proposal_id: int) -> dict[str, Any]:
        if not self.dry_run:
            raise RuntimeError("Live execution is not implemented. Export and manually sign through a trusted Phantom-compatible flow.")
        rows = self.database.query("SELECT * FROM trade_proposals WHERE id=?", (proposal_id,))
        if not rows or rows[0]["status"] != "APPROVED":
            raise ValueError("Only manually approved proposals can be simulated")
        proposal = rows[0]
        payload = json.loads(proposal["payload"])
        trade = payload["suggested_trade"]
        result = {"proposal_id": proposal_id, "decision": proposal["decision"], "amount_usd": trade["amount_usd"], "status": "EXECUTED_DRY_RUN"}
        self.database.execute("INSERT INTO dry_run_trades(proposal_id,payload,pnl_usd) VALUES(?,?,0)", (proposal_id, json.dumps(result)))
        self.database.execute("UPDATE trade_proposals SET status='EXECUTED_DRY_RUN', updated_at=CURRENT_TIMESTAMP WHERE id=?", (proposal_id,))
        return result

    def performance(self) -> dict[str, Any]:
        stats = self.database.query("SELECT COUNT(*) trades, COALESCE(SUM(pnl_usd),0) pnl, SUM(CASE WHEN pnl_usd>0 THEN 1 ELSE 0 END) wins, SUM(CASE WHEN pnl_usd<0 THEN 1 ELSE 0 END) losses FROM dry_run_trades")[0]
        stats["rejected"] = self.database.query("SELECT COUNT(*) n FROM rejected_trades")[0]["n"]
        stats["max_drawdown_usd"] = min(0, float(stats["pnl"] or 0))
        return stats
