from decimal import Decimal

from django.test import TestCase

from banking.models import ApprovalRequest, CompletedTransaction
from banking.services import approve_request, completed_transactions_for_user, request_business_withdrawal
from .helpers import make_business, make_personal, make_user


class HistoryTests(TestCase):
    def test_transaction_history_completed_only_and_approval_history_separate(self):
        user = make_user()
        account = make_personal(user, "91234567", Decimal("10.00"))
        self.assertTrue(completed_transactions_for_user(user).exists())
        personal, business, opening = make_business(make_user("b@example.com", "B"), "92345678", "202612345A", Decimal("8000.00"))
        approval = request_business_withdrawal(business.owner, business, Decimal("100.00"))
        self.assertFalse(CompletedTransaction.objects.filter(approval_request=approval).exists())
        approve_request(approval, business.owner)
        approval.refresh_from_db()
        self.assertEqual(approval.status, ApprovalRequest.COMPLETED)
        self.assertTrue(CompletedTransaction.objects.filter(approval_request=approval).exists())
