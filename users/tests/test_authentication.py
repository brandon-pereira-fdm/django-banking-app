from django.contrib.auth import authenticate, get_user_model
from django.db import IntegrityError
from django.test import TestCase


class AuthenticationTests(TestCase):
    def test_personal_and_business_employee_identities_use_context_and_hashing(self):
        User = get_user_model()
        personal = User.objects.create_user(email="p@example.com", username="P", password="pass12345", login_context=User.PERSONAL)
        business = User.objects.create_user(email="b@example.com", username="B", password="pass12345", login_context=User.BUSINESS_EMPLOYEE)

        self.assertEqual(personal.login_context, User.PERSONAL)
        self.assertEqual(business.login_context, User.BUSINESS_EMPLOYEE)
        self.assertNotEqual(personal.password, "pass12345")
        self.assertTrue(personal.check_password("pass12345"))

    def test_duplicate_email_rejected_across_contexts(self):
        User = get_user_model()
        User.objects.create_user(email="same@example.com", username="P", password="pass12345", login_context=User.PERSONAL)
        with self.assertRaises(IntegrityError):
            User.objects.create_user(email="same@example.com", username="B", password="pass12345", login_context=User.BUSINESS_EMPLOYEE)

    def test_authenticate_success_and_failure(self):
        User = get_user_model()
        User.objects.create_user(email="p@example.com", username="P", password="pass12345", login_context=User.PERSONAL)
        self.assertIsNotNone(authenticate(username="p@example.com", password="pass12345"))
        self.assertIsNone(authenticate(username="p@example.com", password="wrong"))
