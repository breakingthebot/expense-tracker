# tests/test_budgets.py
# Tests monthly category budget persistence and updates.
# Connects to: src/expense_tracker/services/budgets.py
# Created: 2026-06-06

from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.expense_tracker.services.budgets import (
    get_monthly_budgets,
    load_budgets,
    save_budgets,
    set_monthly_budget,
)


class BudgetTests(unittest.TestCase):
    """Verify budget storage and update behavior."""

    def test_set_monthly_budget_updates_category_amount(self) -> None:
        """A budget update returns the selected month and category amount."""
        budgets = set_monthly_budget({}, "2026-06", "Food", Decimal("300.00"))

        self.assertEqual(budgets["2026-06"]["Food"], Decimal("300.00"))

    def test_save_and_load_budgets_round_trip(self) -> None:
        """Saved budgets load back as Decimal amounts."""
        budgets = {"2026-06": {"Food": Decimal("300.00")}}

        with TemporaryDirectory() as temporary_directory:
            budget_file = Path(temporary_directory) / "budgets.json"
            save_budgets(budgets, budget_file)

            loaded_budgets = load_budgets(budget_file)

        self.assertEqual(loaded_budgets, budgets)

    def test_get_monthly_budgets_returns_empty_dict_for_missing_month(self) -> None:
        """Missing month budget lookups return an empty dictionary."""
        self.assertEqual(get_monthly_budgets({}, "2026-06"), {})


if __name__ == "__main__":
    unittest.main()
