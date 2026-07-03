from __future__ import annotations

from typing import Any

import requests


class SolanaService:
    def __init__(self, rpc_url: str, timeout: int = 20):
        self.rpc_url = rpc_url
        self.timeout = timeout

    def _rpc(self, method: str, params: list[Any]) -> Any:
        response = requests.post(self.rpc_url, json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params}, timeout=self.timeout)
        response.raise_for_status()
        body = response.json()
        if body.get("error"):
            raise RuntimeError(body["error"].get("message", "Solana RPC error"))
        return body["result"]

    def get_sol_balance(self, address: str) -> float:
        result = self._rpc("getBalance", [address, {"commitment": "confirmed"}])
        return result["value"] / 1_000_000_000

    def get_token_balances(self, address: str) -> list[dict[str, Any]]:
        result = self._rpc("getTokenAccountsByOwner", [address, {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"}, {"encoding": "jsonParsed"}])
        tokens: list[dict[str, Any]] = []
        for account in result.get("value", []):
            info = account["account"]["data"]["parsed"]["info"]
            amount = info["tokenAmount"]
            if float(amount.get("uiAmount") or 0) > 0:
                tokens.append({"mint": info["mint"], "amount": float(amount["uiAmount"]), "decimals": amount["decimals"]})
        return tokens
