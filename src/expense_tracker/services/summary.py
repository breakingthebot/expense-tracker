# src/expense_tracker/services/summary.py
# Calculates monthly totals from saved expense records.
# Connects to: src/expense_tracker/models/expense.py, src/expense_tracker/cli/menu.py
# Created: 2026-06-06

from dataclasses import dataclass
from decimal import Decimal

from src.expense_tracker.models.expense import Expense

ZERO_DOLLARS = Decimal("0.00")


@dataclass(frozen=True)
class MonthlySummary:
    """Represent spending totals for one month."""

    month: str
    category_totals: dict[str, Decimal]
    total: Decimal


def build_monthly_summary(expenses: list[Expense], month: str) -> MonthlySummary:
    """Calculate category totals and grand total for the selected month."""
    category_totals: dict[str, Decimal] = {}
    total = ZERO_DOLLARS

    for expense in expenses:
        if expense.month != month:
            continue
        category_totals[expense.category] = (
            category_totals.get(expense.category, ZERO_DOLLARS) + expense.amount
        )
        total += expense.amount

    return MonthlySummary(
        month=month,
        category_totals=dict(sorted(category_totals.items())),
        total=total,
    )
