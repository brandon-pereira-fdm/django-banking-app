from django.test import TestCase

from banking.services import PermissionDeniedError, require_authorised_personal_account, require_owner, request_business_withdrawal
from .helpers import make_business, make_user


class AccessControlHelperTests(TestCase):
    def test_owner_and_authorised_checks(self):
        user = make_user()
        personal, business, opening = make_business(user)
        other = make_user("other@example.com", "Other")
        with self.assertRaises(PermissionDeniedError):
            require_owner(business, other)
        approval = request_business_withdrawal(user, business, "100.00")
        require_authorised_personal_account(approval, user)
        with self.assertRaises(PermissionDeniedError):
            require_authorised_personal_account(approval, other)
