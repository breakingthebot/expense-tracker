# tests/test_validators.py
# Tests input validation helpers for amounts, categories, descriptions, and months.
# Connects to: src/expense_tracker/utils/validators.py
# Created: 2026-06-06

from decimal import Decimal
import unittest

from src.expense_tracker.utils.validators import (
    parse_amount,
    validate_category,
    validate_description,
    validate_month,
)


class ValidatorTests(unittest.TestCase):
    """Verify user input validation behavior."""

    def test_parse_amount_accepts_currency_formatting(self) -> None:
        """Amounts may include dollar signs and comma separators."""
        self.assertEqual(parse_amount("$1,234.567"), Decimal("1234.57"))

    def test_parse_amount_rejects_zero(self) -> None:
        """Amounts must be greater than zero."""
        with self.assertRaises(ValueError):
            parse_amount("0")

    def test_validate_category_accepts_known_category(self) -> None:
        """Known categories are returned after whitespace trimming."""
        self.assertEqual(validate_category(" Food "), "Food")

    def test_validate_description_rejects_blank_text(self) -> None:
        """Blank descriptions should not be saved."""
        with self.assertRaises(ValueError):
            validate_description("   ")

    def test_validate_month_rejects_invalid_month_number(self) -> None:
        """Month validation catches impossible month numbers."""
        with self.assertRaises(ValueError):
            validate_month("2026-13")


if __name__ == "__main__":
    unittest.main()
