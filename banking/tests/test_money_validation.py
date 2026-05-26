from decimal import Decimal

from django.test import TestCase

from banking.services import BankingError, MIN_BUSINESS_BALANCE, format_sgd, validate_sgd_amount


class MoneyValidationTests(TestCase):
    def test_valid_amount_and_display(self):
        self.assertEqual(validate_sgd_amount("SGD 105.50"), Decimal("105.50"))
        self.assertEqual(format_sgd(Decimal("7000")), "SGD 7,000.00")

    def test_reject_zero_negative_malformed_and_excess_precision(self):
        for value in ["0", "-1.00", "text", "10.123", ""]:
            with self.assertRaises(BankingError):
                validate_sgd_amount(value)

    def test_retained_minimum_boundaries_are_explicit(self):
        self.assertEqual(MIN_BUSINESS_BALANCE, Decimal("7000.00"))
        self.assertTrue(Decimal("7000.00") >= MIN_BUSINESS_BALANCE)
        self.assertFalse(Decimal("6999.99") >= MIN_BUSINESS_BALANCE)
