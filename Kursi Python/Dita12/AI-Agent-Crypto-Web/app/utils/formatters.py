def usd(value: float | None) -> str:
    return "N/A" if value is None else f"${value:,.2f}"


def percent(value: float | None) -> str:
    return "N/A" if value is None else f"{value:.2f}%"
