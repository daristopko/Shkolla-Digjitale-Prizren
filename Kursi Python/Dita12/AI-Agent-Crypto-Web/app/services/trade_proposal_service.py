from __future__ import annotations

import json
from typing import Any

from app.database import Database
from app.schemas import AIDecision
from app.services.risk_service import RiskService


class TradeProposalService:
    def __init__(self, database: Database, risk: RiskService):
        self.database = database
        self.risk = risk

    def create(self, decision: AIDecision, market: dict[str, Any], token: dict[str, Any], wallet: dict[str, Any]) -> int | None:
        result = self.risk.evaluate(decision, market, token, wallet)
        payload = {**decision.model_dump(mode="json"), "market": market, "risk_events": result.events}
        if not result.allowed:
            for event in result.events:
                self.database.execute("INSERT INTO risk_events(severity,message) VALUES(?,?)", ("HIGH", event))
            return None
        return self.database.execute("INSERT INTO trade_proposals(decision,payload,risk_score,status) VALUES(?,?,?,'PENDING')", (decision.decision.value, json.dumps(payload), result.score))

    def set_status(self, proposal_id: int, approved: bool, reason: str = "") -> None:
        rows = self.database.query("SELECT status FROM trade_proposals WHERE id=?", (proposal_id,))
        if not rows or rows[0]["status"] != "PENDING":
            raise ValueError("Proposal does not exist or is no longer pending")
        status = "APPROVED" if approved else "REJECTED"
        self.database.execute("UPDATE trade_proposals SET status=?, updated_at=CURRENT_TIMESTAMP WHERE id=?", (status, proposal_id))
        if not approved:
            self.database.execute("INSERT INTO rejected_trades(proposal_id,reason) VALUES(?,?)", (proposal_id, reason or "Rejected manually"))

    def pending(self) -> list[dict[str, Any]]:
        return self.database.query("SELECT * FROM trade_proposals WHERE status='PENDING' ORDER BY id DESC")
