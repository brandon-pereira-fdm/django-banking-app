from django.test import TestCase

from banking.models import AccessAuditEvent, BusinessEmployeeAccess
from banking.services import (
    BankingError,
    complete_mandatory_password_change,
    deactivate_employee_access,
    promote_member_to_authoriser,
    provision_employee_access,
    reactivate_employee_access,
    reset_employee_temporary_password,
)
from banking.tests.factories import business_authoriser, business_member


class EmployeeAccessTests(TestCase):
    def test_authoriser_provisions_member_and_authoriser_with_temporary_password(self):
        authoriser, account, _access = business_authoriser()
        member_access = provision_employee_access(authoriser, "Member", "m@example.com", BusinessEmployeeAccess.MEMBER, "temp12345")
        auth_access = provision_employee_access(authoriser, "Auth", "a2@example.com", BusinessEmployeeAccess.AUTHORISER, "temp12345")

        self.assertEqual(member_access.business_account, account)
        self.assertEqual(member_access.access_status, BusinessEmployeeAccess.PASSWORD_CHANGE_REQUIRED)
        self.assertTrue(member_access.user.check_password("temp12345"))
        self.assertNotEqual(member_access.user.password, "temp12345")
        self.assertEqual(auth_access.role, BusinessEmployeeAccess.AUTHORISER)
        self.assertEqual(AccessAuditEvent.objects.filter(event_type=AccessAuditEvent.EMPLOYEE_ACCESS_CREATED).count(), 2)
        self.assertFalse(AccessAuditEvent.objects.filter(safe_metadata__icontains="temp12345").exists())

    def test_member_cannot_provision_or_administer_access(self):
        _authoriser, account, _auth_access = business_authoriser()
        member, member_access = business_member(account)
        with self.assertRaises(BankingError):
            provision_employee_access(member, "X", "x@example.com", BusinessEmployeeAccess.MEMBER, "temp12345")
        with self.assertRaises(BankingError):
            promote_member_to_authoriser(member, member_access)

    def test_mandatory_password_change_activates_employee(self):
        authoriser, _account, _access = business_authoriser()
        provisioned = provision_employee_access(authoriser, "Member", "m@example.com", BusinessEmployeeAccess.MEMBER, "temp12345")
        complete_mandatory_password_change(provisioned.user, "newpass12345")
        provisioned.refresh_from_db()
        self.assertEqual(provisioned.access_status, BusinessEmployeeAccess.ACTIVE)
        self.assertTrue(provisioned.user.check_password("newpass12345"))
        self.assertTrue(AccessAuditEvent.objects.filter(event_type=AccessAuditEvent.PASSWORD_CHANGE_COMPLETED).exists())

    def test_reset_requires_password_change_and_invalidates_prior_password(self):
        authoriser, account, _access = business_authoriser()
        member, member_access = business_member(account)
        self.assertTrue(member.check_password("pass12345"))
        reset_employee_temporary_password(authoriser, member_access, "temp54321")
        member.refresh_from_db()
        member_access.refresh_from_db()
        self.assertFalse(member.check_password("pass12345"))
        self.assertTrue(member.check_password("temp54321"))
        self.assertEqual(member_access.access_status, BusinessEmployeeAccess.PASSWORD_CHANGE_REQUIRED)
        self.assertFalse(AccessAuditEvent.objects.filter(safe_metadata__icontains="temp54321").exists())

    def test_promotion_deactivation_final_authoriser_and_reactivation(self):
        authoriser, account, auth_access = business_authoriser()
        member, member_access = business_member(account)
        promote_member_to_authoriser(authoriser, member_access)
        member_access.refresh_from_db()
        self.assertEqual(member_access.role, BusinessEmployeeAccess.AUTHORISER)

        deactivate_employee_access(authoriser, member_access)
        member_access.refresh_from_db()
        self.assertEqual(member_access.access_status, BusinessEmployeeAccess.DEACTIVATED)

        with self.assertRaises(BankingError):
            deactivate_employee_access(authoriser, auth_access)
        self.assertTrue(AccessAuditEvent.objects.filter(event_type=AccessAuditEvent.FINAL_AUTHORISER_DEACTIVATION_REJECTED).exists())

        reactivate_employee_access(authoriser, member_access, "temp99999")
        member_access.refresh_from_db()
        member.refresh_from_db()
        self.assertEqual(member_access.access_status, BusinessEmployeeAccess.PASSWORD_CHANGE_REQUIRED)
        self.assertTrue(member.check_password("temp99999"))
