from django.test import TestCase
from django.urls import reverse

from .helpers import make_user


class UiPolishTests(TestCase):
    def test_public_and_authenticated_pages_have_labels_and_branding(self):
        self.assertContains(self.client.get(reverse("login")), "Midnight Ledger")
        user = make_user()
        self.client.force_login(user)
        response = self.client.get(reverse("dashboard"))
        self.assertContains(response, "Midnight Ledger")
        self.assertContains(response, "Dashboard")
