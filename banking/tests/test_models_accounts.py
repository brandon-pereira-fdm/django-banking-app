from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from banking.models import BankAccount
from .helpers import make_business, make_personal, make_user


class AccountModelTests(TestCase):
    def test_account_type_constraints_and_uniqueness(self):
        user = make_user()
        personal = make_personal(user, "91234567")
        with self.assertRaises(Exception):
            make_personal(user, "92345678")
        _, business, _ = make_business(user, "92345678", "202612345A")
        self.assertEqual(business.authorised_personal_account, personal)
        invalid = BankAccount(owner=user, account_type=BankAccount.PERSONAL, balance=Decimal("0.00"))
        with self.assertRaises(ValidationError):
            invalid.full_clean()
