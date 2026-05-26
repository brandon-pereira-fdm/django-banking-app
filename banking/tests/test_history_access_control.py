from django.test import TestCase
from django.urls import reverse

from .helpers import make_user


class HistoryAccessControlTests(TestCase):
    def test_history_requires_login(self):
        response = self.client.get(reverse("transactions"))
        self.assertEqual(response.status_code, 302)

    def test_authenticated_history_page_loads(self):
        user = make_user()
        self.client.force_login(user)
        response = self.client.get(reverse("transactions"))
        self.assertEqual(response.status_code, 200)
