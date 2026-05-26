from django.test import TestCase
from django.urls import reverse


class PublicOnboardingViewsTests(TestCase):
    def test_account_type_selection_separates_personal_and_business(self):
        response = self.client.get(reverse("account_type_selection"))
        self.assertContains(response, "Personal Account")
        self.assertContains(response, "phone number")
        self.assertContains(response, "SGD 0.00")
        self.assertContains(response, "Business Account")
        self.assertContains(response, "UEN")
        self.assertContains(response, "SGD 7,000.00")
        self.assertContains(response, "AUTHORISER approval")
