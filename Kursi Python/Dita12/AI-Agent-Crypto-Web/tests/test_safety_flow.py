import unittest
from pathlib import Path

from app.database import Database
from app.schemas import AIDecision
from app.services.paper_trading_service import PaperTradingService
from app.services.risk_service import RiskService
from app.services.trade_proposal_service import TradeProposalService


class SafetyFlowTest(unittest.TestCase):
    def setUp(self) -> None:
        data_dir = Path(__file__).resolve().parents[1] / "data"
        data_dir.mkdir(exist_ok=True)
        self.db_path = data_dir / "test_safety.db"
        self.db_path.unlink(missing_ok=True)
        self.db = Database(self.db_path)
        settings = {
            "max_trade_percent_of_wallet": 10,
            "max_exposure_per_token_percent": 30,
            "max_daily_loss_percent": 5,
            "max_trades_per_day": 5,
            "max_slippage_bps": 150,
            "max_price_impact_percent": 3,
            "minimum_liquidity_usd": 10000,
        }
        self.proposals = TradeProposalService(self.db, RiskService(self.db, settings))
        self.decision = AIDecision.model_validate({
            "decision": "BUY", "confidence": 70, "reasoning_summary": "Small test allocation", "risk_level": "MEDIUM",
            "suggested_trade": {"input_token": "USDC", "output_token": "TEST", "input_mint": "usdc", "output_mint": "test", "amount_usd": 50, "amount_percentage_of_wallet": 5, "max_slippage_bps": 100},
            "entry_zones": [], "dca_zones": [], "take_profit_zones": ["+10% partial"], "stop_loss_zone": "Exit below invalidation", "invalid_trade_conditions": ["Liquidity falls"], "warnings": [],
        })
        self.market = {"liquidity_usd": 50000, "price_impact_percent": 1, "suspicious_metadata": False, "missing_metadata": False}
        self.wallet = {"total_value_usd": 1000, "tokens": []}

    def test_manual_approval_and_blocklist(self) -> None:
        proposal_id = self.proposals.create(self.decision, self.market, {"allowed_for_trading": True, "blocked": False, "risk_level": "MEDIUM"}, self.wallet)
        self.assertIsNotNone(proposal_id)
        paper = PaperTradingService(self.db, dry_run=True)
        with self.assertRaises(ValueError):
            paper.execute_approved(proposal_id)
        self.proposals.set_status(proposal_id, approved=True)
        self.assertEqual(paper.execute_approved(proposal_id)["status"], "EXECUTED_DRY_RUN")
        blocked = self.proposals.create(self.decision, self.market, {"allowed_for_trading": True, "blocked": True, "risk_level": "HIGH"}, self.wallet)
        self.assertIsNone(blocked)


if __name__ == "__main__":
    unittest.main()
