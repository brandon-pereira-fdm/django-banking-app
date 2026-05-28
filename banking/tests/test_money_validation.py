from decimal import Decimal

from django.test import TestCase

from banking.services import ValidationBankingError
from banking.services.money import format_sgd, validate_sgd_amount


class MoneyValidationTests(TestCase):
    def test_valid_decimal_and_formatting(self):
        self.assertEqual(validate_sgd_amount("1,234.50"), Decimal("1234.50"))
        self.assertEqual(format_sgd(Decimal("0")), "SGD 0.00")

    def test_invalid_amounts_rejected(self):
        for value in ["0", "-1.00", "abc", "1.001"]:
            with self.subTest(value=value):
                with self.assertRaises(ValidationBankingError):
                    validate_sgd_amount(value)
