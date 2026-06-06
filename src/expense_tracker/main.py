# src/expense_tracker/main.py
# Configures logging and starts the command-line expense tracker.
# Connects to: src/expense_tracker/config/settings.py, src/expense_tracker/cli/commands.py
# Created: 2026-06-06

import logging
import sys

from src.expense_tracker.cli.commands import run_cli
from src.expense_tracker.config.settings import get_data_file_path

LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"


def configure_logging() -> None:
    """Configure basic structured logging for the CLI application."""
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)


def main() -> int:
    """Start the expense tracker CLI and return a process exit code."""
    configure_logging()
    return run_cli(get_data_file_path())


if __name__ == "__main__":
    sys.exit(main())
