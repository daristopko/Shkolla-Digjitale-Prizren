from rich.console import Console
from rich.table import Table

from app.schemas import WalletSnapshot
from app.utils.formatters import percent, usd


def render(console: Console, snapshot: WalletSnapshot) -> None:
    console.print(f"SOL balance: [bold]{snapshot.sol_balance:,.6f}[/bold]  Estimated wallet value: [bold]{usd(snapshot.total_value_usd)}[/bold]")
    table = Table("Mint", "Amount", "USD value", "Exposure")
    for token in snapshot.tokens:
        table.add_row(token["mint"], f"{token['amount']:,.6f}", usd(token.get("value_usd")), percent(token.get("exposure_percent")))
    console.print(table)
