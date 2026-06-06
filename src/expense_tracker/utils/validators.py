# src/expense_tracker/utils/validators.py
# Validates and normalizes user input before records are saved.
# Connects to: src/expense_tracker/cli/menu.py, src/expense_tracker/models/expense.py
# Created: 2026-06-06

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

CENTS = Decimal("0.01")
MAX_DESCRIPTION_LENGTH = 120
VALID_CATEGORIES = (
    "Food",
    "Housing",
    "Transportation",
    "Entertainment",
    "Utilities",
    "Healthcare",
    "Savings",
    "Miscellaneous",
)


def parse_amount(raw_amount: str) -> Decimal:
    """Validate an amount string and return a positive two-decimal Decimal."""
    normalized_amount = raw_amount.replace("$", "").replace(",", "").strip()
    try:
        amount = Decimal(normalized_amount)
    except InvalidOperation as exc:
        raise ValueError("Amount must be a valid number.") from exc

    if amount <= Decimal("0"):
        raise ValueError("Amount must be greater than zero.")

    return amount.quantize(CENTS, rounding=ROUND_HALF_UP)


def validate_category(category: str) -> str:
    """Validate that a category is one of the supported expense categories."""
    normalized_category = category.strip()
    if normalized_category not in VALID_CATEGORIES:
        raise ValueError("Category must be selected from the available list.")
    return normalized_category


def validate_description(description: str) -> str:
    """Validate and normalize a short expense description."""
    normalized_description = description.strip()
    if not normalized_description:
        raise ValueError("Description is required.")
    if len(normalized_description) > MAX_DESCRIPTION_LENGTH:
        raise ValueError(
            f"Description must be {MAX_DESCRIPTION_LENGTH} characters or fewer."
        )
    return normalized_description


def validate_month(raw_month: str) -> str:
    """Validate a summary month in YYYY-MM format."""
    normalized_month = raw_month.strip()
    parts = normalized_month.split("-")
    if len(parts) != 2:
        raise ValueError("Month must use YYYY-MM format.")

    year, month = parts
    if len(year) != 4 or len(month) != 2 or not year.isdigit() or not month.isdigit():
        raise ValueError("Month must use YYYY-MM format.")

    month_number = int(month)
    if month_number < 1 or month_number > 12:
        raise ValueError("Month must be between 01 and 12.")

    return normalized_month
