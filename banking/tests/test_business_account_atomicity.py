from decimal import Decimal

from django.test import TestCase

from banking.models import BankAccount, CompletedTransaction
from banking.services import BankingError, create_business_account, create_personal_account
from .helpers import make_user


class BusinessAccountAtomicityTests(TestCase):
    def test_low_opening_deposit_creates_no_business_or_transaction(self):
        user = make_user()
        create_personal_account(user, "91234567")
        with self.assertRaises(BankingError):
            create_business_account(user, "Low", "202612345A", Decimal("6999.99"))
        self.assertFalse(BankAccount.objects.filter(account_type=BankAccount.BUSINESS).exists())
        self.assertFalse(CompletedTransaction.objects.exists())
