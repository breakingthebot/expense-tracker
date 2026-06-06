# src/expense_tracker/services/recurring.py
# Loads, saves, and applies recurring expense templates.
# Connects to: src/expense_tracker/models/recurring_template.py, src/expense_tracker/models/expense.py
# Created: 2026-06-06

from datetime import date
from json import JSONDecodeError
import calendar
import json
import logging
from pathlib import Path
from uuid import uuid4

from src.expense_tracker.models.expense import Expense
from src.expense_tracker.models.recurring_template import RecurringTemplate

LOGGER = logging.getLogger(__name__)


class RecurringTemplateStorageError(RuntimeError):
    """Represent a failure while reading or writing recurring template data."""


def get_recurring_file_path(data_file: Path) -> Path:
    """Return the recurring template file path beside an expense data file."""
    return data_file.with_name("recurring_templates.json")


def load_recurring_templates(template_file: Path) -> list[RecurringTemplate]:
    """Load recurring expense templates from a JSON file."""
    if not template_file.exists():
        LOGGER.info(
            "Recurring template file does not exist yet.",
            extra={"path": str(template_file)},
        )
        return []

    try:
        with template_file.open("r", encoding="utf-8") as file:
            raw_templates = json.load(file)
    except JSONDecodeError as exc:
        LOGGER.error(
            "Recurring template file contains invalid JSON.",
            extra={"path": str(template_file)},
        )
        raise RecurringTemplateStorageError(
            "Saved recurring templates are not valid JSON."
        ) from exc
    except OSError as exc:
        LOGGER.error(
            "Recurring template file could not be read.",
            extra={"path": str(template_file)},
        )
        raise RecurringTemplateStorageError(
            "Saved recurring templates could not be read."
        ) from exc

    if not isinstance(raw_templates, list):
        raise RecurringTemplateStorageError("Saved recurring templates must be a list.")

    try:
        return [
            RecurringTemplate.from_dict(raw_template)
            for raw_template in raw_templates
        ]
    except (KeyError, TypeError, ValueError) as exc:
        raise RecurringTemplateStorageError(
            "Saved recurring templates have an invalid record."
        ) from exc


def save_recurring_templates(
    templates: list[RecurringTemplate],
    template_file: Path,
) -> None:
    """Save recurring expense templates to a JSON file."""
    template_file.parent.mkdir(parents=True, exist_ok=True)
    temporary_file = template_file.with_suffix(".tmp")

    try:
        with temporary_file.open("w", encoding="utf-8") as file:
            json.dump([template.to_dict() for template in templates], file, indent=2)
            file.write("\n")
        temporary_file.replace(template_file)
    except OSError as exc:
        LOGGER.error(
            "Recurring template file could not be written.",
            extra={"path": str(template_file)},
        )
        raise RecurringTemplateStorageError(
            "Recurring templates could not be saved."
        ) from exc


def apply_templates_to_month(
    templates: list[RecurringTemplate],
    month: str,
    existing_expenses: list[Expense] | None = None,
) -> list[Expense]:
    """Create non-duplicate expense records from templates for a selected month."""
    year_text, month_text = month.split("-")
    year = int(year_text)
    month_number = int(month_text)
    last_day = calendar.monthrange(year, month_number)[1]
    existing_keys = {
        _build_expense_match_key(expense)
        for expense in existing_expenses or []
        if expense.month == month
    }

    created_expenses: list[Expense] = []
    for template in templates:
        template_expense = Expense(
            amount=template.amount,
            category=template.category,
            description=template.description,
            expense_date=_build_template_date(template, year, month_number, last_day),
            expense_id=str(uuid4()),
        )
        expense_key = _build_expense_match_key(template_expense)
        if expense_key in existing_keys:
            continue

        created_expenses.append(template_expense)
        existing_keys.add(expense_key)

    return created_expenses


def _build_template_date(
    template: RecurringTemplate,
    year: int,
    month_number: int,
    last_day: int,
) -> date:
    """Return the applied expense date for a recurring template."""
    return date(year, month_number, min(template.day, last_day))


def _build_expense_match_key(expense: Expense) -> tuple[str, str, str, str]:
    """Return the fields used to identify recurring duplicate expenses."""
    return (
        expense.expense_date.isoformat(),
        expense.category,
        str(expense.amount),
        expense.description,
    )
