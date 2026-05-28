from django.test import TestCase

from banking.tests.factories import business_authoriser, personal_user


class AccessContextTests(TestCase):
    def test_personal_denied_business_pages_and_business_denied_personal_pages(self):
        personal = personal_user()
        business, _account, _access = business_authoriser()

        self.client.force_login(personal)
        response = self.client.get("/business/")
        self.assertEqual(response.status_code, 403)

        self.client.force_login(business)
        response = self.client.get("/personal/")
        self.assertEqual(response.status_code, 403)
