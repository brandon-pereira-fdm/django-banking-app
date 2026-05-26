from django.test import TestCase
from django.urls import reverse

from banking.tests.factories import business_account, business_user, membership, personal_account, personal_user


class AccessContextTests(TestCase):
    def test_personal_denied_business_and_business_denied_personal(self):
        personal = personal_user(email="p@example.com")
        personal_account(personal, phone="+6591111111")
        business = business_user(email="b@example.com")
        account = business_account()
        membership(business, account)

        self.client.force_login(personal)
        self.assertEqual(self.client.get(reverse("business_dashboard", args=[account.account_id])).status_code, 403)

        self.client.force_login(business)
        self.assertEqual(self.client.get(reverse("personal_dashboard")).status_code, 403)
