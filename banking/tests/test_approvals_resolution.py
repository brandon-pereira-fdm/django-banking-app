from decimal import Decimal

from django.test import TestCase

from banking.models import ApprovalRequest, CompletedTransaction, TransferOperation
from banking.services import PermissionDeniedError, approve_request, reject_request, request_business_transfer, request_business_withdrawal
from .helpers import make_business, make_personal, make_user


class ApprovalResolutionTests(TestCase):
    def test_valid_withdrawal_and_transfer_can_leave_exactly_7000(self):
        user = make_user()
        personal, business, opening = make_business(user, opening=Decimal("8000.00"))
        withdrawal = request_business_withdrawal(user, business, Decimal("1000.00"))
        approve_request(withdrawal, user)
        withdrawal.refresh_from_db()
        business.refresh_from_db()
        self.assertEqual(withdrawal.status, ApprovalRequest.COMPLETED)
        self.assertEqual(business.balance, Decimal("7000.00"))
        self.assertTrue(CompletedTransaction.objects.filter(transaction_type=CompletedTransaction.WITHDRAWAL, approval_request=withdrawal).exists())

        user2 = make_user("two@example.com", "Two")
        personal2, business2, opening2 = make_business(user2, "92345678", "202612346B", Decimal("8000.00"))
        recipient = make_personal(make_user("r@example.com", "Recipient"), "93456789")
        approval = request_business_transfer(user2, business2, "PERSONAL", "93456789", Decimal("1000.00"))
        approve_request(approval, user2)
        approval.refresh_from_db()
        business2.refresh_from_db()
        recipient.refresh_from_db()
        self.assertEqual(approval.status, ApprovalRequest.COMPLETED)
        self.assertEqual(business2.balance, Decimal("7000.00"))
        self.assertEqual(recipient.balance, Decimal("1000.00"))
        self.assertTrue(TransferOperation.objects.filter(approval_requests=approval).exists())

    def test_6999_99_boundary_fails_without_movement_or_completed_records(self):
        user = make_user()
        personal, business, opening = make_business(user, opening=Decimal("8000.00"))
        withdrawal = request_business_withdrawal(user, business, Decimal("1000.01"))
        approve_request(withdrawal, user)
        withdrawal.refresh_from_db()
        business.refresh_from_db()
        self.assertEqual(withdrawal.status, ApprovalRequest.FAILED)
        self.assertEqual(business.balance, Decimal("8000.00"))
        self.assertFalse(CompletedTransaction.objects.filter(transaction_type=CompletedTransaction.WITHDRAWAL, approval_request=withdrawal).exists())

        user2 = make_user("two@example.com", "Two")
        personal2, business2, opening2 = make_business(user2, "92345678", "202612346B", Decimal("8000.00"))
        recipient = make_personal(make_user("r@example.com", "Recipient"), "93456789")
        approval = request_business_transfer(user2, business2, "PERSONAL", "93456789", Decimal("1000.01"))
        approve_request(approval, user2)
        approval.refresh_from_db()
        business2.refresh_from_db()
        recipient.refresh_from_db()
        self.assertEqual(approval.status, ApprovalRequest.FAILED)
        self.assertEqual(business2.balance, Decimal("8000.00"))
        self.assertEqual(recipient.balance, Decimal("0.00"))
        self.assertFalse(TransferOperation.objects.filter(approval_requests=approval).exists())
        self.assertFalse(CompletedTransaction.objects.filter(approval_request=approval).exists())

    def test_unauthorised_reject_and_no_approved_status(self):
        user = make_user()
        personal, business, opening = make_business(user, opening=Decimal("8000.00"))
        approval = request_business_withdrawal(user, business, Decimal("100.00"))
        other = make_user("other@example.com", "Other")
        with self.assertRaises(PermissionDeniedError):
            approve_request(approval, other)
        reject_request(approval, user)
        approval.refresh_from_db()
        self.assertEqual(approval.status, ApprovalRequest.REJECTED)
        self.assertNotIn("APPROVED", [choice[0] for choice in ApprovalRequest.STATUSES])
