from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from banking.models import BusinessAccessAuditEvent, BusinessApprovalRequest, CompletedFinancialTransaction
from banking.services import create_invitation, deposit_business, request_business_withdrawal
from banking.tests.factories import business_account, business_user, membership, personal_account, personal_user


class HistoriesAndSecurityTests(TestCase):
    def test_histories_are_distinct_and_access_controlled(self):
        authoriser = business_user("auth@example.com")
        account = business_account(balance=Decimal("7000.00"))
        membership(authoriser, account)
        deposit_business(authoriser, account, "100.00")
        request_business_withdrawal(authoriser, account, "10.00")
        create_invitation(authoriser, account, "invitee@example.com", "MEMBER")
        self.assertEqual(CompletedFinancialTransaction.objects.count(), 1)
        self.assertEqual(BusinessApprovalRequest.objects.count(), 1)
        self.assertTrue(BusinessAccessAuditEvent.objects.exists())

        personal = personal_user("p@example.com")
        personal_account(personal, phone="+6594444444")
        self.client.force_login(personal)
        self.assertEqual(self.client.get(reverse("business_transactions", args=[account.account_id])).status_code, 403)
        self.assertEqual(self.client.get(reverse("approval_history", args=[account.account_id])).status_code, 403)
        self.assertEqual(self.client.get(reverse("access_audit", args=[account.account_id])).status_code, 403)

        self.client.force_login(authoriser)
        self.assertContains(self.client.get(reverse("business_transactions", args=[account.account_id])), "Completed financial movements only")
        self.assertContains(self.client.get(reverse("approval_history", args=[account.account_id])), "workflow records only")
        self.assertContains(self.client.get(reverse("access_audit", args=[account.account_id])), "membership governance only")

    def test_csrf_middleware_is_enabled(self):
        from django.conf import settings

        self.assertIn("django.middleware.csrf.CsrfViewMiddleware", settings.MIDDLEWARE)
