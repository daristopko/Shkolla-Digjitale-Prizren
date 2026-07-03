import unittest
from unittest.mock import Mock, patch

import requests

from app.services.market_data_service import MarketDataService
from app.services.token_metadata_service import TokenMetadataService


class MetadataFallbackTest(unittest.TestCase):
    @patch("app.services.token_metadata_service.requests.get")
    def test_jupiter_dns_failure_returns_safe_fallback(self, get: Mock) -> None:
        get.side_effect = requests.ConnectionError("DNS unavailable")
        result = TokenMetadataService().fetch("mint")
        self.assertTrue(result["missing"])
        self.assertEqual(result["source"], "fallback")
        self.assertIn("temporarily unavailable", result["warning"])

    @patch("app.services.market_data_service.requests.get")
    def test_market_data_uses_dex_pair_name_when_metadata_is_down(self, get: Mock) -> None:
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {"pairs": [{
            "baseToken": {"symbol": "TEST", "name": "Test Token"},
            "priceUsd": "1.25", "liquidity": {"usd": 50000},
            "priceChange": {"h24": 2}, "url": "https://example.test",
        }]}
        get.return_value = response
        metadata = Mock()
        metadata.fetch.return_value = {"symbol": "UNKNOWN", "name": "Unknown token", "missing": True, "suspicious": False, "source": "fallback", "warning": "Metadata unavailable"}
        result = MarketDataService(metadata).fetch("mint")
        self.assertEqual(result["symbol"], "TEST")
        self.assertEqual(result["name"], "Test Token")
        self.assertEqual(result["metadata_warning"], "Metadata unavailable")

    @patch("app.services.market_data_service.requests.get")
    def test_dex_market_collects_multiple_discovery_sources(self, get: Mock) -> None:
        def response(payload: object) -> Mock:
            item = Mock()
            item.raise_for_status.return_value = None
            item.json.return_value = payload
            return item

        get.side_effect = [
            response([{"chainId": "solana", "tokenAddress": "mint-a"}]),
            requests.ConnectionError("temporary profiles outage"),
            response([{"chainId": "solana", "tokenAddress": "mint-b"}]),
            response([{"chainId": "ethereum", "tokenAddress": "ignored"}]),
            response([{"chainId": "solana", "tokenAddress": "mint-a"}]),
            response([
                {
                    "chainId": "solana",
                    "dexId": "raydium",
                    "baseToken": {"address": "mint-a", "symbol": "AAA", "name": "Token A"},
                    "quoteToken": {"symbol": "SOL"},
                    "priceUsd": "1",
                    "priceChange": {"h24": 1},
                    "volume": {"h24": 200},
                    "liquidity": {"usd": 1000},
                    "url": "https://example.test/a",
                },
                {
                    "chainId": "solana",
                    "dexId": "orca",
                    "baseToken": {"address": "mint-b", "symbol": "BBB", "name": "Token B"},
                    "quoteToken": {"symbol": "USDC"},
                    "priceUsd": "2",
                    "priceChange": {"h24": -2},
                    "volume": {"h24": 300},
                    "liquidity": {"usd": 2000},
                    "url": "https://example.test/b",
                },
            ]),
            *[response({"pairs": []}) for _ in range(20)],
        ]

        result = MarketDataService(TokenMetadataService()).fetch_solana_dex_market()

        self.assertEqual([token["symbol"] for token in result], ["BBB", "AAA"])
        self.assertIn("/tokens/v1/solana/mint-a,mint-b", get.call_args_list[5].args[0])


if __name__ == "__main__":
    unittest.main()
