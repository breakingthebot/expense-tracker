# src/expense_tracker/services/storage.py
# Loads and saves expense records to a local JSON file.
# Connects to: src/expense_tracker/models/expense.py, src/expense_tracker/config/settings.py
# Created: 2026-06-06

from json import JSONDecodeError
import json
import logging
from pathlib import Path

from src.expense_tracker.models.expense import Expense

LOGGER = logging.getLogger(__name__)


class ExpenseStorageError(RuntimeError):
    """Represent a failure while reading or writing expense data."""


def load_expenses(data_file: Path) -> list[Expense]:
    """Load expenses from a JSON file, returning an empty list when absent."""
    if not data_file.exists():
        LOGGER.info("Expense data file does not exist yet.", extra={"path": str(data_file)})
        return []

    try:
        with data_file.open("r", encoding="utf-8") as file:
            raw_expenses = json.load(file)
    except JSONDecodeError as exc:
        LOGGER.error("Expense data file contains invalid JSON.", extra={"path": str(data_file)})
        raise ExpenseStorageError("Saved expense data is not valid JSON.") from exc
    except OSError as exc:
        LOGGER.error("Expense data file could not be read.", extra={"path": str(data_file)})
        raise ExpenseStorageError("Saved expense data could not be read.") from exc

    if not isinstance(raw_expenses, list):
        raise ExpenseStorageError("Saved expense data must be a list.")

    try:
        return [Expense.from_dict(raw_expense) for raw_expense in raw_expenses]
    except (KeyError, TypeError, ValueError) as exc:
        LOGGER.error("Expense data file has an invalid record.", extra={"path": str(data_file)})
        raise ExpenseStorageError("Saved expense data has an invalid record.") from exc


def save_expenses(expenses: list[Expense], data_file: Path) -> None:
    """Save expenses to a JSON file using an atomic replace."""
    data_file.parent.mkdir(parents=True, exist_ok=True)
    temporary_file = data_file.with_suffix(".tmp")

    try:
        with temporary_file.open("w", encoding="utf-8") as file:
            json.dump([expense.to_dict() for expense in expenses], file, indent=2)
            file.write("\n")
        temporary_file.replace(data_file)
    except OSError as exc:
        LOGGER.error("Expense data file could not be written.", extra={"path": str(data_file)})
        raise ExpenseStorageError("Expense data could not be saved.") from exc
