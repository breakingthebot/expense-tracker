# src/expense_tracker/models/recurring_template.py
# Defines reusable recurring expense templates and JSON serialization helpers.
# Connects to: src/expense_tracker/services/recurring.py, src/expense_tracker/models/expense.py
# Created: 2026-06-06

from dataclasses import dataclass
from decimal import Decimal
from typing import Any
from uuid import uuid4


@dataclass(frozen=True)
class RecurringTemplate:
    """Represent one reusable recurring expense template."""

    amount: Decimal
    category: str
    description: str
    day: int
    template_id: str

    def to_dict(self) -> dict[str, Any]:
        """Convert the template into JSON-safe dictionary data."""
        return {
            "amount": str(self.amount),
            "category": self.category,
            "description": self.description,
            "day": self.day,
            "id": self.template_id,
        }

    @classmethod
    def from_dict(cls, raw_template: dict[str, Any]) -> "RecurringTemplate":
        """Build a template from decoded JSON dictionary data."""
        return cls(
            amount=Decimal(str(raw_template["amount"])),
            category=str(raw_template["category"]),
            description=str(raw_template["description"]),
            day=int(raw_template["day"]),
            template_id=str(raw_template.get("id") or uuid4()),
        )
