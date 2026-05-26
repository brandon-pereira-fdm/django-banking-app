from decimal import Decimal

from django.test import TestCase

from banking.models import CompletedTransaction
from banking.services import BankingError, deposit
from .helpers import make_business, make_personal, make_user


class DepositTests(TestCase):
    def test_personal_and_business_deposits_create_transactions(self):
        user = make_user()
        personal = make_personal(user, "91234567")
        tx = deposit(user, personal, Decimal("25.50"))
        personal.refresh_from_db()
        self.assertEqual(personal.balance, Decimal("25.50"))
        self.assertEqual(tx.transaction_type, CompletedTransaction.DEPOSIT)

        _, business, _ = make_business(make_user("biz@example.com", "Biz"), "92345678", "202612345A")
        tx2 = deposit(business.owner, business, Decimal("10.00"))
        business.refresh_from_db()
        self.assertEqual(business.balance, Decimal("7010.00"))
        self.assertEqual(tx2.transaction_type, CompletedTransaction.DEPOSIT)

    def test_invalid_deposit_changes_nothing(self):
        user = make_user()
        account = make_personal(user, "91234567")
        for amount in ["0", "-1.00", "10.123"]:
            with self.assertRaises(BankingError):
                deposit(user, account, amount)
        account.refresh_from_db()
        self.assertEqual(account.balance, Decimal("0.00"))
        self.assertEqual(CompletedTransaction.objects.count(), 0)
