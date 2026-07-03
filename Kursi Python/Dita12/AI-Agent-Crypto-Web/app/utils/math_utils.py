def max_drawdown(values: list[float]) -> float:
    peak = values[0] if values else 0
    drawdown = 0.0
    for value in values:
        peak = max(peak, value)
        if peak:
            drawdown = min(drawdown, (value - peak) / peak * 100)
    return drawdown
