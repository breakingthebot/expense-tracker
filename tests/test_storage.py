# tests/test_storage.py
# Tests JSON persistence for expense records.
# Connects to: src/expense_tracker/services/storage.py, src/expense_tracker/models/expense.py
# Created: 2026-06-06

from datetime import date
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.expense_tracker.models.expense import Expense
from src.expense_tracker.services.storage import load_expenses, save_expenses


class StorageTests(unittest.TestCase):
    """Verify local JSON persistence behavior."""

    def test_save_and_load_expenses_round_trip(self) -> None:
        """Saved expenses can be loaded back as Expense objects."""
        expense = Expense(Decimal("15.25"), "Food", "Lunch", date(2026, 6, 6))

        with TemporaryDirectory() as temporary_directory:
            data_file = Path(temporary_directory) / "expenses.json"
            save_expenses([expense], data_file)

            loaded_expenses = load_expenses(data_file)

        self.assertEqual(loaded_expenses, [expense])

    def test_load_expenses_returns_empty_list_when_file_missing(self) -> None:
        """A missing data file starts the user with no saved expenses."""
        with TemporaryDirectory() as temporary_directory:
            data_file = Path(temporary_directory) / "expenses.json"

            self.assertEqual(load_expenses(data_file), [])


if __name__ == "__main__":
    unittest.main()
