from rich.console import Console
from rich.panel import Panel


def render(console: Console, wallet_address: str, dry_run: bool) -> None:
    mode = "DRY RUN / PAPER TRADING" if dry_run else "REVIEW-ONLY (live signing unavailable)"
    wallet = wallet_address or "Not configured"
    console.print(Panel(f"Mode: [bold]{mode}[/bold]\nWallet: {wallet}\nNo seed phrase or private key is ever requested.", title="Dashboard", border_style="cyan"))
