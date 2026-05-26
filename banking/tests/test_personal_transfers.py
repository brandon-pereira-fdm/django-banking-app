from decimal import Decimal

from django.test import TestCase

from banking.models import CompletedTransaction
from banking.services import BankingError, transfer_from_personal
from .helpers import make_business, make_personal, make_user


class PersonalTransferTests(TestCase):
    def test_personal_to_personal_and_personal_to_business_linked_records(self):
        user = make_user()
        sender = make_personal(user, "91234567", Decimal("200.00"))
        recipient = make_personal(make_user("r@example.com", "Recipient"), "92345678")
        op, debit, credit = transfer_from_personal(user, sender, "PERSONAL", "92345678", Decimal("50.00"))
        sender.refresh_from_db()
        recipient.refresh_from_db()
        self.assertEqual(sender.balance, Decimal("150.00"))
        self.assertEqual(recipient.balance, Decimal("50.00"))
        self.assertEqual(debit.transfer_operation, op)
        self.assertEqual(credit.transfer_operation, op)
        self.assertNotEqual(debit.transaction_id, credit.transaction_id)

        _, business, _ = make_business(make_user("b@example.com", "Biz"), "93456789", "202612345A")
        transfer_from_personal(user, sender, "BUSINESS", "202612345A", Decimal("150.00"))
        sender.refresh_from_db()
        business.refresh_from_db()
        self.assertEqual(sender.balance, Decimal("0.00"))
        self.assertEqual(business.balance, Decimal("7150.00"))

    def test_insufficient_funds_rolls_back(self):
        user = make_user()
        sender = make_personal(user, "91234567", Decimal("10.00"))
        recipient = make_personal(make_user("r@example.com", "Recipient"), "92345678")
        existing = CompletedTransaction.objects.count()
        with self.assertRaises(BankingError):
            transfer_from_personal(user, sender, "PERSONAL", "92345678", Decimal("10.01"))
        sender.refresh_from_db()
        recipient.refresh_from_db()
        self.assertEqual(sender.balance, Decimal("10.00"))
        self.assertEqual(recipient.balance, Decimal("0.00"))
        self.assertEqual(CompletedTransaction.objects.count(), existing)
