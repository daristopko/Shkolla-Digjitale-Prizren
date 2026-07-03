from rich.console import Console
from rich.table import Table


def render(console: Console, trades: list[dict]) -> None:
    table = Table("ID", "Proposal", "PnL", "Created")
    for trade in trades:
        table.add_row(str(trade["id"]), str(trade["proposal_id"]), f"${trade['pnl_usd']:,.2f}", trade["created_at"])
    console.print(table if trades else "No dry-run trades yet.")
