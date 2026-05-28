from decimal import Decimal

from django.test import TestCase

from banking.models import AccessAuditEvent, BusinessEmployeeAccess, CompletedFinancialTransaction, PersonalAccount
from banking.services import BankingError, register_business_account, register_personal_account


class RegistrationServiceTests(TestCase):
    def test_personal_registration_creates_zero_balance_personal_only_account(self):
        user, account = register_personal_account("P", "p@example.com", "pass12345", "+6590000000")
        self.assertEqual(user.login_context, "PERSONAL")
        self.assertEqual(account.balance, Decimal("0.00"))
        self.assertEqual(PersonalAccount.objects.count(), 1)
        self.assertEqual(CompletedFinancialTransaction.objects.count(), 0)
        self.assertFalse(hasattr(user, "business_access"))

    def test_business_registration_creates_active_authoriser_opening_transaction_and_audit(self):
        user, account, access = register_business_account("A", "a@example.com", "pass12345", "Acme", "202400001A", "7000.00")
        self.assertEqual(user.login_context, "BUSINESS_EMPLOYEE")
        self.assertEqual(account.balance, Decimal("7000.00"))
        self.assertEqual(access.role, BusinessEmployeeAccess.AUTHORISER)
        self.assertEqual(access.access_status, BusinessEmployeeAccess.ACTIVE)
        self.assertEqual(CompletedFinancialTransaction.objects.get().transaction_type, CompletedFinancialTransaction.BUSINESS_OPENING_DEPOSIT)
        self.assertEqual(AccessAuditEvent.objects.count(), 2)
        self.assertEqual(PersonalAccount.objects.count(), 0)

    def test_business_opening_below_minimum_rejected_without_partial_creation(self):
        with self.assertRaises(BankingError):
            register_business_account("A", "a@example.com", "pass12345", "Acme", "202400001A", "6999.99")
        self.assertEqual(BusinessEmployeeAccess.objects.count(), 0)
