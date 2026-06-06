# src/expense_tracker/cli/commands.py
# Provides non-interactive command parsing for expense tracker actions.
# Connects to: src/expense_tracker/services/storage.py, src/expense_tracker/services/exporter.py
# Created: 2026-06-06

from argparse import ArgumentParser, Namespace
from datetime import date
from decimal import Decimal
from pathlib import Path
import logging
from uuid import uuid4

from src.expense_tracker.cli.menu import run_menu
from src.expense_tracker.models.expense import Expense
from src.expense_tracker.models.recurring_template import RecurringTemplate
from src.expense_tracker.services.budgets import (
    BudgetStorageError,
    get_budget_file_path,
    get_monthly_budgets,
    load_budgets,
    save_budgets,
    set_monthly_budget,
)
from src.expense_tracker.services.exporter import (
    ExpenseExportError,
    export_expenses_to_csv,
)
from src.expense_tracker.services.recurring import (
    RecurringTemplateStorageError,
    apply_templates_to_month,
    get_recurring_file_path,
    load_recurring_templates,
    save_recurring_templates,
)
from src.expense_tracker.services.storage import (
    ExpenseStorageError,
    load_expenses,
    save_expenses,
)
from src.expense_tracker.services.summary import MonthlySummary, build_monthly_summary
from src.expense_tracker.utils.validators import (
    VALID_CATEGORIES,
    parse_amount,
    parse_expense_date,
    validate_category,
    validate_description,
    validate_month,
)

LOGGER = logging.getLogger(__name__)
MIN_RECURRING_DAY = 1
MAX_RECURRING_DAY = 31


def build_parser() -> ArgumentParser:
    """Create the argument parser for expense tracker commands."""
    parser = ArgumentParser(description="Track expenses by category in a JSON file.")
    subparsers = parser.add_subparsers(dest="command")

    add_parser = subparsers.add_parser("add", help="Add a new expense.")
    add_parser.add_argument(
        "--amount",
        required=True,
        help="Expense amount, such as 12.50.",
    )
    add_parser.add_argument("--category", required=True, choices=VALID_CATEGORIES)
    add_parser.add_argument("--description", required=True)
    add_parser.add_argument(
        "--date",
        default=date.today().isoformat(),
        help="Expense date in YYYY-MM-DD format. Defaults to today.",
    )

    summary_parser = subparsers.add_parser("summary", help="Show a monthly summary.")
    summary_parser.add_argument(
        "--month",
        default=date.today().strftime("%Y-%m"),
        help="Month to summarize in YYYY-MM format.",
    )

    report_parser = subparsers.add_parser(
        "report",
        help="Show monthly spending insights.",
    )
    report_parser.add_argument(
        "--month",
        default=date.today().strftime("%Y-%m"),
        help="Month to report in YYYY-MM format.",
    )

    budget_parser = subparsers.add_parser("budget", help="Manage monthly budgets.")
    budget_subparsers = budget_parser.add_subparsers(dest="budget_action")

    budget_set_parser = budget_subparsers.add_parser(
        "set",
        help="Set a category budget.",
    )
    budget_set_parser.add_argument(
        "--month",
        required=True,
        help="Budget month in YYYY-MM format.",
    )
    budget_set_parser.add_argument(
        "--category",
        required=True,
        choices=VALID_CATEGORIES,
    )
    budget_set_parser.add_argument(
        "--amount",
        required=True,
        help="Budget amount.",
    )

    budget_list_parser = budget_subparsers.add_parser("list", help="List budgets.")
    budget_list_parser.add_argument(
        "--month",
        default=date.today().strftime("%Y-%m"),
        help="Budget month in YYYY-MM format.",
    )

    recurring_parser = subparsers.add_parser(
        "recurring",
        help="Manage recurring expense templates.",
    )
    recurring_subparsers = recurring_parser.add_subparsers(dest="recurring_action")

    recurring_add_parser = recurring_subparsers.add_parser(
        "add",
        help="Create a recurring expense template.",
    )
    recurring_add_parser.add_argument("--amount", required=True)
    recurring_add_parser.add_argument(
        "--category",
        required=True,
        choices=VALID_CATEGORIES,
    )
    recurring_add_parser.add_argument("--description", required=True)
    recurring_add_parser.add_argument(
        "--day",
        required=True,
        help="Day of month from 1 to 31.",
    )

    recurring_subparsers.add_parser("list", help="List recurring templates.")

    recurring_apply_parser = recurring_subparsers.add_parser(
        "apply",
        help="Apply recurring templates to a month.",
    )
    recurring_apply_parser.add_argument(
        "--month",
        required=True,
        help="Month to create expenses for in YYYY-MM format.",
    )

    list_parser = subparsers.add_parser("list", help="List saved expenses.")
    list_parser.add_argument(
        "--month",
        help="Optional month filter in YYYY-MM format.",
    )

    delete_parser = subparsers.add_parser("delete", help="Delete an expense by ID.")
    delete_parser.add_argument(
        "--id",
        required=True,
        help="Expense ID from the list command.",
    )

    edit_parser = subparsers.add_parser("edit", help="Edit an expense by ID.")
    edit_parser.add_argument(
        "--id",
        required=True,
        help="Expense ID from the list command.",
    )
    edit_parser.add_argument("--amount", help="Updated expense amount.")
    edit_parser.add_argument(
        "--category",
        choices=VALID_CATEGORIES,
        help="Updated category.",
    )
    edit_parser.add_argument("--description", help="Updated description.")
    edit_parser.add_argument("--date", help="Updated date in YYYY-MM-DD format.")

    export_parser = subparsers.add_parser("export", help="Export expenses to CSV.")
    export_parser.add_argument(
        "--output",
        required=True,
        help="CSV file path to create.",
    )
    export_parser.add_argument(
        "--month",
        help="Optional month filter in YYYY-MM format.",
    )

    subparsers.add_parser("interactive", help="Open the guided interactive menu.")
    return parser


