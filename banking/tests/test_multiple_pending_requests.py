from decimal import Decimal

from django.test import TestCase

from banking.models import ApprovalRequest, CompletedTransaction
from banking.services import approve_request, request_business_withdrawal
from .helpers import make_business, make_user


class MultiplePendingTests(TestCase):
    def test_multiple_pending_no_reservation_and_later_6999_99_failure(self):
        user = make_user()
        personal, business, opening = make_business(user, opening=Decimal("8500.00"))
        first = request_business_withdrawal(user, business, Decimal("1000.00"))
        second = request_business_withdrawal(user, business, Decimal("500.01"))
        business.refresh_from_db()
        self.assertEqual(ApprovalRequest.objects.filter(status=ApprovalRequest.PENDING).count(), 2)
        self.assertEqual(business.balance, Decimal("8500.00"))

        approve_request(first, user)
        first.refresh_from_db()
        business.refresh_from_db()
        self.assertEqual(first.status, ApprovalRequest.COMPLETED)
        self.assertEqual(business.balance, Decimal("7500.00"))

        approve_request(second, user)
        second.refresh_from_db()
        business.refresh_from_db()
        self.assertEqual(second.status, ApprovalRequest.FAILED)
        self.assertEqual(business.balance, Decimal("7500.00"))
        self.assertEqual(CompletedTransaction.objects.filter(transaction_type=CompletedTransaction.WITHDRAWAL).count(), 1)
