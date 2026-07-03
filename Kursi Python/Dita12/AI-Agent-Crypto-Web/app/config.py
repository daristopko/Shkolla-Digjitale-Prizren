from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


def _bool(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    openai_model: str = field(default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4.1-mini"))
    openai_base_url: str = field(default_factory=lambda: os.getenv("OPENAI_BASE_URL", ""))
    solana_rpc_url: str = field(default_factory=lambda: os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com"))
    jupiter_api_base_url: str = field(default_factory=lambda: os.getenv("JUPITER_API_BASE_URL", "https://quote-api.jup.ag/v6"))
    birdeye_api_key: str = field(default_factory=lambda: os.getenv("BIRDEYE_API_KEY", ""))
    dry_run: bool = field(default_factory=lambda: _bool("DRY_RUN", True))
    default_slippage_bps: int = field(default_factory=lambda: int(os.getenv("DEFAULT_SLIPPAGE_BPS", "100")))
    max_trade_percent_of_wallet: float = field(default_factory=lambda: float(os.getenv("MAX_TRADE_PERCENT_OF_WALLET", "10")))
    max_exposure_per_token_percent: float = field(default_factory=lambda: float(os.getenv("MAX_EXPOSURE_PER_TOKEN_PERCENT", "30")))
    max_daily_loss_percent: float = field(default_factory=lambda: float(os.getenv("MAX_DAILY_LOSS_PERCENT", "5")))
    max_trades_per_day: int = field(default_factory=lambda: int(os.getenv("MAX_TRADES_PER_DAY", "5")))
    max_price_impact_percent: float = field(default_factory=lambda: float(os.getenv("MAX_PRICE_IMPACT_PERCENT", "3")))
    minimum_liquidity_usd: float = field(default_factory=lambda: float(os.getenv("MINIMUM_LIQUIDITY_USD", "10000")))
    database_path: Path = field(default_factory=lambda: ROOT / "data" / "app.db")

    def risk_dict(self) -> dict[str, object]:
        return {
            "dry_run": self.dry_run,
            "manual_approval_required": True,
            "max_trade_percent_of_wallet": self.max_trade_percent_of_wallet,
            "max_exposure_per_token_percent": self.max_exposure_per_token_percent,
            "max_daily_loss_percent": self.max_daily_loss_percent,
            "max_trades_per_day": self.max_trades_per_day,
            "max_slippage_bps": min(self.default_slippage_bps, 150),
            "max_price_impact_percent": self.max_price_impact_percent,
            "minimum_liquidity_usd": self.minimum_liquidity_usd,
        }
