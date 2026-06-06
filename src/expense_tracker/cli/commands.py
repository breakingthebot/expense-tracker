# src/expense_tracker/cli/commands.py
# Provides non-interactive command parsing for adding and summarizing expenses.
# Connects to: src/expense_tracker/services/storage.py, src/expense_tracker/services/summary.py
# Created: 2026-06-06

from argparse import ArgumentParser, Namespace
from datetime import date
from pathlib import Path
import logging

from src.expense_tracker.cli.menu import run_menu
from src.expense_tracker.models.expense import Expense
from src.expense_tracker.services.storage import (
    ExpenseStorageError,
    load_expenses,
    save_expenses,
)
from src.expense_tracker.services.summary import MonthlySummary, build_monthly_summary
from src.expense_tracker.utils.validators import (
    VALID_CATEGORIES,
    parse_amount,
    parse_expense_date,
    validate_description,
    validate_month,
)

LOGGER = logging.getLogger(__name__)


def build_parser() -> ArgumentParser:
    """Create the argument parser for expense tracker commands."""
    parser = ArgumentParser(description="Track expenses by category in a JSON file.")
    subparsers = parser.add_subparsers(dest="command")

    add_parser = subparsers.add_parser("add", help="Add a new expense.")
    add_parser.add_argument("--amount", required=True, help="Expense amount, such as 12.50.")
    add_parser.add_argument("--category", required=True, choices=VALID_CATEGORIES)
    add_parser.add_argument("--description", required=True)
    add_parser.add_argument(
        "--date",
        default=date.today().isoformat(),
        help="Expense date in YYYY-MM-DD format. Defaults to today.",
    )

    summary_parser = subparsers.add_parser("summary", help="Show a monthly summary.")
    summary_parser.add_argument(
        "--month",
        default=date.today().strftime("%Y-%m"),
        help="Month to summarize in YYYY-MM format.",
    )

    subparsers.add_parser("interactive", help="Open the guided interactive menu.")
    return parser


def run_cli(data_file: Path, arguments: list[str] | None = None) -> int:
    """Run a command-line action and return a process exit code."""
    parser = build_parser()
    parsed_arguments = parser.parse_args(arguments)

    if parsed_arguments.command == "add":
        return _run_add_command(parsed_arguments, data_file)
    if parsed_arguments.command == "summary":
        return _run_summary_command(parsed_arguments, data_file)

    run_menu(data_file)
    return 0


def _run_add_command(arguments: Namespace, data_file: Path) -> int:
    """Add an expense from command arguments."""
    try:
        expense = Expense(
            amount=parse_amount(arguments.amount),
            category=arguments.category,
            description=validate_description(arguments.description),
            expense_date=parse_expense_date(arguments.date),
        )
        expenses = load_expenses(data_file)
        expenses.append(expense)
        save_expenses(expenses, data_file)
    except (ExpenseStorageError, ValueError) as exc:
        print(f"Error: {exc}")
        return 1

    LOGGER.info("Expense added from command.", extra={"category": expense.category})
    print(f"Added ${expense.amount} for {expense.category}.")
    return 0


def _run_summary_command(arguments: Namespace, data_file: Path) -> int:
    """Print a monthly summary from command arguments."""
    try:
        month = validate_month(arguments.month)
        expenses = load_expenses(data_file)
    except (ExpenseStorageError, ValueError) as exc:
        print(f"Error: {exc}")
        return 1

    _print_command_summary(build_monthly_summary(expenses, month))
    return 0


def _print_command_summary(summary: MonthlySummary) -> None:
    """Print a command-friendly monthly summary."""
    print(f"Summary for {summary.month}")
    if not summary.category_totals:
        print("No expenses recorded for this month.")
        return

    for category, amount in summary.category_totals.items():
        print(f"{category}: ${amount}")
    print(f"Total: ${summary.total}")
