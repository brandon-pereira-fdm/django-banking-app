from decimal import Decimal

from django.test import TestCase

from banking.models import ApprovalRequest, CompletedTransaction, TransferOperation
from banking.services import request_business_transfer
from .helpers import make_business, make_personal, make_user


class BusinessTransferRequestTests(TestCase):
    def test_pending_business_transfer_moves_no_money_and_creates_no_completed_records(self):
        personal, business, opening = make_business(make_user())
        recipient = make_personal(make_user("p@example.com", "P"), "92345678")
        approval = request_business_transfer(business.owner, business, "PERSONAL", "92345678", Decimal("100.00"))
        business.refresh_from_db()
        recipient.refresh_from_db()
        self.assertEqual(approval.status, ApprovalRequest.PENDING)
        self.assertEqual(business.balance, Decimal("7000.00"))
        self.assertEqual(recipient.balance, Decimal("0.00"))
        self.assertFalse(TransferOperation.objects.exists())
        self.assertEqual(CompletedTransaction.objects.exclude(pk=opening.pk).count(), 0)

    def test_business_to_business_pending_request(self):
        personal, business, opening = make_business(make_user())
        _, recipient_business, _ = make_business(make_user("b2@example.com", "B2"), "93456789", "202612346B")
        approval = request_business_transfer(business.owner, business, "BUSINESS", "202612346B", Decimal("100.00"))
        self.assertEqual(approval.recipient_account, recipient_business)
        self.assertEqual(approval.status, ApprovalRequest.PENDING)
