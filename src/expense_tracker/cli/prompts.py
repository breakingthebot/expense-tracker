# src/expense_tracker/cli/prompts.py
# Collects and validates questionnaire-style terminal input.
# Connects to: src/expense_tracker/cli/menu.py, src/expense_tracker/utils/validators.py
# Created: 2026-06-06

from datetime import date
from decimal import Decimal
from pathlib import Path

from src.expense_tracker.models.expense import Expense
from src.expense_tracker.utils.validators import (
    VALID_CATEGORIES,
    parse_amount,
    parse_expense_date,
    validate_category,
    validate_description,
    validate_month,
)


def prompt_for_amount() -> Decimal:
    """Prompt until the user enters a valid expense amount."""
    while True:
        try:
            return parse_amount(input("Amount: $"))
        except ValueError as exc:
            print(f"Error: {exc}")


def prompt_for_category() -> str:
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
        return validate_category(VALID_CATEGORIES[choice - 1])


def prompt_for_description() -> str:
    """Prompt until the user enters a valid expense description."""
    while True:
        try:
            return validate_description(input("Description: "))
        except ValueError as exc:
            print(f"Error: {exc}")


def prompt_for_expense_date() -> date:
    """Prompt until the user enters a valid date or accepts today's date."""
    default_date = date.today().isoformat()
    while True:
        raw_date = input(f"Date [{default_date}]: ").strip()
        try:
            return parse_expense_date(raw_date or default_date)
        except ValueError as exc:
            print(f"Error: {exc}")


def prompt_for_month(label: str) -> str:
    """Prompt until the user enters a valid month or accepts current month."""
    default_month = date.today().strftime("%Y-%m")
    while True:
        raw_month = input(f"{label} [{default_month}]: ").strip()
        try:
            return validate_month(raw_month or default_month)
        except ValueError as exc:
            print(f"Error: {exc}")


def prompt_for_optional_month(label: str) -> str | None:
    """Prompt for an optional month filter."""
    while True:
        raw_month = input(f"{label}: ").strip()
        if not raw_month:
            return None
        try:
            return validate_month(raw_month)
        except ValueError as exc:
            print(f"Error: {exc}")


def prompt_for_output_path() -> Path:
    """Prompt until the user enters a CSV output path."""
    while True:
        raw_path = input("CSV output path [exports/expenses.csv]: ").strip()
        output_path = Path(raw_path or "exports/expenses.csv")
        if output_path.suffix.lower() != ".csv":
            print("Error: Output path must end with .csv.")
            continue
        return output_path


def prompt_for_expense_updates(expense: Expense) -> Expense:
    """Prompt for optional edits and return an updated expense."""
    return Expense(
        amount=_prompt_for_optional_amount(expense.amount),
        category=_prompt_for_optional_category(expense.category),
        description=_prompt_for_optional_description(expense.description),
        expense_date=_prompt_for_optional_date(expense.expense_date),
        expense_id=expense.expense_id,
    )


def _prompt_for_optional_amount(current_amount: Decimal) -> Decimal:
    """Prompt for an optional updated amount."""
    while True:
        raw_amount = input(f"Amount [{current_amount}]: ").strip()
        if not raw_amount:
            return current_amount
        try:
            return parse_amount(raw_amount)
        except ValueError as exc:
            print(f"Error: {exc}")


def _prompt_for_optional_category(current_category: str) -> str:
    """Prompt for an optional updated category."""
    print("\nCategories")
    for index, category in enumerate(VALID_CATEGORIES, start=1):
        print(f"{index}. {category}")

    while True:
        raw_choice = input(f"Category number [{current_category}]: ").strip()
        if not raw_choice:
            return current_category
        if not raw_choice.isdigit():
            print("Error: Enter the number beside the category.")
            continue

        choice = int(raw_choice)
        if choice < 1 or choice > len(VALID_CATEGORIES):
            print(f"Error: Choose a number from 1 to {len(VALID_CATEGORIES)}.")
            continue
        return validate_category(VALID_CATEGORIES[choice - 1])


def _prompt_for_optional_description(current_description: str) -> str:
    """Prompt for an optional updated description."""
    while True:
        raw_description = input(f"Description [{current_description}]: ").strip()
        if not raw_description:
            return current_description
        try:
            return validate_description(raw_description)
        except ValueError as exc:
            print(f"Error: {exc}")


def _prompt_for_optional_date(current_date: date) -> date:
    """Prompt for an optional updated date."""
    while True:
        raw_date = input(f"Date [{current_date.isoformat()}]: ").strip()
        if not raw_date:
            return current_date
        try:
            return parse_expense_date(raw_date)
        except ValueError as exc:
            print(f"Error: {exc}")
