# tests/test_summary.py
# Tests monthly summary calculations from expense records.
# Connects to: src/expense_tracker/services/summary.py, src/expense_tracker/models/expense.py
# Created: 2026-06-06

from datetime import date
from decimal import Decimal
import unittest

from src.expense_tracker.models.expense import Expense
from src.expense_tracker.services.summary import build_monthly_summary


class SummaryTests(unittest.TestCase):
    """Verify monthly category and total calculations."""

    def test_build_monthly_summary_groups_by_category(self) -> None:
        """Expenses in the selected month are summed by category."""
        expenses = [
            Expense(Decimal("12.50"), "Food", "Lunch", date(2026, 6, 1)),
            Expense(Decimal("7.25"), "Food", "Coffee", date(2026, 6, 2)),
            Expense(Decimal("40.00"), "Utilities", "Internet", date(2026, 6, 3)),
            Expense(Decimal("99.99"), "Food", "Old month", date(2026, 5, 1)),
        ]

        summary = build_monthly_summary(expenses, "2026-06")

        self.assertEqual(summary.total, Decimal("59.75"))
        self.assertEqual(summary.category_totals["Food"], Decimal("19.75"))
        self.assertEqual(summary.category_totals["Utilities"], Decimal("40.00"))

    def test_build_monthly_summary_handles_empty_month(self) -> None:
        """A month with no expenses returns empty totals."""
        summary = build_monthly_summary([], "2026-06")

        self.assertEqual(summary.total, Decimal("0.00"))
        self.assertEqual(summary.category_totals, {})


if __name__ == "__main__":
    unittest.main()
