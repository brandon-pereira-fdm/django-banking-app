from decimal import Decimal
from uuid import UUID

from django.test import TestCase

from banking.models import CompletedTransaction
from banking.services import deposit
from .helpers import make_personal, make_user


class CompletedTransactionModelTests(TestCase):
    def test_uuid_and_completed_status(self):
        user = make_user()
        account = make_personal(user, "91234567")
        tx = deposit(user, account, Decimal("10.00"))
        self.assertIsInstance(tx.transaction_id, UUID)
        self.assertEqual(tx.status, CompletedTransaction.COMPLETED)
        self.assertEqual(tx.currency, "SGD")
