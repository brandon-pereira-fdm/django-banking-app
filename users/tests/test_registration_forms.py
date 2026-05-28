from django.test import TestCase

from users.forms import BusinessRegistrationForm, PersonalRegistrationForm


class RegistrationFormTests(TestCase):
    def test_registration_forms_set_login_context_without_visible_field(self):
        personal_form = PersonalRegistrationForm(
            data={
                "email": "p@example.com",
                "username": "P",
                "password1": "complex-pass-123",
                "password2": "complex-pass-123",
                "phone_number": "+6590000000",
            }
        )
        self.assertTrue(personal_form.is_valid(), personal_form.errors)
        self.assertNotIn("login_context", personal_form.fields)
        self.assertEqual(personal_form.save(commit=False).login_context, "PERSONAL")

        business_form = BusinessRegistrationForm(
            data={
                "email": "b@example.com",
                "username": "B",
                "password1": "complex-pass-123",
                "password2": "complex-pass-123",
                "business_display_name": "Acme",
                "uen": "202400001A",
                "opening_deposit": "7000.00",
            }
        )
        self.assertTrue(business_form.is_valid(), business_form.errors)
        self.assertNotIn("login_context", business_form.fields)
        self.assertEqual(business_form.save(commit=False).login_context, "BUSINESS_EMPLOYEE")
