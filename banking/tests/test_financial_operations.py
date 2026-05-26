from decimal import Decimal

from django.test import TestCase

from banking.models import BusinessApprovalRequest, CompletedFinancialTransaction, PersonalAccount, TransferOperation
from banking.services import (
    PermissionDeniedError,
    ValidationBankingError,
    approve_request,
    cancel_request,
    deposit_business,
    deposit_personal,
    reject_request,
    request_business_transfer,
    request_business_withdrawal,
    transfer_from_personal,
    withdraw_personal,
)
from banking.tests.factories import business_account, business_user, membership, personal_account, personal_user


class FinancialOperationsTests(TestCase):
    def test_personal_deposit_withdrawal_and_zero_boundary(self):
        user = personal_user()
        account = personal_account(user, balance=Decimal("100.00"))
        deposit_personal(user, account, "25.00")
        account.refresh_from_db()
        self.assertEqual(account.balance, Decimal("125.00"))
        withdraw_personal(user, account, "125.00")
        account.refresh_from_db()
        self.assertEqual(account.balance, Decimal("0.00"))
        with self.assertRaises(ValidationBankingError):
            withdraw_personal(user, account, "0.01")
        self.assertEqual(CompletedFinancialTransaction.objects.filter(personal_account=account).count(), 2)

    def test_business_deposit_requires_membership_and_no_approval(self):
        user = business_user()
        account = business_account(balance=Decimal("7000.00"))
        membership(user, account)
        deposit_business(user, account, "100.00")
        account.refresh_from_db()
        self.assertEqual(account.balance, Decimal("7100.00"))
        self.assertEqual(BusinessApprovalRequest.objects.count(), 0)
        outsider = business_user("out@example.com")
        with self.assertRaises(PermissionDeniedError):
            deposit_business(outsider, account, "1.00")

    def test_personal_transfers_to_personal_and_business(self):
        sender_user = personal_user("sender@example.com")
        sender = personal_account(sender_user, phone="+6591111111", balance=Decimal("100.00"))
        recipient_user = personal_user("recipient@example.com")
        recipient = personal_account(recipient_user, phone="+6592222222", balance=Decimal("0.00"))
        business = business_account(balance=Decimal("7000.00"))
        transfer, debit, credit = transfer_from_personal(sender_user, sender, "PERSONAL", recipient.phone_number, "25.00")
        sender.refresh_from_db()
        recipient.refresh_from_db()
        self.assertEqual(sender.balance, Decimal("75.00"))
        self.assertEqual(recipient.balance, Decimal("25.00"))
        self.assertEqual(debit.transfer_operation_id, credit.transfer_operation_id)
        transfer_from_personal(sender_user, sender, "BUSINESS", business.uen, "75.00")
        sender.refresh_from_db()
        business.refresh_from_db()
        self.assertEqual(sender.balance, Decimal("0.00"))
        self.assertEqual(business.balance, Decimal("7075.00"))
        with self.assertRaises(ValidationBankingError):
            transfer_from_personal(sender_user, sender, "PERSONAL", sender.phone_number, "1.00")
        self.assertEqual(TransferOperation.objects.count(), 2)

    def test_business_requests_and_approvals_lifecycle(self):
        authoriser = business_user("auth@example.com")
        member_user = business_user("member@example.com")
        account = business_account(balance=Decimal("8000.00"))
        membership(authoriser, account)
        member = membership(member_user, account, role="MEMBER")
        request = request_business_withdrawal(member_user, account, "500.00")
        account.refresh_from_db()
        self.assertEqual(request.status, BusinessApprovalRequest.PENDING)
        self.assertEqual(account.balance, Decimal("8000.00"))
        self.assertFalse(CompletedFinancialTransaction.objects.filter(business_approval_request=request).exists())
        with self.assertRaises(PermissionDeniedError):
            approve_request(member_user, request)
        approve_request(authoriser, request)
        request.refresh_from_db()
        account.refresh_from_db()
        self.assertEqual(request.status, BusinessApprovalRequest.COMPLETED)
        self.assertEqual(account.balance, Decimal("7500.00"))
        pending = request_business_withdrawal(member_user, account, "500.01")
        approve_request(authoriser, pending)
        pending.refresh_from_db()
        account.refresh_from_db()
        self.assertEqual(pending.status, BusinessApprovalRequest.FAILED)
        self.assertEqual(account.balance, Decimal("7500.00"))
        reject_me = request_business_withdrawal(member_user, account, "1.00")
        reject_request(authoriser, reject_me)
        reject_me.refresh_from_db()
        self.assertEqual(reject_me.status, BusinessApprovalRequest.REJECTED)
        cancel_me = request_business_withdrawal(member_user, account, "1.00")
        cancel_request(member_user, cancel_me)
        cancel_me.refresh_from_db()
        self.assertEqual(cancel_me.status, BusinessApprovalRequest.CANCELLED)

    def test_business_transfer_request_moves_only_on_approval(self):
        authoriser = business_user("auth@example.com")
        account = business_account(balance=Decimal("7500.00"))
        membership(authoriser, account)
        recipient_user = personal_user("recipient@example.com")
        recipient = personal_account(recipient_user, phone="+6593333333", balance=Decimal("0.00"))
        request = request_business_transfer(authoriser, account, "PERSONAL", recipient.phone_number, "500.00")
        recipient.refresh_from_db()
        self.assertEqual(recipient.balance, Decimal("0.00"))
        self.assertEqual(TransferOperation.objects.count(), 0)
        approve_request(authoriser, request)
        request.refresh_from_db()
        account.refresh_from_db()
        recipient.refresh_from_db()
        self.assertEqual(request.status, BusinessApprovalRequest.COMPLETED)
        self.assertEqual(account.balance, Decimal("7000.00"))
        self.assertEqual(recipient.balance, Decimal("500.00"))
        self.assertEqual(TransferOperation.objects.count(), 1)
