from decimal import Decimal

from django.test import TestCase

from banking.models import BankAccount
from banking.services import BankingError, create_personal_account
from .helpers import make_user


class PersonalAccountTests(TestCase):
    def test_create_personal_account_starts_at_zero_without_opening_deposit(self):
        user = make_user()
        account = create_personal_account(user, "9123 4567")
        self.assertEqual(account.account_type, BankAccount.PERSONAL)
        self.assertEqual(account.balance, Decimal("0.00"))
        self.assertEqual(account.phone_number, "91234567")
        self.assertEqual(account.transactions.count(), 0)

    def test_duplicate_personal_account_and_duplicate_phone_rejected(self):
        user = make_user()
        create_personal_account(user, "91234567")
        with self.assertRaises(BankingError):
            create_personal_account(user, "92345678")
        other = make_user("other@example.com", "Other")
        with self.assertRaises(BankingError):
            create_personal_account(other, "9123-4567")
