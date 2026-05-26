from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


User = get_user_model()


class UserIdentityTests(TestCase):
    def test_user_manager_uses_unique_email_and_display_username(self):
        user = User.objects.create_user(email="person@example.com", username="Person", password="ComplexPass123!")
        self.assertEqual(user.email, "person@example.com")
        self.assertEqual(str(user), "Person")

    def test_duplicate_email_rejected(self):
        User.objects.create_user(email="same@example.com", username="One", password="ComplexPass123!")
        with self.assertRaises(Exception):
            User.objects.create_user(email="same@example.com", username="Two", password="ComplexPass123!")

    def test_registration_hashes_password_and_signs_in(self):
        response = self.client.post(
            reverse("register"),
            {
                "email": "new@example.com",
                "username": "New",
                "password1": "ComplexPass123!",
                "password2": "ComplexPass123!",
            },
        )
        self.assertRedirects(response, reverse("dashboard"))
        user = User.objects.get(email="new@example.com")
        self.assertNotEqual(user.password, "ComplexPass123!")
        self.assertTrue(user.check_password("ComplexPass123!"))

    def test_sign_in_success_and_failure(self):
        User.objects.create_user(email="login@example.com", username="Login", password="ComplexPass123!")
        ok = self.client.post(reverse("login"), {"email": "login@example.com", "password": "ComplexPass123!"})
        self.assertRedirects(ok, reverse("dashboard"))
        self.client.post(reverse("logout"))
        bad = self.client.post(reverse("login"), {"email": "login@example.com", "password": "wrong"})
        self.assertContains(bad, "email address or password", status_code=200)

    def test_protected_page_requires_authentication(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)
