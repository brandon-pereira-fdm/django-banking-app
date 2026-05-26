from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from .helpers import make_personal, make_user


class TransferViewTests(TestCase):
    def test_transfer_form_and_safe_confirmation(self):
        user = make_user()
        sender = make_personal(user, "91234567", Decimal("20.00"))
        recipient = make_personal(make_user("r@example.com", "Recipient"), "92345678")
        self.client.force_login(user)
        response = self.client.get(reverse("transfer"))
        self.assertContains(response, "Recipient account type")
        response = self.client.post(reverse("transfer"), {"source_account": sender.pk, "recipient_type": "PERSONAL", "identifier": "92345678", "amount": "10.00"})
        self.assertContains(response, "Recipient")
        self.assertNotContains(response, "r@example.com")
