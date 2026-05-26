from decimal import Decimal

from django.test import TestCase

from banking.models import ApprovalRequest, CompletedTransaction
from banking.services import BankingError, cancel_request, request_business_withdrawal
from .helpers import make_business, make_user


class BusinessWithdrawalRequestTests(TestCase):
    def test_pending_request_no_balance_movement_or_completed_transaction(self):
        personal, business, opening = make_business(make_user())
        approval = request_business_withdrawal(business.owner, business, Decimal("100.00"))
        business.refresh_from_db()
        self.assertEqual(approval.status, ApprovalRequest.PENDING)
        self.assertEqual(business.balance, Decimal("7000.00"))
        self.assertEqual(CompletedTransaction.objects.exclude(pk=opening.pk).count(), 0)

    def test_cancel_pending_and_terminal_not_actionable(self):
        personal, business, opening = make_business(make_user())
        approval = request_business_withdrawal(business.owner, business, Decimal("100.00"))
        cancel_request(approval, business.owner)
        approval.refresh_from_db()
        self.assertEqual(approval.status, ApprovalRequest.CANCELLED)
        with self.assertRaises(BankingError):
            cancel_request(approval, business.owner)
