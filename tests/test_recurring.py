# tests/test_recurring.py
# Tests recurring expense template persistence and monthly application.
# Connects to: src/expense_tracker/services/recurring.py
# Created: 2026-06-06

from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.expense_tracker.models.recurring_template import RecurringTemplate
from src.expense_tracker.services.recurring import (
    apply_templates_to_month,
    load_recurring_templates,
    save_recurring_templates,
)


class RecurringTemplateTests(unittest.TestCase):
    """Verify recurring expense template behavior."""

    def test_save_and_load_recurring_templates_round_trip(self) -> None:
        """Saved recurring templates load back as model objects."""
        template = RecurringTemplate(
            Decimal("1200.00"),
            "Housing",
            "Rent",
            1,
            "template-1",
        )

        with TemporaryDirectory() as temporary_directory:
            template_file = Path(temporary_directory) / "recurring_templates.json"
            save_recurring_templates([template], template_file)

            loaded_templates = load_recurring_templates(template_file)

        self.assertEqual(loaded_templates, [template])

    def test_apply_templates_to_month_clamps_day_to_month_end(self) -> None:
        """Template days beyond month length use the month's final day."""
        template = RecurringTemplate(
            Decimal("15.00"),
            "Utilities",
            "Subscription",
            31,
            "template-1",
        )

        expenses = apply_templates_to_month([template], "2026-02")

        self.assertEqual(len(expenses), 1)
        self.assertEqual(expenses[0].expense_date.isoformat(), "2026-02-28")
        self.assertEqual(expenses[0].amount, Decimal("15.00"))


if __name__ == "__main__":
    unittest.main()