def run_cli(data_file: Path, arguments: list[str] | None = None) -> int:
    """Run a command-line action and return a process exit code."""
    parser = build_parser()
    parsed_arguments = parser.parse_args(arguments)

    if parsed_arguments.command == "add":
        return _run_add_command(parsed_arguments, data_file)
    if parsed_arguments.command == "budget":
        return _run_budget_command(parsed_arguments, data_file)
    if parsed_arguments.command == "delete":
        return _run_delete_command(parsed_arguments, data_file)
    if parsed_arguments.command == "edit":
        return _run_edit_command(parsed_arguments, data_file)
    if parsed_arguments.command == "export":
        return _run_export_command(parsed_arguments, data_file)
    if parsed_arguments.command == "list":
        return _run_list_command(parsed_arguments, data_file)
    if parsed_arguments.command == "recurring":
        return _run_recurring_command(parsed_arguments, data_file)
    if parsed_arguments.command == "report":
        return _run_report_command(parsed_arguments, data_file)
    if parsed_arguments.command == "summary":
        return _run_summary_command(parsed_arguments, data_file)

    run_menu(data_file)
    return 0


def _run_add_command(arguments: Namespace, data_file: Path) -> int:
    """Add an expense from command arguments."""
    try:
        expense = Expense(
            amount=parse_amount(arguments.amount),
            category=arguments.category,
            description=validate_description(arguments.description),
            expense_date=parse_expense_date(arguments.date),
            expense_id=str(uuid4()),
        )
        expenses = load_expenses(data_file)
        expenses.append(expense)
        save_expenses(expenses, data_file)
    except (ExpenseStorageError, ValueError) as exc:
        print(f"Error: {exc}")
        return 1

    LOGGER.info("Expense added from command.", extra={"category": expense.category})
    print(f"Added ${expense.amount} for {expense.category}.")
    return 0


def _run_budget_command(arguments: Namespace, data_file: Path) -> int:
    """Run a budget subcommand."""
    if arguments.budget_action == "set":
        return _run_budget_set_command(arguments, data_file)
    if arguments.budget_action == "list":
        return _run_budget_list_command(arguments, data_file)

    print("Error: Choose a budget action: set or list.")
    return 1


def _run_budget_set_command(arguments: Namespace, data_file: Path) -> int:
    """Set a monthly category budget."""
    budget_file = get_budget_file_path(data_file)
    try:
        month = validate_month(arguments.month)
        category = validate_category(arguments.category)
        amount = parse_amount(arguments.amount)
        budgets = load_budgets(budget_file)
        updated_budgets = set_monthly_budget(budgets, month, category, amount)
        save_budgets(updated_budgets, budget_file)
    except (BudgetStorageError, ValueError) as exc:
        print(f"Error: {exc}")
        return 1

    print(f"Set {category} budget for {month} to ${amount}.")
    return 0


def _run_budget_list_command(arguments: Namespace, data_file: Path) -> int:
    """List monthly category budgets."""
    budget_file = get_budget_file_path(data_file)
    try:
        month = validate_month(arguments.month)
        budgets = get_monthly_budgets(load_budgets(budget_file), month)
    except (BudgetStorageError, ValueError) as exc:
        print(f"Error: {exc}")
        return 1

    _print_budgets(month, budgets)
    return 0


def _run_recurring_command(arguments: Namespace, data_file: Path) -> int:
    """Run a recurring template subcommand."""
    if arguments.recurring_action == "add":
        return _run_recurring_add_command(arguments, data_file)
    if arguments.recurring_action == "list":
        return _run_recurring_list_command(data_file)
    if arguments.recurring_action == "apply":
        return _run_recurring_apply_command(arguments, data_file)

    print("Error: Choose a recurring action: add, list, or apply.")
    return 1


