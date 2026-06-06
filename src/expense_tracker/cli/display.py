# src/expense_tracker/cli/display.py
# Prints terminal output for expense lists, summaries, and reports.
# Connects to: src/expense_tracker/cli/menu.py, src/expense_tracker/models/expense.py
# Created: 2026-06-06

from src.expense_tracker.models.expense import Expense
from src.expense_tracker.services.summary import MonthlySummary


def print_expenses(expenses: list[Expense], month: str | None) -> None:
    """Print expenses in a readable table-like format."""
    title = f"\nExpenses for {month}" if month else "\nAll expenses"
    print(title)
    if not expenses:
        print("No expenses found.")
        return

    sorted_expenses = sorted(expenses, key=lambda expense: expense.expense_date)
    for expense in sorted_expenses:
        print(
            f"{expense.expense_id} | "
            f"{expense.expense_date.isoformat()} | "
            f"{expense.category} | "
            f"${expense.amount} | "
            f"{expense.description}"
        )


def print_summary(summary: MonthlySummary) -> None:
    """Print a monthly spending summary to the terminal."""
    print(f"\nSummary for {summary.month}")
    if not summary.category_totals:
        print("No expenses recorded for this month.")
        return

    for category, amount in summary.category_totals.items():
        print(f"{category}: ${amount}")
    print(f"Total: ${summary.total}")


def print_report(summary: MonthlySummary) -> None:
    """Print a monthly spending report to the terminal."""
    print(f"\nReport for {summary.month}")
    if summary.transaction_count == 0:
        print("No expenses recorded for this month.")
        return

    print(f"Total spent: ${summary.total}")
    print(f"Transactions: {summary.transaction_count}")
    print(f"Average expense: ${summary.average_expense}")
    print(f"Top category: {summary.top_category}")
    print("Category breakdown:")
    for category, amount in summary.category_totals.items():
        print(f"- {category}: ${amount}")
