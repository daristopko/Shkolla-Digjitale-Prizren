from rich.console import Console
from rich.panel import Panel

from app.schemas import AIDecision


def render(console: Console, decision: AIDecision) -> None:
    trade = decision.suggested_trade
    body = f"Decision: [bold]{decision.decision.value}[/bold] ({decision.confidence}% confidence)\nRisk: {decision.risk_level.value}\nReason: {decision.reasoning_summary}\nAmount: ${trade.amount_usd:,.2f} ({trade.amount_percentage_of_wallet:.2f}% of wallet)\nStop/invalidation: {decision.stop_loss_zone}\nWarnings: {', '.join(decision.warnings) or 'None'}"
    console.print(Panel(body, title="AI Analysis", border_style="yellow"))
