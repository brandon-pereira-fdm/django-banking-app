from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from banking.models import (
    AccessAuditEvent,
    BusinessEmployeeAccess,
    BusinessOutgoingRequest,
    CompletedFinancialTransaction,
    PersonalAccount,
    TransferOperation,
)
from banking.tests.factories import business_authoriser, personal_user


class ModelStructureTests(TestCase):
    def test_personal_account_requires_personal_owner_and_unique_phone(self):
        personal = personal_user()
        self.assertEqual(personal.personal_account.balance, 0)
        business, _account, _access = business_authoriser(email="b1@example.com", uen="202400002B")
        invalid = PersonalAccount(owner=business, phone_number="+6599990000")
        with self.assertRaises(ValidationError):
            invalid.full_clean()

    def test_business_employee_access_is_one_account_scoped_and_has_no_balance_or_identifier(self):
        _user, _account, access = business_authoriser()
        self.assertFalse(hasattr(access, "balance"))
        self.assertFalse(hasattr(access, "phone_number"))
        self.assertFalse(hasattr(access, "uen"))
        self.assertEqual(access.role, BusinessEmployeeAccess.AUTHORISER)
        self.assertEqual(access.access_status, BusinessEmployeeAccess.ACTIVE)

    def test_status_and_role_choices_do_not_include_superseded_values(self):
        self.assertEqual({c[0] for c in BusinessEmployeeAccess.ROLE_CHOICES}, {"MEMBER", "AUTHORISER"})
        self.assertEqual({c[0] for c in BusinessEmployeeAccess.STATUS_CHOICES}, {"PASSWORD_CHANGE_REQUIRED", "ACTIVE", "DEACTIVATED"})
        self.assertEqual({c[0] for c in BusinessOutgoingRequest.STATUS_CHOICES}, {"PENDING", "COMPLETED", "REJECTED", "CANCELLED", "FAILED"})
        self.assertNotIn("APPROVED", {c[0] for c in BusinessOutgoingRequest.STATUS_CHOICES})

    def test_record_families_are_distinct(self):
        self.assertNotEqual(CompletedFinancialTransaction._meta.db_table, BusinessOutgoingRequest._meta.db_table)
        self.assertNotEqual(AccessAuditEvent._meta.db_table, CompletedFinancialTransaction._meta.db_table)
        self.assertTrue(TransferOperation._meta.get_field("operation_id").unique)

    def test_email_unique_for_all_login_contexts(self):
        User = get_user_model()
        User.objects.create_user(email="unique@example.com", username="P", password="pass12345", login_context=User.PERSONAL)
        with self.assertRaises(Exception):
            User.objects.create_user(email="unique@example.com", username="B", password="pass12345", login_context=User.BUSINESS_EMPLOYEE)
