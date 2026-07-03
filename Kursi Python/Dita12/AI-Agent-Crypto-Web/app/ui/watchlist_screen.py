from rich.console import Console
from rich.table import Table


def render(console: Console, tokens: list[dict]) -> None:
    table = Table("Mint", "Symbol", "Name", "Risk", "Allowed", "Blocked", "Notes")
    for token in tokens:
        table.add_row(token["mint_address"], token["symbol"], token["name"], token["risk_level"], "yes" if token["allowed_for_trading"] else "no", "yes" if token["blocked"] else "no", token["notes"] or "")
    console.print(table if tokens else "Watchlist is empty.")
