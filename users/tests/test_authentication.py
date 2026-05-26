from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class AuthenticationTests(TestCase):
    def test_unique_email_access_contexts_and_password_hashing(self):
        User = get_user_model()
        personal = User.objects.create_user(
            email="same@example.com",
            username="Pat",
            password="Str0ngPass123",
            access_context=User.PERSONAL,
        )
        self.assertEqual(personal.access_context, User.PERSONAL)
        self.assertTrue(personal.check_password("Str0ngPass123"))
        self.assertNotEqual(personal.password, "Str0ngPass123")
        with self.assertRaises(Exception):
            User.objects.create_user(
                email="same@example.com",
                username="Biz",
                password="Str0ngPass123",
                access_context=User.BUSINESS,
            )

    def test_valid_and_invalid_sign_in(self):
        User = get_user_model()
        User.objects.create_user(email="pat@example.com", username="Pat", password="Str0ngPass123", access_context=User.PERSONAL)
        response = self.client.post(reverse("login"), {"email": "pat@example.com", "password": "wrong"})
        self.assertContains(response, "incorrect", status_code=200)
        response = self.client.post(reverse("login"), {"email": "pat@example.com", "password": "Str0ngPass123"})
        self.assertEqual(response.status_code, 302)
