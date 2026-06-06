# src/expense_tracker/cli/menu.py
# Coordinates the questionnaire-style menu for the expense tracker.
# Connects to: src/expense_tracker/cli/prompts.py, src/expense_tracker/cli/display.py
# Created: 2026-06-06

import logging
from pathlib import Path
from uuid import uuid4

from src.expense_tracker.cli.display import print_expenses, print_report, print_summary
from src.expense_tracker.cli.prompts import (
    prompt_for_amount,
    prompt_for_category,
    prompt_for_description,
    prompt_for_expense_date,
    prompt_for_expense_updates,
    prompt_for_month,
    prompt_for_optional_month,
    prompt_for_output_path,
)
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
from src.expense_tracker.services.summary import build_monthly_summary

LOGGER = logging.getLogger(__name__)
MENU_ADD_EXPENSE = "1"
MENU_LIST_EXPENSES = "2"
MENU_EDIT_EXPENSE = "3"
MENU_DELETE_EXPENSE = "4"
MENU_VIEW_SUMMARY = "5"
MENU_VIEW_REPORT = "6"
MENU_EXPORT_CSV = "7"
MENU_SET_BUDGET = "8"
MENU_LIST_BUDGETS = "9"
MENU_ADD_RECURRING = "10"
MENU_LIST_RECURRING = "11"
MENU_APPLY_RECURRING = "12"
MENU_EXIT = "13"


def run_menu(data_file: Path) -> None:
    """Run the interactive CLI menu until the user exits."""
    try:
        expenses = load_expenses(data_file)
    except ExpenseStorageError as exc:
        print(f"Error: {exc}")
        return

    print("Expense Tracker CLI")
    print("Answer the prompts to manage expenses without memorizing commands.")

    while True:
        _print_menu_options()
        choice = input("Select an option: ").strip()
        if choice == MENU_ADD_EXPENSE:
            _handle_add_expense(expenses, data_file)
        elif choice == MENU_LIST_EXPENSES:
            _handle_list_expenses(expenses)
        elif choice == MENU_EDIT_EXPENSE:
            _handle_edit_expense(expenses, data_file)
        elif choice == MENU_DELETE_EXPENSE:
            _handle_delete_expense(expenses, data_file)
        elif choice == MENU_VIEW_SUMMARY:
            _handle_monthly_summary(expenses)
        elif choice == MENU_VIEW_REPORT:
            _handle_monthly_report(expenses, data_file)
        elif choice == MENU_EXPORT_CSV:
            _handle_csv_export(expenses)
        elif choice == MENU_SET_BUDGET:
            _handle_set_budget(data_file)
        elif choice == MENU_LIST_BUDGETS:
            _handle_list_budgets(data_file)
        elif choice == MENU_ADD_RECURRING:
            _handle_add_recurring_template(data_file)
        elif choice == MENU_LIST_RECURRING:
            _handle_list_recurring_templates(data_file)
        elif choice == MENU_APPLY_RECURRING:
            _handle_apply_recurring_templates(expenses, data_file)
        elif choice == MENU_EXIT:
            print("Goodbye.")
            return
        else:
            print("Please choose a number from 1 to 13.")


def _print_menu_options() -> None:
    """Print the available questionnaire menu actions."""
    print("\n1. Add expense")
    print("2. List expenses")
    print("3. Edit expense")
    print("4. Delete expense")
    print("5. View monthly summary")
    print("6. View monthly report")
    print("7. Export CSV")
    print("8. Set budget")
    print("9. List budgets")
    print("10. Add recurring template")
    print("11. List recurring templates")
    print("12. Apply recurring templates")
    print("13. Exit")


def _handle_add_expense(expenses: list[Expense], data_file: Path) -> None:
    """Prompt for a new expense, validate it, and save it."""
    expense = Expense(
        amount=prompt_for_amount(),
        category=prompt_for_category(),
        description=prompt_for_description(),
        expense_date=prompt_for_expense_date(),
        expense_id=str(uuid4()),
    )
    expenses.append(expense)

    try:
        save_expenses(expenses, data_file)
    except ExpenseStorageError as exc:
        expenses.pop()
        print(f"Error: {exc}")
        return

    LOGGER.info(
        "Expense added.",
        extra={"category": expense.category, "month": expense.month},
    )
    print(f"Added ${expense.amount} for {expense.category}.")


def _handle_list_expenses(expenses: list[Expense]) -> None:
    """Prompt for an optional month and list matching expenses."""
    month = prompt_for_optional_month("Month to list, or leave blank for all")
    print_expenses(_filter_expenses_by_month(expenses, month), month)


def _handle_edit_expense(expenses: list[Expense], data_file: Path) -> None:
    """Prompt for expense updates and save the edited record."""
    if not expenses:
        print("No expenses available to edit.")
        return

    print_expenses(expenses, None)
    expense_id = input("Expense ID to edit: ").strip()
    existing_expense = _find_expense_by_id(expenses, expense_id)
    if existing_expense is None:
        print("Error: No expense found with that ID.")
        return

    print("Leave a field blank to keep its current value.")
    edited_expense = prompt_for_expense_updates(existing_expense)
    updated_expenses = [
        edited_expense if expense.expense_id == expense_id else expense
        for expense in expenses
    ]

    if _save_replacement_expenses(expenses, updated_expenses, data_file):
        print(f"Updated expense {expense_id}.")


