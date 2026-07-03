from __future__ import annotations

from app.database import Database
from app.schemas import AIDecision, AnalysisContext
from app.services.openai_service import OpenAIService

SYSTEM_PROMPT = "You are a conservative crypto trading risk assistant. You do not promise profit. You never suggest all-in trades. You respect risk limits. You return structured JSON only. If data is insufficient, return HOLD or AVOID. You prioritize capital protection. Always include stop-loss or invalidation logic and partial profit-taking zones for actionable trades."


class AIAgentService:
    def __init__(self, openai: OpenAIService, database: Database):
        self.openai = openai
        self.database = database

    def analyze(self, context: AnalysisContext) -> AIDecision:
        payload = context.model_dump(mode="json")
        raw, decision = self.openai.structured(SYSTEM_PROMPT, payload, AIDecision)
        self.database.save_analysis(payload, raw, decision.model_dump(mode="json"))
        return decision
