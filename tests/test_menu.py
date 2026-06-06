# tests/test_menu.py
# Tests guided questionnaire-style menu flows for the expense tracker CLI.
# Connects to: src/expense_tracker/cli/menu.py, src/expense_tracker/services/storage.py
# Created: 2026-06-06

from datetime import date
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import io
import unittest

from src.expense_tracker.cli.menu import run_menu
from src.expense_tracker.models.expense import Expense
from src.expense_tracker.services.storage import load_expenses, save_expenses


class MenuTests(unittest.TestCase):
    """Verify questionnaire-style interactive menu behavior."""

    def test_menu_add_expense_saves_prompted_record(self) -> None:
        """The guided add flow saves an expense from user prompts."""
        user_inputs = iter(
            [
                "1",
                "12.50",
                "1",
                "Lunch",
                "2026-06-01",
                "8",
            ]
        )

        with TemporaryDirectory() as temporary_directory:
            data_file = Path(temporary_directory) / "expenses.json"
            with patch("builtins.input", lambda _prompt: next(user_inputs)):
                with patch("sys.stdout", new_callable=io.StringIO):
                    run_menu(data_file)

            expenses = load_expenses(data_file)

        self.assertEqual(len(expenses), 1)
        self.assertEqual(expenses[0].amount, Decimal("12.50"))
        self.assertEqual(expenses[0].category, "Food")
        self.assertEqual(expenses[0].expense_date, date(2026, 6, 1))

    def test_menu_report_prints_prompted_month(self) -> None:
        """The guided report flow prints metrics for the selected month."""
        user_inputs = iter(["6", "2026-06", "8"])
        expense = Expense(
            Decimal("20.00"),
            "Utilities",
            "Internet",
            date(2026, 6, 1),
            "expense-1",
        )

        with TemporaryDirectory() as temporary_directory:
            data_file = Path(temporary_directory) / "expenses.json"
            save_expenses([expense], data_file)

            with patch("builtins.input", lambda _prompt: next(user_inputs)):
                with patch("sys.stdout", new_callable=io.StringIO) as output:
                    run_menu(data_file)

        self.assertIn("Report for 2026-06", output.getvalue())
        self.assertIn("Top category: Utilities", output.getvalue())


if __name__ == "__main__":
    unittest.main()
