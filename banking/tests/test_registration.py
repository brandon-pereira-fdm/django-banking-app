from decimal import Decimal

from django.test import TestCase

from banking.models import BusinessAccessAuditEvent, BusinessMembership, CompletedFinancialTransaction, PersonalAccount
from banking.services import ValidationBankingError, register_business_creator, register_personal_user


class RegistrationTests(TestCase):
    def test_personal_registration_creates_account_at_zero_no_business_access(self):
        user, account = register_personal_user("Pat", "pat@example.com", "Str0ngPass123", "+65 9123 4567")
        self.assertEqual(user.access_context, "PERSONAL")
        self.assertEqual(account.balance, Decimal("0.00"))
        self.assertEqual(PersonalAccount.objects.count(), 1)
        self.assertEqual(BusinessMembership.objects.count(), 0)
        self.assertFalse(CompletedFinancialTransaction.objects.exists())

    def test_business_registration_creates_initial_authoriser_and_audit(self):
        user, account, membership = register_business_creator(
            "Biz Creator",
            "biz@example.com",
            "Str0ngPass123",
            "Acme Pte Ltd",
            "202400001a",
            "7000.00",
        )
        self.assertEqual(user.access_context, "BUSINESS")
        self.assertEqual(account.uen, "202400001A")
        self.assertEqual(account.balance, Decimal("7000.00"))
        self.assertEqual(membership.role, BusinessMembership.AUTHORISER)
        self.assertEqual(CompletedFinancialTransaction.objects.get().transaction_type, CompletedFinancialTransaction.BUSINESS_OPENING_DEPOSIT)
        self.assertEqual(BusinessAccessAuditEvent.objects.count(), 2)
        self.assertFalse(PersonalAccount.objects.exists())

    def test_business_registration_rejects_below_minimum(self):
        with self.assertRaises(ValidationBankingError):
            register_business_creator("Biz", "biz@example.com", "Str0ngPass123", "Acme", "202400001A", "6999.99")
