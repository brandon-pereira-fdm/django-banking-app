from decimal import Decimal

from django.test import TestCase

from banking.services import ValidationBankingError
from banking.services.money import MIN_BUSINESS_BALANCE, validate_sgd_amount


class MoneyValidationTests(TestCase):
    def test_valid_and_boundary_amounts(self):
        self.assertEqual(validate_sgd_amount("7000.00"), MIN_BUSINESS_BALANCE)
        self.assertEqual(validate_sgd_amount("1"), Decimal("1.00"))

    def test_rejects_invalid_amounts(self):
        for value in ["0", "-1", "abc", "1.001", "10000000000.00"]:
            with self.subTest(value=value):
                with self.assertRaises(ValidationBankingError):
                    validate_sgd_amount(value)
