import json

from rich.console import Console
from rich.table import Table


def render(console: Console, proposals: list[dict]) -> None:
    table = Table("ID", "Decision", "Confidence", "Amount", "Risk score", "Status")
    for proposal in proposals:
        payload = json.loads(proposal["payload"])
        table.add_row(str(proposal["id"]), proposal["decision"], str(payload["confidence"]), f"${payload['suggested_trade']['amount_usd']:,.2f}", str(proposal["risk_score"]), proposal["status"])
    console.print(table if proposals else "No proposals found.")
