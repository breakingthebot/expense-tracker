# tests/test_commands.py
# Tests non-interactive command behavior for the expense tracker CLI.
# Connects to: src/expense_tracker/cli/commands.py
# Created: 2026-06-06

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import io
import unittest

from src.expense_tracker.cli.commands import run_cli
from src.expense_tracker.services.storage import load_expenses


class CommandTests(unittest.TestCase):
    """Verify command-mode add behavior."""

    def test_add_command_saves_expense(self) -> None:
        """The add command stores a validated expense in JSON."""
        with TemporaryDirectory() as temporary_directory:
            data_file = Path(temporary_directory) / "expenses.json"
            with patch("sys.stdout", new_callable=io.StringIO):
                exit_code = run_cli(
                    data_file,
                    [
                        "add",
                        "--amount",
                        "10.50",
                        "--category",
                        "Food",
                        "--description",
                        "Lunch",
                    ],
                )

            expenses = load_expenses(data_file)

        self.assertEqual(exit_code, 0)
        self.assertEqual(len(expenses), 1)
        self.assertEqual(expenses[0].category, "Food")


if __name__ == "__main__":
    unittest.main()
