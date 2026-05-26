from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from banking.services import request_business_withdrawal
from .helpers import make_business, make_user


class ApprovalViewTests(TestCase):
    def test_detail_shows_projected_balance_and_pending_actions(self):
        user = make_user()
        personal, business, opening = make_business(user, opening=Decimal("8000.00"))
        approval = request_business_withdrawal(user, business, Decimal("1000.01"))
        self.client.force_login(user)
        response = self.client.get(reverse("approval_detail", args=[approval.request_id]))
        self.assertContains(response, "SGD 6,999.99")
        self.assertContains(response, "Would fall below SGD 7,000.00")
        self.assertContains(response, "Approve")