def _run_recurring_add_command(arguments: Namespace, data_file: Path) -> int:
    """Create a recurring expense template."""
    template_file = get_recurring_file_path(data_file)
    try:
        template = RecurringTemplate(
            amount=parse_amount(arguments.amount),
            category=validate_category(arguments.category),
            description=validate_description(arguments.description),
            day=_parse_recurring_day(arguments.day),
            template_id=str(uuid4()),
        )
        templates = load_recurring_templates(template_file)
        templates.append(template)
        save_recurring_templates(templates, template_file)
    except (RecurringTemplateStorageError, ValueError) as exc:
        print(f"Error: {exc}")
        return 1

    print(f"Created recurring template {template.template_id}.")
    return 0


def _run_recurring_list_command(data_file: Path) -> int:
    """List recurring expense templates."""
    template_file = get_recurring_file_path(data_file)
    try:
        templates = load_recurring_templates(template_file)
    except RecurringTemplateStorageError as exc:
        print(f"Error: {exc}")
        return 1

    _print_recurring_templates(templates)
    return 0


def _run_recurring_apply_command(arguments: Namespace, data_file: Path) -> int:
    """Create expenses from recurring templates for a selected month."""
    template_file = get_recurring_file_path(data_file)
    try:
        month = validate_month(arguments.month)
        templates = load_recurring_templates(template_file)
        expenses = load_expenses(data_file)
        created_expenses = apply_templates_to_month(templates, month)
        save_expenses(expenses + created_expenses, data_file)
    except (RecurringTemplateStorageError, ExpenseStorageError, ValueError) as exc:
        print(f"Error: {exc}")
        return 1

    print(f"Applied {len(created_expenses)} recurring template(s) to {month}.")
    return 0


def _run_delete_command(arguments: Namespace, data_file: Path) -> int:
    """Delete an expense by its stable ID."""
    try:
        expenses = load_expenses(data_file)
        remaining_expenses = [
            expense for expense in expenses if expense.expense_id != arguments.id
        ]
        if len(remaining_expenses) == len(expenses):
            print("Error: No expense found with that ID.")
            return 1
        save_expenses(remaining_expenses, data_file)
    except ExpenseStorageError as exc:
        print(f"Error: {exc}")
        return 1

    LOGGER.info("Expense deleted from command.", extra={"expense_id": arguments.id})
    print(f"Deleted expense {arguments.id}.")
    return 0


def _run_edit_command(arguments: Namespace, data_file: Path) -> int:
    """Edit one or more fields on an existing expense."""
    if not _has_edit_fields(arguments):
        print("Error: Provide at least one field to update.")
        return 1

    try:
        expenses = load_expenses(data_file)
        updated_expenses = _replace_edited_expense(expenses, arguments)
        save_expenses(updated_expenses, data_file)
    except (ExpenseStorageError, ValueError) as exc:
        print(f"Error: {exc}")
        return 1

    LOGGER.info("Expense edited from command.", extra={"expense_id": arguments.id})
    print(f"Updated expense {arguments.id}.")
    return 0


def _run_export_command(arguments: Namespace, data_file: Path) -> int:
    """Export saved expenses to a CSV file."""
    try:
        month = validate_month(arguments.month) if arguments.month else None
        expenses = load_expenses(data_file)
        filtered_expenses = _filter_expenses_by_month(expenses, month)
        export_expenses_to_csv(filtered_expenses, Path(arguments.output))
    except (ExpenseStorageError, ExpenseExportError, ValueError) as exc:
        print(f"Error: {exc}")
        return 1

    print(f"Exported {len(filtered_expenses)} expense record(s) to {arguments.output}.")
    return 0


def _run_list_command(arguments: Namespace, data_file: Path) -> int:
    """Print saved expenses, optionally filtered by month."""
    try:
        month = validate_month(arguments.month) if arguments.month else None
        expenses = load_expenses(data_file)
    except (ExpenseStorageError, ValueError) as exc:
        print(f"Error: {exc}")
        return 1

    filtered_expenses = _filter_expenses_by_month(expenses, month)
    _print_expenses(filtered_expenses, month)
    return 0


def _run_report_command(arguments: Namespace, data_file: Path) -> int:
    """Print monthly spending insights from saved expenses."""
    budget_file = get_budget_file_path(data_file)
    try:
        month = validate_month(arguments.month)
        expenses = load_expenses(data_file)
        budgets = get_monthly_budgets(load_budgets(budget_file), month)
    except (ExpenseStorageError, BudgetStorageError, ValueError) as exc:
        print(f"Error: {exc}")
        return 1

    _print_monthly_report(build_monthly_summary(expenses, month), budgets)
    return 0


