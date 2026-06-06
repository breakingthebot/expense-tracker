# tests/test_commands.py
# Tests non-interactive command behavior for the expense tracker CLI.
# Connects to: src/expense_tracker/cli/commands.py
# Created: 2026-06-06

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from datetime import date
import csv
import io
import unittest

from src.expense_tracker.cli.commands import run_cli
from src.expense_tracker.services.storage import load_expenses


class CommandTests(unittest.TestCase):
    """Verify command-mode behavior."""

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
                        "--date",
                        "2026-06-01",
                    ],
                )

            expenses = load_expenses(data_file)

        self.assertEqual(exit_code, 0)
        self.assertEqual(len(expenses), 1)
        self.assertEqual(expenses[0].category, "Food")
        self.assertEqual(expenses[0].expense_date, date(2026, 6, 1))
        self.assertTrue(expenses[0].expense_id)

    def test_list_command_prints_saved_expenses(self) -> None:
        """The list command displays saved expenses in date order."""
        with TemporaryDirectory() as temporary_directory:
            data_file = Path(temporary_directory) / "expenses.json"
            with patch("sys.stdout", new_callable=io.StringIO):
                run_cli(
                    data_file,
                    [
                        "add",
                        "--amount",
                        "10.50",
                        "--category",
                        "Food",
                        "--description",
                        "Lunch",
                        "--date",
                        "2026-06-01",
                    ],
                )
            with patch("sys.stdout", new_callable=io.StringIO) as output:
                exit_code = run_cli(data_file, ["list"])

        self.assertEqual(exit_code, 0)
        self.assertIn("All expenses", output.getvalue())
        self.assertIn("2026-06-01 | Food | $10.50 | Lunch", output.getvalue())

    def test_list_command_filters_by_month(self) -> None:
        """The list command can filter expenses by YYYY-MM."""
        with TemporaryDirectory() as temporary_directory:
            data_file = Path(temporary_directory) / "expenses.json"
            for raw_date, description in (
                ("2026-06-01", "Lunch"),
                ("2026-07-01", "Dinner"),
            ):
                with patch("sys.stdout", new_callable=io.StringIO):
                    run_cli(
                        data_file,
                        [
                            "add",
                            "--amount",
                            "10.50",
                            "--category",
                            "Food",
                            "--description",
                            description,
                            "--date",
                            raw_date,
                        ],
                    )

            with patch("sys.stdout", new_callable=io.StringIO) as output:
                exit_code = run_cli(data_file, ["list", "--month", "2026-06"])

        self.assertEqual(exit_code, 0)
        self.assertIn("Expenses for 2026-06", output.getvalue())
        self.assertIn("Lunch", output.getvalue())
        self.assertNotIn("Dinner", output.getvalue())

    def test_delete_command_removes_saved_expense(self) -> None:
        """The delete command removes one saved expense by ID."""
        with TemporaryDirectory() as temporary_directory:
            data_file = Path(temporary_directory) / "expenses.json"
            with patch("sys.stdout", new_callable=io.StringIO):
                run_cli(
                    data_file,
                    [
                        "add",
                        "--amount",
                        "10.50",
                        "--category",
                        "Food",
                        "--description",
                        "Lunch",
                        "--date",
                        "2026-06-01",
                    ],
                )
            expense_id = load_expenses(data_file)[0].expense_id

            with patch("sys.stdout", new_callable=io.StringIO) as output:
                exit_code = run_cli(data_file, ["delete", "--id", expense_id])

            expenses = load_expenses(data_file)

        self.assertEqual(exit_code, 0)
        self.assertEqual(expenses, [])
        self.assertIn(f"Deleted expense {expense_id}.", output.getvalue())

    def test_delete_command_returns_error_for_missing_id(self) -> None:
        """The delete command reports when the requested ID does not exist."""
        with TemporaryDirectory() as temporary_directory:
            data_file = Path(temporary_directory) / "expenses.json"
            with patch("sys.stdout", new_callable=io.StringIO) as output:
                exit_code = run_cli(data_file, ["delete", "--id", "missing-id"])

        self.assertEqual(exit_code, 1)
        self.assertIn("Error: No expense found with that ID.", output.getvalue())

    def test_budget_set_and_list_commands_manage_monthly_budget(self) -> None:
        """Budget commands save and display monthly category budgets."""
        with TemporaryDirectory() as temporary_directory:
            data_file = Path(temporary_directory) / "expenses.json"

            with patch("sys.stdout", new_callable=io.StringIO) as set_output:
                set_exit_code = run_cli(
                    data_file,
                    [
                        "budget",
                        "set",
                        "--month",
                        "2026-06",
                        "--category",
                        "Food",
                        "--amount",
                        "300.00",
                    ],
                )

            with patch("sys.stdout", new_callable=io.StringIO) as list_output:
                list_exit_code = run_cli(
                    data_file,
                    ["budget", "list", "--month", "2026-06"],
                )

        self.assertEqual(set_exit_code, 0)
        self.assertEqual(list_exit_code, 0)
        self.assertIn("Set Food budget for 2026-06 to $300.00.", set_output.getvalue())
        self.assertIn("Food: $300.00", list_output.getvalue())

    def test_edit_command_updates_saved_expense(self) -> None:
        """The edit command updates provided fields and preserves the expense ID."""
        with TemporaryDirectory() as temporary_directory:
            data_file = Path(temporary_directory) / "expenses.json"
            with patch("sys.stdout", new_callable=io.StringIO):
                run_cli(
                    data_file,
                    [
                        "add",
                        "--amount",
                        "10.50",
                        "--category",
                        "Food",
                        "--description",
                        "Lunch",
                        "--date",
                        "2026-06-01",
                    ],
                )
            original_expense = load_expenses(data_file)[0]

            with patch("sys.stdout", new_callable=io.StringIO) as output:
                exit_code = run_cli(
                    data_file,
                    [
                        "edit",
                        "--id",
                        original_expense.expense_id,
                        "--amount",
                        "12.25",
                        "--category",
                        "Entertainment",
                        "--description",
                        "Movie",
                        "--date",
                        "2026-06-02",
                    ],
                )

            edited_expense = load_expenses(data_file)[0]

        self.assertEqual(exit_code, 0)
        self.assertEqual(edited_expense.expense_id, original_expense.expense_id)
        self.assertEqual(str(edited_expense.amount), "12.25")
        self.assertEqual(edited_expense.category, "Entertainment")
        self.assertEqual(edited_expense.description, "Movie")
        self.assertEqual(edited_expense.expense_date, date(2026, 6, 2))
        self.assertIn(f"Updated expense {original_expense.expense_id}.", output.getvalue())

    def test_edit_command_requires_update_field(self) -> None:
        """The edit command rejects requests that do not change any fields."""
        with TemporaryDirectory() as temporary_directory:
            data_file = Path(temporary_directory) / "expenses.json"
            with patch("sys.stdout", new_callable=io.StringIO) as output:
                exit_code = run_cli(data_file, ["edit", "--id", "expense-1"])

        self.assertEqual(exit_code, 1)
        self.assertIn("Error: Provide at least one field to update.", output.getvalue())

    def test_edit_command_returns_error_for_missing_id(self) -> None:
        """The edit command reports when the requested ID does not exist."""
        with TemporaryDirectory() as temporary_directory:
            data_file = Path(temporary_directory) / "expenses.json"
            with patch("sys.stdout", new_callable=io.StringIO) as output:
                exit_code = run_cli(
                    data_file,
                    ["edit", "--id", "missing-id", "--amount", "12.25"],
                )

        self.assertEqual(exit_code, 1)
        self.assertIn("Error: No expense found with that ID.", output.getvalue())

    def test_export_command_writes_csv_file(self) -> None:
        """The export command writes saved expenses to CSV."""
        with TemporaryDirectory() as temporary_directory:
            data_file = Path(temporary_directory) / "expenses.json"
            output_file = Path(temporary_directory) / "exports" / "expenses.csv"
            with patch("sys.stdout", new_callable=io.StringIO):
                run_cli(
                    data_file,
                    [
                        "add",
                        "--amount",
                        "10.50",
                        "--category",
                        "Food",
                        "--description",
                        "Lunch",
                        "--date",
                        "2026-06-01",
                    ],
                )

            with patch("sys.stdout", new_callable=io.StringIO) as output:
                exit_code = run_cli(
                    data_file,
                    ["export", "--output", str(output_file)],
                )

            with output_file.open("r", encoding="utf-8", newline="") as file:
                rows = list(csv.DictReader(file))

        self.assertEqual(exit_code, 0)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["date"], "2026-06-01")
        self.assertEqual(rows[0]["amount"], "10.50")
        self.assertIn("Exported 1 expense record(s)", output.getvalue())

    def test_export_command_filters_by_month(self) -> None:
        """The export command can write only one month of expenses."""
        with TemporaryDirectory() as temporary_directory:
            data_file = Path(temporary_directory) / "expenses.json"
            output_file = Path(temporary_directory) / "expenses.csv"
            for raw_date, description in (
                ("2026-06-01", "Lunch"),
                ("2026-07-01", "Dinner"),
            ):
                with patch("sys.stdout", new_callable=io.StringIO):
                    run_cli(
                        data_file,
                        [
                            "add",
                            "--amount",
                            "10.50",
                            "--category",
                            "Food",
                            "--description",
                            description,
                            "--date",
                            raw_date,
                        ],
                    )

            with patch("sys.stdout", new_callable=io.StringIO):
                exit_code = run_cli(
                    data_file,
                    ["export", "--output", str(output_file), "--month", "2026-06"],
                )

            with output_file.open("r", encoding="utf-8", newline="") as file:
                rows = list(csv.DictReader(file))

        self.assertEqual(exit_code, 0)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["description"], "Lunch")

    def test_report_command_prints_monthly_insights(self) -> None:
        """The report command prints richer monthly spending metrics."""
        with TemporaryDirectory() as temporary_directory:
            data_file = Path(temporary_directory) / "expenses.json"
            for amount, category, description in (
                ("10.50", "Food", "Lunch"),
                ("20.00", "Utilities", "Internet"),
            ):
                with patch("sys.stdout", new_callable=io.StringIO):
                    run_cli(
                        data_file,
                        [
                            "add",
                            "--amount",
                            amount,
                            "--category",
                            category,
                            "--description",
                            description,
                            "--date",
                            "2026-06-01",
                        ],
                    )

            with patch("sys.stdout", new_callable=io.StringIO) as output:
                exit_code = run_cli(data_file, ["report", "--month", "2026-06"])

        self.assertEqual(exit_code, 0)
        self.assertIn("Report for 2026-06", output.getvalue())
        self.assertIn("Total spent: $30.50", output.getvalue())
        self.assertIn("Transactions: 2", output.getvalue())
        self.assertIn("Average expense: $15.25", output.getvalue())
        self.assertIn("Top category: Utilities", output.getvalue())

    def test_report_command_prints_budget_comparison(self) -> None:
        """The report command compares monthly spending against budgets."""
        with TemporaryDirectory() as temporary_directory:
            data_file = Path(temporary_directory) / "expenses.json"
            with patch("sys.stdout", new_callable=io.StringIO):
                run_cli(
                    data_file,
                    [
                        "add",
                        "--amount",
                        "75.00",
                        "--category",
                        "Food",
                        "--description",
                        "Groceries",
                        "--date",
                        "2026-06-01",
                    ],
                )
                run_cli(
                    data_file,
                    [
                        "budget",
                        "set",
                        "--month",
                        "2026-06",
                        "--category",
                        "Food",
                        "--amount",
                        "100.00",
                    ],
                )

            with patch("sys.stdout", new_callable=io.StringIO) as output:
                exit_code = run_cli(data_file, ["report", "--month", "2026-06"])

        self.assertEqual(exit_code, 0)
        self.assertIn(
            "- Food: budget $100.00, spent $75.00, remaining $25.00",
            output.getvalue(),
        )


if __name__ == "__main__":
    unittest.main()
