from decimal import Decimal

from django.test import TestCase

from banking.models import CompletedTransaction
from banking.services import BankingError, withdraw_personal
from .helpers import make_personal, make_user


class PersonalWithdrawalTests(TestCase):
    def test_valid_and_full_balance_withdrawal(self):
        user = make_user()
        account = make_personal(user, "91234567", Decimal("100.00"))
        tx = withdraw_personal(user, account, Decimal("40.00"))
        account.refresh_from_db()
        self.assertEqual(account.balance, Decimal("60.00"))
        self.assertEqual(tx.transaction_type, CompletedTransaction.WITHDRAWAL)
        withdraw_personal(user, account, Decimal("60.00"))
        account.refresh_from_db()
        self.assertEqual(account.balance, Decimal("0.00"))

    def test_overdraft_and_invalid_amount_rejected_without_transaction(self):
        user = make_user()
        account = make_personal(user, "91234567", Decimal("10.00"))
        existing = CompletedTransaction.objects.count()
        with self.assertRaises(BankingError):
            withdraw_personal(user, account, Decimal("10.01"))
        with self.assertRaises(BankingError):
            withdraw_personal(user, account, "0")
        account.refresh_from_db()
        self.assertEqual(account.balance, Decimal("10.00"))
        self.assertEqual(CompletedTransaction.objects.count(), existing)
