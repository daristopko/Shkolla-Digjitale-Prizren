from __future__ import annotations

from typing import Any

import requests
from requests import RequestException

from app.services.token_metadata_service import TokenMetadataService

DEXSCREENER_BATCH_SIZE = 30
DEXSCREENER_DISCOVERY_QUERIES = (
    "SOL", "USDC", "USDT", "JUP", "BONK", "RAY", "ORCA", "JTO", "PYTH", "WIF",
    "POPCAT", "MEW", "BOME", "MOBILE", "HNT", "WEN", "KMNO", "JLP", "MPLX", "ZEUS",
)


class MarketDataService:
    def __init__(self, metadata: TokenMetadataService, birdeye_api_key: str = "", timeout: int = 15):
        self.metadata = metadata
        self.birdeye_api_key = birdeye_api_key
        self.timeout = timeout

    def fetch(self, mint: str) -> dict[str, Any]:
        metadata = self.metadata.fetch(mint)
        pairs_response = requests.get(f"https://api.dexscreener.com/latest/dex/tokens/{mint}", timeout=self.timeout)
        pairs_response.raise_for_status()
        pairs = pairs_response.json().get("pairs") or []
        pair = max(pairs, key=lambda p: float((p.get("liquidity") or {}).get("usd") or 0), default={})
        pair_token = pair.get("baseToken") or {}
        metadata_symbol = metadata.get("symbol")
        metadata_name = metadata.get("name")
        return {
            "mint": mint,
            "symbol": pair_token.get("symbol") if metadata_symbol in {None, "", "UNKNOWN"} else metadata_symbol,
            "name": pair_token.get("name") if metadata_name in {None, "", "Unknown token"} else metadata_name,
            "price_usd": float(pair["priceUsd"]) if pair.get("priceUsd") else None,
            "liquidity_usd": float((pair.get("liquidity") or {}).get("usd") or 0),
            "price_change_24h": float((pair.get("priceChange") or {}).get("h24") or 0),
            "route_available": bool(pair),
            "suspicious_metadata": metadata.get("suspicious", False),
            "missing_metadata": metadata.get("missing", False),
            "metadata_source": metadata.get("source", "unknown"),
            "metadata_warning": metadata.get("warning", ""),
            "dex_url": pair.get("url", ""),
        }

    @staticmethod
    def _normalize_solana_pairs(pairs: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
        pairs = [pair for pair in pairs if pair.get("chainId") == "solana"]
        best_by_token: dict[str, dict[str, Any]] = {}
        for pair in pairs:
            base = pair.get("baseToken") or {}
            mint = base.get("address", "")
            if not mint:
                continue
            liquidity = float((pair.get("liquidity") or {}).get("usd") or 0)
            current = best_by_token.get(mint)
            current_liquidity = float((current.get("liquidity") or {}).get("usd") or 0) if current else -1
            if liquidity > current_liquidity:
                best_by_token[mint] = pair

        ranked = sorted(
            best_by_token.values(),
            key=lambda pair: float((pair.get("volume") or {}).get("h24") or 0),
            reverse=True,
        )[:limit]
        return [
            {
                "symbol": (pair.get("baseToken") or {}).get("symbol", "UNKNOWN"),
                "name": (pair.get("baseToken") or {}).get("name", "Unknown token"),
                "mint": (pair.get("baseToken") or {}).get("address", ""),
                "quote_symbol": (pair.get("quoteToken") or {}).get("symbol", ""),
                "dex": pair.get("dexId", ""),
                "price_usd": float(pair["priceUsd"]) if pair.get("priceUsd") else None,
                "price_change_24h": float((pair.get("priceChange") or {}).get("h24") or 0),
                "volume_24h": float((pair.get("volume") or {}).get("h24") or 0),
                "liquidity_usd": float((pair.get("liquidity") or {}).get("usd") or 0),
                "url": pair.get("url", ""),
            }
            for pair in ranked
        ]

    @staticmethod
    def _chunk(items: list[str], size: int) -> list[list[str]]:
        return [items[index:index + size] for index in range(0, len(items), size)]

    def _get_json(self, url: str, **kwargs: Any) -> Any:
        response = requests.get(url, timeout=self.timeout, **kwargs)
        response.raise_for_status()
        return response.json()

    def _collect_solana_discovery_addresses(self, limit: int) -> list[str]:
        addresses: list[str] = []

        def add(items: Any) -> None:
            if isinstance(items, dict):
                items = [items]
            if not isinstance(items, list):
                return
            for item in items:
                if not isinstance(item, dict):
                    continue
                if item.get("chainId") == "solana" and item.get("tokenAddress"):
                    addresses.append(item["tokenAddress"])

        for endpoint in (
            "https://api.dexscreener.com/token-profiles/latest/v1",
            "https://api.dexscreener.com/community-takeovers/latest/v1",
            "https://api.dexscreener.com/ads/latest/v1",
            "https://api.dexscreener.com/token-boosts/latest/v1",
            "https://api.dexscreener.com/token-boosts/top/v1",
        ):
            try:
                add(self._get_json(endpoint))
            except RequestException:
                continue

        return list(dict.fromkeys(addresses))[:limit]

    def search_solana_dex(self, query: str, limit: int = 100) -> list[dict[str, Any]]:
        query = query.strip()
        if not query:
            return []
        data = self._get_json(
            "https://api.dexscreener.com/latest/dex/search",
            params={"q": query},
        )
        return self._normalize_solana_pairs(data.get("pairs") or [], limit)

    def fetch_solana_dex_market(self, limit: int = 500) -> list[dict[str, Any]]:
        """Return a broad Solana DEX discovery list, never as an allowlist."""
        addresses = self._collect_solana_discovery_addresses(limit)
        pairs: list[dict[str, Any]] = []

        for batch in self._chunk(addresses, DEXSCREENER_BATCH_SIZE):
            try:
                data = self._get_json(f"https://api.dexscreener.com/tokens/v1/solana/{','.join(batch)}")
            except RequestException:
                continue
            if isinstance(data, list):
                pairs.extend(data)
            elif isinstance(data, dict):
                pairs.extend(data.get("pairs") or [])

        for query in DEXSCREENER_DISCOVERY_QUERIES:
            try:
                data = self._get_json(
                    "https://api.dexscreener.com/latest/dex/search",
                    params={"q": query},
                )
                pairs.extend(data.get("pairs") or [])
            except RequestException:
                continue
        return self._normalize_solana_pairs(pairs, limit)
