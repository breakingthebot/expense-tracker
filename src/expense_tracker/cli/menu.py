# src/expense_tracker/cli/menu.py
# Handles all terminal prompts and display output for the expense tracker.
# Connects to: src/expense_tracker/services/storage.py, src/expense_tracker/services/summary.py
# Created: 2026-06-06

from datetime import date
from decimal import Decimal
import logging
from pathlib import Path

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
    validate_category,
    validate_description,
    validate_month,
)

LOGGER = logging.getLogger(__name__)
MENU_ADD_EXPENSE = "1"
MENU_VIEW_SUMMARY = "2"
MENU_EXIT = "3"


def run_menu(data_file: Path) -> None:
    """Run the interactive CLI menu until the user exits."""
    try:
        expenses = load_expenses(data_file)
    except ExpenseStorageError as exc:
        print(f"Error: {exc}")
        return

    print("Expense Tracker CLI")
    print("Track expenses by category and review monthly totals.")

    while True:
        print("\n1. Add expense")
        print("2. View monthly summary")
        print("3. Exit")

        choice = input("Select an option: ").strip()
        if choice == MENU_ADD_EXPENSE:
            _handle_add_expense(expenses, data_file)
        elif choice == MENU_VIEW_SUMMARY:
            _handle_monthly_summary(expenses)
        elif choice == MENU_EXIT:
            print("Goodbye.")
            return
        else:
            print("Please choose 1, 2, or 3.")


def _handle_add_expense(expenses: list[Expense], data_file: Path) -> None:
    """Prompt for a new expense, validate it, and save it."""
    amount = _prompt_for_amount()
    category = _prompt_for_category()
    description = _prompt_for_description()

    expense = Expense(
        amount=amount,
        category=category,
        description=description,
        expense_date=date.today(),
    )
    expenses.append(expense)

    try:
        save_expenses(expenses, data_file)
    except ExpenseStorageError as exc:
        expenses.pop()
        print(f"Error: {exc}")
        return

    LOGGER.info(
        "Expense added.",
        extra={"category": expense.category, "month": expense.month},
    )
    print(f"Added ${expense.amount} for {expense.category}.")


def _handle_monthly_summary(expenses: list[Expense]) -> None:
    """Prompt for a month and display its summary totals."""
    default_month = date.today().strftime("%Y-%m")
    raw_month = input(f"Month to summarize [{default_month}]: ").strip()

    try:
        month = validate_month(raw_month or default_month)
    except ValueError as exc:
        print(f"Error: {exc}")
        return

    summary = build_monthly_summary(expenses, month)
    _print_summary(summary)


def _prompt_for_amount() -> Decimal:
    """Prompt until the user enters a valid expense amount."""
    while True:
        try:
            return parse_amount(input("Amount: $"))
        except ValueError as exc:
            print(f"Error: {exc}")


def _prompt_for_category() -> str:
    """Prompt until the user selects a valid expense category."""
    print("\nCategories")
    for index, category in enumerate(VALID_CATEGORIES, start=1):
        print(f"{index}. {category}")

    while True:
        raw_choice = input("Select category number: ").strip()
        if not raw_choice.isdigit():
            print("Error: Enter the number beside the category.")
            continue

        choice = int(raw_choice)
        if choice < 1 or choice > len(VALID_CATEGORIES):
            print(f"Error: Choose a number from 1 to {len(VALID_CATEGORIES)}.")
            continue

        try:
            return validate_category(VALID_CATEGORIES[choice - 1])
        except ValueError as exc:
            print(f"Error: {exc}")


def _prompt_for_description() -> str:
    """Prompt until the user enters a valid expense description."""
    while True:
        try:
            return validate_description(input("Description: "))
        except ValueError as exc:
            print(f"Error: {exc}")


def _print_summary(summary: MonthlySummary) -> None:
    """Print a monthly spending summary to the terminal."""
    print(f"\nSummary for {summary.month}")
    if not summary.category_totals:
        print("No expenses recorded for this month.")
        return

    for category, amount in summary.category_totals.items():
        print(f"{category}: ${amount}")
    print(f"Total: ${summary.total}")
