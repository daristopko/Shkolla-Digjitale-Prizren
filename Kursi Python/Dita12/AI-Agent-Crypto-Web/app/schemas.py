from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, model_validator


class Decision(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    DCA = "DCA"
    TAKE_PROFIT = "TAKE_PROFIT"
    AVOID = "AVOID"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    EXTREME = "EXTREME"


class SuggestedTrade(BaseModel):
    input_token: str = ""
    output_token: str = ""
    input_mint: str = ""
    output_mint: str = ""
    amount_usd: float = Field(default=0, ge=0)
    amount_percentage_of_wallet: float = Field(default=0, ge=0, le=100)
    max_slippage_bps: int = Field(default=0, ge=0)


class AIDecision(BaseModel):
    decision: Decision
    confidence: int = Field(ge=0, le=100)
    reasoning_summary: str
    risk_level: RiskLevel
    suggested_trade: SuggestedTrade = Field(default_factory=SuggestedTrade)
    entry_zones: list[Any] = Field(default_factory=list)
    dca_zones: list[Any] = Field(default_factory=list)
    take_profit_zones: list[Any] = Field(default_factory=list)
    stop_loss_zone: str
    invalid_trade_conditions: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def require_invalidation(self) -> "AIDecision":
        if not self.stop_loss_zone and not self.invalid_trade_conditions:
            raise ValueError("stop-loss or invalidation logic is required")
        return self


class WatchedToken(BaseModel):
    mint_address: str
    symbol: str = "UNKNOWN"
    name: str = "Unknown token"
    category: str = "uncategorized"
    notes: str = ""
    allowed_for_trading: bool = True
    blocked: bool = False
    risk_level: RiskLevel = RiskLevel.HIGH
    reason_for_blocking: str = ""
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class WalletSnapshot(BaseModel):
    public_address: str
    total_value_usd: float = 0
    sol_balance: float = 0
    tokens: list[dict[str, Any]] = Field(default_factory=list)
    captured_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class AnalysisContext(BaseModel):
    wallet: dict[str, Any]
    watchlist: list[dict[str, Any]] = Field(default_factory=list)
    market_data: list[dict[str, Any]] = Field(default_factory=list)
    risk_settings: dict[str, Any]
    trading_rules: dict[str, Any] = Field(default_factory=dict)
    previous_trades: list[dict[str, Any]] = Field(default_factory=list)
    open_positions: list[dict[str, Any]] = Field(default_factory=list)
