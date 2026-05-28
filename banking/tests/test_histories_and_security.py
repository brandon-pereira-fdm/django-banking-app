from django.test import TestCase

from banking.models import AccessAuditEvent, BusinessEmployeeAccess, BusinessOutgoingRequest, CompletedFinancialTransaction
from banking.services import deposit_business, deposit_personal, provision_employee_access, submit_business_withdrawal_request
from banking.tests.factories import business_authoriser, personal_user


class HistoriesAndSecurityTests(TestCase):
    def test_histories_are_distinct_and_do_not_show_password_content(self):
        authoriser, account, _access = business_authoriser()
        personal = personal_user(email="p@example.com")
        deposit_personal(personal, personal.personal_account, "25.00")
        deposit_business(authoriser, account, "25.00")
        submit_business_withdrawal_request(authoriser, account, "1.00")
        provision_employee_access(authoriser, "Member", "m@example.com", BusinessEmployeeAccess.MEMBER, "temp12345")

        self.assertTrue(CompletedFinancialTransaction.objects.filter(transaction_type=CompletedFinancialTransaction.DEPOSIT).exists())
        self.assertTrue(BusinessOutgoingRequest.objects.filter(status=BusinessOutgoingRequest.PENDING).exists())
        self.assertTrue(AccessAuditEvent.objects.filter(event_type=AccessAuditEvent.EMPLOYEE_ACCESS_CREATED).exists())
        self.assertFalse(AccessAuditEvent.objects.filter(safe_metadata__icontains="temp12345").exists())

    def test_ui_routes_do_not_expose_old_navigation(self):
        authoriser, _account, _access = business_authoriser()
        self.client.force_login(authoriser)
        response = self.client.get("/business/team-access/")
        self.assertContains(response, "Team Access")
        self.assertNotContains(response, "Invite Business User")
        self.assertNotContains(response, "Store Invitation")
        self.assertEqual(self.client.get("/business/invitations/").status_code, 404)
