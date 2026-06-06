# src/expense_tracker/services/exporter.py
# Exports expense records to CSV for spreadsheet and reporting workflows.
# Connects to: src/expense_tracker/models/expense.py, src/expense_tracker/cli/commands.py
# Created: 2026-06-06

from csv import DictWriter
from pathlib import Path

from src.expense_tracker.models.expense import Expense

CSV_FIELDS = ("id", "date", "month", "category", "amount", "description")


class ExpenseExportError(RuntimeError):
    """Represent a failure while exporting expense data."""


def export_expenses_to_csv(expenses: list[Expense], output_file: Path) -> None:
    """Write expense records to a CSV file."""
    output_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        with output_file.open("w", encoding="utf-8", newline="") as file:
            writer = DictWriter(file, fieldnames=CSV_FIELDS)
            writer.writeheader()
            for expense in sorted(expenses, key=lambda record: record.expense_date):
                writer.writerow(
                    {
                        "id": expense.expense_id,
                        "date": expense.expense_date.isoformat(),
                        "month": expense.month,
                        "category": expense.category,
                        "amount": str(expense.amount),
                        "description": expense.description,
                    }
                )
    except OSError as exc:
        raise ExpenseExportError("Expense data could not be exported.") from exc
