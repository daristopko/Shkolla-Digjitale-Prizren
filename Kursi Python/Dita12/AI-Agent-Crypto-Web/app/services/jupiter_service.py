from __future__ import annotations

from typing import Any

import requests


class JupiterService:
    def __init__(self, base_url: str, timeout: int = 20):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def quote(self, input_mint: str, output_mint: str, amount_base_units: int, slippage_bps: int) -> dict[str, Any]:
        response = requests.get(f"{self.base_url}/quote", params={"inputMint": input_mint, "outputMint": output_mint, "amount": amount_base_units, "slippageBps": slippage_bps}, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def prepare_swap_export(self, quote: dict[str, Any], public_address: str) -> dict[str, Any]:
        """Return reviewable data only; this deliberately does not sign or submit."""
        return {
            "wallet": public_address,
            "quote": quote,
            "execution": "MANUAL_PHANTOM_SIGNING_REQUIRED",
            "warning": "No transaction was signed or submitted. Review and sign only in a trusted Phantom-compatible flow.",
        }
