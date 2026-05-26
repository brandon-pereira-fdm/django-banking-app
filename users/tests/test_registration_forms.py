from django.test import TestCase
from django.urls import reverse

from banking.models import BusinessAccount, PersonalAccount
from users.forms import BusinessRegistrationForm, PersonalRegistrationForm


class RegistrationFormContextTests(TestCase):
    def test_personal_registration_form_sets_personal_context_without_visible_field(self):
        form = PersonalRegistrationForm(
            data={
                "email": "pat@example.com",
                "username": "Pat",
                "password1": "Str0ngPass123",
                "password2": "Str0ngPass123",
                "phone_number": "+65 9123 4567",
            }
        )
        self.assertNotIn("access_context", form.fields)
        self.assertTrue(form.is_valid(), form.errors.as_data())
        user = form.save()
        self.assertEqual(user.access_context, "PERSONAL")

    def test_business_registration_form_sets_business_context_without_visible_field(self):
        form = BusinessRegistrationForm(
            data={
                "email": "biz@example.com",
                "username": "Biz",
                "password1": "Str0ngPass123",
                "password2": "Str0ngPass123",
                "business_display_name": "Acme Pte Ltd",
                "uen": "202400001a",
                "opening_deposit": "7000.00",
            }
        )
        self.assertNotIn("access_context", form.fields)
        self.assertTrue(form.is_valid(), form.errors.as_data())
        user = form.save()
        self.assertEqual(user.access_context, "BUSINESS")

    def test_registration_pages_submit_successfully(self):
        personal_response = self.client.post(
            reverse("register_personal"),
            {
                "email": "page-personal@example.com",
                "username": "Page Personal",
                "password1": "Str0ngPass123",
                "password2": "Str0ngPass123",
                "phone_number": "+65 9234 5678",
            },
        )
        self.assertEqual(personal_response.status_code, 302)
        self.assertTrue(PersonalAccount.objects.filter(owner__email="page-personal@example.com", owner__access_context="PERSONAL").exists())

        self.client.logout()
        business_response = self.client.post(
            reverse("register_business"),
            {
                "email": "page-business@example.com",
                "username": "Page Business",
                "password1": "Str0ngPass123",
                "password2": "Str0ngPass123",
                "business_display_name": "Page Business Pte Ltd",
                "uen": "202499999A",
                "opening_deposit": "7000.00",
            },
        )
        self.assertEqual(business_response.status_code, 302)
        self.assertTrue(BusinessAccount.objects.filter(uen="202499999A", memberships__user__access_context="BUSINESS").exists())
