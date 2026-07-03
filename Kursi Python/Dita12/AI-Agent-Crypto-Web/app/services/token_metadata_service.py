from __future__ import annotations

import re
from typing import Any

import requests


class TokenMetadataService:
    def __init__(self, timeout: int = 15):
        self.timeout = timeout

    def fetch(self, mint: str) -> dict[str, Any]:
        try:
            response = requests.get(
                "https://lite-api.jup.ag/tokens/v2/search",
                params={"query": mint},
                timeout=self.timeout,
            )
            response.raise_for_status()
            matches = response.json()
            data = next(
                (item for item in matches if item.get("id") == mint or item.get("address") == mint),
                None,
            )
        except (requests.RequestException, ValueError, TypeError):
            return {
                "address": mint,
                "symbol": "UNKNOWN",
                "name": "Unknown token",
                "missing": True,
                "suspicious": False,
                "source": "fallback",
                "warning": "Jupiter metadata is temporarily unavailable; using DEX pair metadata when possible.",
            }
        if not data:
            return {
                "address": mint,
                "symbol": "UNKNOWN",
                "name": "Unknown token",
                "missing": True,
                "suspicious": True,
                "source": "jupiter",
                "warning": "The token was not found in Jupiter token metadata.",
            }
        text = f"{data.get('symbol', '')} {data.get('name', '')}".lower()
        suspicious = bool(re.search(r"airdrop|claim|support|official.*v2|reward", text))
        return {**data, "address": data.get("id", mint), "missing": False, "suspicious": suspicious, "source": "jupiter", "warning": ""}

    @staticmethod
    def duplicate_symbols(items: list[dict[str, Any]]) -> set[str]:
        symbols = [str(item.get("symbol", "")).upper() for item in items if item.get("symbol")]
        return {symbol for symbol in symbols if symbols.count(symbol) > 1}
