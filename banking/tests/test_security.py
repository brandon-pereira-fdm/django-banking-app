from django.test import TestCase
from django.urls import reverse

from banking.services import request_business_withdrawal
from .helpers import make_business, make_user


class SecurityTests(TestCase):
    def test_approval_detail_forbidden_for_unrelated_user(self):
        user = make_user()
        personal, business, opening = make_business(user)
        approval = request_business_withdrawal(user, business, "100.00")
        other = make_user("other@example.com", "Other")
        self.client.force_login(other)
        response = self.client.get(reverse("approval_detail", args=[approval.request_id]))
        self.assertEqual(response.status_code, 403)
