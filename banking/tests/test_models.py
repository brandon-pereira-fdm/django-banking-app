from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from banking.models import (
    BusinessAccount,
    BusinessApprovalRequest,
    BusinessInvitation,
    BusinessMembership,
    CompletedFinancialTransaction,
    PersonalAccount,
    TransferOperation,
)
from banking.tests.factories import business_account, business_user, membership, personal_account, personal_user


class ModelTests(TestCase):
    def test_personal_account_requires_personal_user_and_unique_phone(self):
        p_user = personal_user()
        b_user = business_user()
        account = PersonalAccount(owner=p_user, phone_number="+6590000001")
        account.full_clean()
        PersonalAccount.objects.create(owner=p_user, phone_number="+6590000001")
        with self.assertRaises(ValidationError):
            PersonalAccount(owner=b_user, phone_number="+6590000002").full_clean()
        with self.assertRaises(Exception):
            PersonalAccount.objects.create(owner=personal_user("p2@example.com"), phone_number="+6590000001")

    def test_business_memberships_and_invitations(self):
        user = business_user()
        account_one = business_account(uen="202400001A")
        account_two = business_account(name="Beta", uen="202400002A")
        membership(user, account_one, BusinessMembership.MEMBER)
        membership(user, account_two, BusinessMembership.AUTHORISER)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                membership(user, account_one, BusinessMembership.MEMBER)
        with self.assertRaises(ValidationError):
            BusinessMembership(user=personal_user("p3@example.com"), business_account=account_one, role=BusinessMembership.MEMBER).full_clean()
        invitation = BusinessInvitation.objects.create(
            business_account=account_one,
            invited_email="invitee@example.com",
            intended_role=BusinessMembership.AUTHORISER,
            inviting_membership=BusinessMembership.objects.get(user=user, business_account=account_two),
        )
        self.assertEqual(invitation.status, BusinessInvitation.PENDING)

    def test_financial_and_approval_choices(self):
        statuses = [choice[0] for choice in BusinessApprovalRequest.STATUS_CHOICES]
        self.assertEqual(statuses, ["PENDING", "COMPLETED", "REJECTED", "CANCELLED", "FAILED"])
        self.assertNotIn("APPROVED", statuses)
        self.assertTrue(CompletedFinancialTransaction.TRANSACTION_TYPE_CHOICES)
        self.assertTrue(TransferOperation._meta.get_field("transfer_operation_id"))
