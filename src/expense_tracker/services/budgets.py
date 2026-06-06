# src/expense_tracker/services/budgets.py
# Loads, saves, and updates monthly category budgets.
# Connects to: src/expense_tracker/cli/commands.py, src/expense_tracker/cli/menu.py
# Created: 2026-06-06

from decimal import Decimal
from json import JSONDecodeError
import json
import logging
from pathlib import Path

LOGGER = logging.getLogger(__name__)


class BudgetStorageError(RuntimeError):
    """Represent a failure while reading or writing budget data."""


def get_budget_file_path(data_file: Path) -> Path:
    """Return the budget file path that belongs beside an expense data file."""
    return data_file.with_name("budgets.json")


def load_budgets(budget_file: Path) -> dict[str, dict[str, Decimal]]:
    """Load monthly category budgets from a JSON file."""
    if not budget_file.exists():
        LOGGER.info(
            "Budget data file does not exist yet.",
            extra={"path": str(budget_file)},
        )
        return {}

    try:
        with budget_file.open("r", encoding="utf-8") as file:
            raw_budgets = json.load(file)
    except JSONDecodeError as exc:
        LOGGER.error(
            "Budget data file contains invalid JSON.",
            extra={"path": str(budget_file)},
        )
        raise BudgetStorageError("Saved budget data is not valid JSON.") from exc
    except OSError as exc:
        LOGGER.error(
            "Budget data file could not be read.",
            extra={"path": str(budget_file)},
        )
        raise BudgetStorageError("Saved budget data could not be read.") from exc

    if not isinstance(raw_budgets, dict):
        raise BudgetStorageError("Saved budget data must be an object.")

    try:
        return {
            str(month): {
                str(category): Decimal(str(amount))
                for category, amount in category_budgets.items()
            }
            for month, category_budgets in raw_budgets.items()
        }
    except (AttributeError, TypeError) as exc:
        raise BudgetStorageError("Saved budget data has an invalid record.") from exc


def save_budgets(budgets: dict[str, dict[str, Decimal]], budget_file: Path) -> None:
    """Save monthly category budgets to a JSON file."""
    budget_file.parent.mkdir(parents=True, exist_ok=True)
    temporary_file = budget_file.with_suffix(".tmp")

    serializable_budgets = {
        month: {
            category: str(amount)
            for category, amount in sorted(category_budgets.items())
        }
        for month, category_budgets in sorted(budgets.items())
    }

    try:
        with temporary_file.open("w", encoding="utf-8") as file:
            json.dump(serializable_budgets, file, indent=2)
            file.write("\n")
        temporary_file.replace(budget_file)
    except OSError as exc:
        LOGGER.error(
            "Budget data file could not be written.",
            extra={"path": str(budget_file)},
        )
        raise BudgetStorageError("Budget data could not be saved.") from exc


def set_monthly_budget(
    budgets: dict[str, dict[str, Decimal]],
    month: str,
    category: str,
    amount: Decimal,
) -> dict[str, dict[str, Decimal]]:
    """Return budgets with one monthly category budget updated."""
    updated_budgets = {
        existing_month: dict(category_budgets)
        for existing_month, category_budgets in budgets.items()
    }
    updated_budgets.setdefault(month, {})[category] = amount
    return updated_budgets


def get_monthly_budgets(
    budgets: dict[str, dict[str, Decimal]],
    month: str,
) -> dict[str, Decimal]:
    """Return category budgets for one month."""
    return dict(budgets.get(month, {}))