def _run_summary_command(arguments: Namespace, data_file: Path) -> int:
    """Print a monthly summary from command arguments."""
    try:
        month = validate_month(arguments.month)
        expenses = load_expenses(data_file)
    except (ExpenseStorageError, ValueError) as exc:
        print(f"Error: {exc}")
        return 1

    _print_command_summary(build_monthly_summary(expenses, month))
    return 0


def _has_edit_fields(arguments: Namespace) -> bool:
    """Return whether the edit command includes at least one field update."""
    return any(
        value is not None
        for value in (
            arguments.amount,
            arguments.category,
            arguments.description,
            arguments.date,
        )
    )


def _replace_edited_expense(expenses: list[Expense], arguments: Namespace) -> list[Expense]:
    """Return expenses with the matching record replaced by edited data."""
    updated_expenses: list[Expense] = []
    found_expense = False

    for expense in expenses:
        if expense.expense_id != arguments.id:
            updated_expenses.append(expense)
            continue

        updated_expenses.append(_build_edited_expense(expense, arguments))
        found_expense = True

    if not found_expense:
        raise ValueError("No expense found with that ID.")

    return updated_expenses


def _build_edited_expense(expense: Expense, arguments: Namespace) -> Expense:
    """Build an edited expense while preserving unspecified fields."""
    return Expense(
        amount=(
            parse_amount(arguments.amount)
            if arguments.amount is not None
            else expense.amount
        ),
        category=(
            arguments.category if arguments.category is not None else expense.category
        ),
        description=(
            validate_description(arguments.description)
            if arguments.description is not None
            else expense.description
        ),
        expense_date=(
            parse_expense_date(arguments.date)
            if arguments.date is not None
            else expense.expense_date
        ),
        expense_id=expense.expense_id,
    )


def _filter_expenses_by_month(expenses: list[Expense], month: str | None) -> list[Expense]:
    """Return expenses for the selected month, or all expenses when omitted."""
    if month is None:
        return expenses
    return [expense for expense in expenses if expense.month == month]


def _parse_recurring_day(raw_day: str) -> int:
    """Validate and return a recurring template day of month."""
    if not raw_day.strip().isdigit():
        raise ValueError("Recurring day must be a number from 1 to 31.")

    day = int(raw_day)
    if day < MIN_RECURRING_DAY or day > MAX_RECURRING_DAY:
        raise ValueError("Recurring day must be between 1 and 31.")
    return day


def _print_expenses(expenses: list[Expense], month: str | None) -> None:
    """Print expense records in a readable table-like format."""
    title = f"Expenses for {month}" if month else "All expenses"
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


def _print_command_summary(summary: MonthlySummary) -> None:
    """Print a command-friendly monthly summary."""
    print(f"Summary for {summary.month}")
    if not summary.category_totals:
        print("No expenses recorded for this month.")
        return

    for category, amount in summary.category_totals.items():
        print(f"{category}: ${amount}")
    print(f"Total: ${summary.total}")


def _print_budgets(month: str, budgets: dict[str, Decimal]) -> None:
    """Print monthly category budgets."""
    print(f"Budgets for {month}")
    if not budgets:
        print("No budgets set for this month.")
        return

    for category, amount in sorted(budgets.items()):
        print(f"{category}: ${amount}")


def _print_recurring_templates(templates: list[RecurringTemplate]) -> None:
    """Print recurring expense templates."""
    print("Recurring templates")
    if not templates:
        print("No recurring templates saved.")
        return

    for template in sorted(templates, key=lambda item: item.day):
        print(
            f"{template.template_id} | "
            f"day {template.day} | "
            f"{template.category} | "
            f"${template.amount} | "
            f"{template.description}"
        )


def _print_monthly_report(
    summary: MonthlySummary,
    budgets: dict[str, Decimal] | None = None,
) -> None:
    """Print monthly spending insights for portfolio-friendly reporting."""
    print(f"Report for {summary.month}")
    if summary.transaction_count == 0:
        print("No expenses recorded for this month.")

    print(f"Total spent: ${summary.total}")
    print(f"Transactions: {summary.transaction_count}")
    print(f"Average expense: ${summary.average_expense}")
    print(f"Top category: {summary.top_category}")
    print("Category breakdown:")
    for category, amount in summary.category_totals.items():
        print(f"- {category}: ${amount}")

    if budgets:
        print("Budget comparison:")
        compared_categories = sorted(set(budgets) | set(summary.category_totals))
        for category in compared_categories:
            budget_amount = budgets.get(category)
            spent_amount = summary.category_totals.get(category, Decimal("0.00"))
            if budget_amount is None:
                print(f"- {category}: no budget set, spent ${spent_amount}")
                continue
            remaining_amount = budget_amount - spent_amount
            print(
                f"- {category}: budget ${budget_amount}, "
                f"spent ${spent_amount}, "
                f"remaining ${remaining_amount}"
            )
