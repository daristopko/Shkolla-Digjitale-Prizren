import logging
from pathlib import Path


def setup_logging(root: Path) -> logging.Logger:
    log_dir = root / "data"
    log_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[logging.FileHandler(log_dir / "app.log", encoding="utf-8")],
    )
    return logging.getLogger("phantom_agent")
