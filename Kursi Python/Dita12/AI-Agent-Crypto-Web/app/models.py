from dataclasses import dataclass
from typing import Any


@dataclass
class RiskResult:
    allowed: bool
    score: int
    events: list[str]


@dataclass
class MarketData:
    mint: str
    price_usd: float | None = None
    liquidity_usd: float | None = None
    price_impact_percent: float | None = None
    route_available: bool = False
    suspicious_metadata: bool = False
    raw: dict[str, Any] | None = None
