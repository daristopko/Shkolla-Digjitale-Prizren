import argparse

from app.ui.desktop_app import DesktopApp
from app.ui.terminal_app import TerminalApp


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Python Phantom AI DEX Agent")
    parser.add_argument("--terminal", action="store_true", help="Use the Rich terminal interface")
    args = parser.parse_args()
    (TerminalApp() if args.terminal else DesktopApp()).run()