def _handle_delete_expense(expenses: list[Expense], data_file: Path) -> None:
    """Prompt for an expense ID and delete the matching record."""
    if not expenses:
        print("No expenses available to delete.")
        return

    print_expenses(expenses, None)
    expense_id = input("Expense ID to delete: ").strip()
    remaining_expenses = [
        expense for expense in expenses if expense.expense_id != expense_id
    ]
    if len(remaining_expenses) == len(expenses):
        print("Error: No expense found with that ID.")
        return

    if _save_replacement_expenses(expenses, remaining_expenses, data_file):
        print(f"Deleted expense {expense_id}.")


def _handle_monthly_summary(expenses: list[Expense]) -> None:
    """Prompt for a month and display its summary totals."""
    month = prompt_for_month("Month to summarize")
    print_summary(build_monthly_summary(expenses, month))


def _handle_monthly_report(expenses: list[Expense], data_file: Path) -> None:
    """Prompt for a month and display richer spending insights."""
    month = prompt_for_month("Month to report")
    try:
        budgets = get_monthly_budgets(
            load_budgets(get_budget_file_path(data_file)),
            month,
        )
    except BudgetStorageError:
        budgets = {}

    print_report(build_monthly_summary(expenses, month), budgets)


def _handle_csv_export(expenses: list[Expense]) -> None:
    """Prompt for export options and write matching expenses to CSV."""
    month = prompt_for_optional_month("Month to export, or leave blank for all")
    output_path = prompt_for_output_path()
    filtered_expenses = _filter_expenses_by_month(expenses, month)

    try:
        export_expenses_to_csv(filtered_expenses, output_path)
    except ExpenseExportError as exc:
        print(f"Error: {exc}")
        return

    print(f"Exported {len(filtered_expenses)} expense record(s) to {output_path}.")


def _handle_set_budget(data_file: Path) -> None:
    """Prompt for a monthly category budget and save it."""
    budget_file = get_budget_file_path(data_file)
    month = prompt_for_month("Budget month")
    category = prompt_for_category()
    amount = prompt_for_amount()

    try:
        budgets = load_budgets(budget_file)
        updated_budgets = set_monthly_budget(budgets, month, category, amount)
        save_budgets(updated_budgets, budget_file)
    except BudgetStorageError as exc:
        print(f"Error: {exc}")
        return

    print(f"Set {category} budget for {month} to ${amount}.")


def _handle_list_budgets(data_file: Path) -> None:
    """Prompt for a month and list matching budgets."""
    budget_file = get_budget_file_path(data_file)
    month = prompt_for_month("Budget month")

    try:
        budgets = get_monthly_budgets(load_budgets(budget_file), month)
    except BudgetStorageError as exc:
        print(f"Error: {exc}")
        return

    print(f"\nBudgets for {month}")
    if not budgets:
        print("No budgets set for this month.")
        return
    for category, amount in sorted(budgets.items()):
        print(f"{category}: ${amount}")


def _handle_add_recurring_template(data_file: Path) -> None:
    """Prompt for a recurring template and save it."""
    template_file = get_recurring_file_path(data_file)
    template = RecurringTemplate(
        amount=prompt_for_amount(),
        category=prompt_for_category(),
        description=prompt_for_description(),
        day=_prompt_for_recurring_day(),
        template_id=str(uuid4()),
    )

    try:
        templates = load_recurring_templates(template_file)
        templates.append(template)
        save_recurring_templates(templates, template_file)
    except RecurringTemplateStorageError as exc:
        print(f"Error: {exc}")
        return

    print(f"Created recurring template {template.template_id}.")


def _handle_list_recurring_templates(data_file: Path) -> None:
    """List saved recurring templates."""
    try:
        templates = load_recurring_templates(get_recurring_file_path(data_file))
    except RecurringTemplateStorageError as exc:
        print(f"Error: {exc}")
        return

    _print_recurring_templates(templates)


def _handle_apply_recurring_templates(
    expenses: list[Expense],
    data_file: Path,
) -> None:
    """Prompt for a month and create expenses from recurring templates."""
    month = prompt_for_month("Month to apply templates")
    try:
        templates = load_recurring_templates(get_recurring_file_path(data_file))
        created_expenses = apply_templates_to_month(templates, month)
        save_expenses(expenses + created_expenses, data_file)
    except (RecurringTemplateStorageError, ExpenseStorageError) as exc:
        print(f"Error: {exc}")
        return

    expenses.extend(created_expenses)
    print(f"Applied {len(created_expenses)} recurring template(s) to {month}.")


def _save_replacement_expenses(
    current_expenses: list[Expense],
    replacement_expenses: list[Expense],
    data_file: Path,
) -> bool:
    """Save replacement expenses and update the in-memory menu list."""
    try:
        save_expenses(replacement_expenses, data_file)
    except ExpenseStorageError as exc:
        print(f"Error: {exc}")
        return False

    current_expenses[:] = replacement_expenses
    return True


def _find_expense_by_id(expenses: list[Expense], expense_id: str) -> Expense | None:
    """Return the expense matching an ID, if present."""
    for expense in expenses:
        if expense.expense_id == expense_id:
            return expense
    return None


def _filter_expenses_by_month(expenses: list[Expense], month: str | None) -> list[Expense]:
    """Return expenses for the selected month, or all expenses when omitted."""
    if month is None:
        return expenses
    return [expense for expense in expenses if expense.month == month]


def _prompt_for_recurring_day() -> int:
    """Prompt until the user enters a valid recurring day of month."""
    while True:
        raw_day = input("Day of month [1-31]: ").strip()
        if not raw_day.isdigit():
            print("Error: Recurring day must be a number from 1 to 31.")
            continue

        day = int(raw_day)
        if day < 1 or day > 31:
            print("Error: Recurring day must be between 1 and 31.")
            continue
        return day


def _print_recurring_templates(templates: list[RecurringTemplate]) -> None:
    """Print recurring expense templates."""
    print("\nRecurring templates")
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
