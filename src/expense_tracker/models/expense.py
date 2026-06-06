# src/expense_tracker/models/expense.py
# Defines the Expense data model and JSON serialization helpers.
# Connects to: src/expense_tracker/services/storage.py, src/expense_tracker/services/summary.py
# Created: 2026-06-06

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any
from uuid import uuid4

DATE_FORMAT = "%Y-%m-%d"
MONTH_FORMAT_LENGTH = 7


@dataclass(frozen=True)
class Expense:
    """Represent one categorized expense record."""

    amount: Decimal
    category: str
    description: str
    expense_date: date
    expense_id: str

    @property
    def month(self) -> str:
        """Return the YYYY-MM month used for summary grouping."""
        return self.expense_date.strftime("%Y-%m")

    def to_dict(self) -> dict[str, Any]:
        """Convert the expense into JSON-safe dictionary data."""
        return {
            "amount": str(self.amount),
            "category": self.category,
            "description": self.description,
            "date": self.expense_date.isoformat(),
            "id": self.expense_id,
            "month": self.month,
        }

    @classmethod
    def from_dict(cls, raw_expense: dict[str, Any]) -> "Expense":
        """Build an expense from decoded JSON dictionary data."""
        return cls(
            amount=Decimal(str(raw_expense["amount"])),
            category=str(raw_expense["category"]),
            description=str(raw_expense["description"]),
            expense_date=date.fromisoformat(str(raw_expense["date"])),
            expense_id=str(raw_expense.get("id") or uuid4()),
        )
