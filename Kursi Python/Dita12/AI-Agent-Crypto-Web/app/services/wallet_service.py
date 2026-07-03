from __future__ import annotations

from app.schemas import WalletSnapshot
from app.services.solana_service import SolanaService


class WalletService:
    def __init__(self, solana: SolanaService):
        self.solana = solana

    def snapshot(self, public_address: str, prices: dict[str, float] | None = None) -> WalletSnapshot:
        prices = prices or {}
        sol_balance = self.solana.get_sol_balance(public_address)
        tokens = self.solana.get_token_balances(public_address)
        total = sol_balance * prices.get("SOL", 0)
        for token in tokens:
            token["value_usd"] = token["amount"] * prices.get(token["mint"], 0)
            total += token["value_usd"]
        for token in tokens:
            token["exposure_percent"] = token["value_usd"] / total * 100 if total else 0
        return WalletSnapshot(public_address=public_address, sol_balance=sol_balance, total_value_usd=total, tokens=tokens)
