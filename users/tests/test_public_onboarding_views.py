from django.test import TestCase


class PublicOnboardingViewTests(TestCase):
    def test_product_selection_has_v3_account_paths_without_old_terms(self):
        response = self.client.get("/")
        self.assertContains(response, "Personal Account")
        self.assertContains(response, "Business Account")
        self.assertContains(response, "Phone number")
        self.assertContains(response, "UEN")
        self.assertContains(response, "employee access")
        self.assertNotContains(response, "Invite Business User")
        self.assertNotContains(response, "Store Invitation")

    def test_login_page_available(self):
        response = self.client.get("/login/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sign In")
