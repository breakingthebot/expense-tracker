# src/expense_tracker/services/summary.py
# Calculates monthly totals from saved expense records.
# Connects to: src/expense_tracker/models/expense.py, src/expense_tracker/cli/menu.py
# Created: 2026-06-06

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from src.expense_tracker.models.expense import Expense

ZERO_DOLLARS = Decimal("0.00")
CENTS = Decimal("0.01")


@dataclass(frozen=True)
class MonthlySummary:
    """Represent spending totals for one month."""

    month: str
    category_totals: dict[str, Decimal]
    total: Decimal
    transaction_count: int
    average_expense: Decimal
    top_category: str | None


def build_monthly_summary(expenses: list[Expense], month: str) -> MonthlySummary:
    """Calculate category totals and grand total for the selected month."""
    category_totals: dict[str, Decimal] = {}
    transaction_count = 0
    total = ZERO_DOLLARS

    for expense in expenses:
        if expense.month != month:
            continue
        transaction_count += 1
        category_totals[expense.category] = (
            category_totals.get(expense.category, ZERO_DOLLARS) + expense.amount
        )
        total += expense.amount

    average_expense = _calculate_average(total, transaction_count)
    top_category = _find_top_category(category_totals)

    return MonthlySummary(
        month=month,
        category_totals=dict(sorted(category_totals.items())),
        total=total,
        transaction_count=transaction_count,
        average_expense=average_expense,
        top_category=top_category,
    )


def _calculate_average(total: Decimal, transaction_count: int) -> Decimal:
    """Return the average expense amount for a transaction count."""
    if transaction_count == 0:
        return ZERO_DOLLARS
    return (total / Decimal(transaction_count)).quantize(CENTS, rounding=ROUND_HALF_UP)


def _find_top_category(category_totals: dict[str, Decimal]) -> str | None:
    """Return the category with the highest total spending."""
    if not category_totals:
        return None
    return max(category_totals, key=category_totals.get)
