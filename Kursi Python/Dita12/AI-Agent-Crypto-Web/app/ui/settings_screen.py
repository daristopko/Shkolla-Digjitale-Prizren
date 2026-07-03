from rich.console import Console
from rich.table import Table


def render(console: Console, settings: dict[str, object]) -> None:
    table = Table("Risk setting", "Value")
    for key, value in settings.items():
        table.add_row(key, str(value))
    console.print(table)
