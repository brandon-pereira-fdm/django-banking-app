from django.test import TestCase
from django.urls import reverse

from .helpers import make_user


class DashboardUiTests(TestCase):
    def test_dashboard_shell_renders_navigation_and_username(self):
        user = make_user()
        self.client.force_login(user)
        response = self.client.get(reverse("dashboard"))
        self.assertContains(response, "Dashboard")
        self.assertContains(response, user.username)
        self.assertContains(response, "Personal Account")
        self.assertContains(response, "Business Account")
