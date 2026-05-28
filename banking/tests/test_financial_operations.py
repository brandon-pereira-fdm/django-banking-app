from decimal import Decimal

from django.test import TestCase

from banking.models import BusinessOutgoingRequest, CompletedFinancialTransaction, TransferOperation
from banking.services import (
    BankingError,
    approve_business_request,
    cancel_business_request,
    deposit_business,
    deposit_personal,
    reject_business_request,
    submit_business_transfer_request,
    submit_business_withdrawal_request,
    transfer_from_personal,
    withdraw_personal,
)
from banking.tests.factories import business_authoriser, business_member, personal_user


class FinancialOperationsTests(TestCase):
    def test_personal_deposit_withdrawal_and_zero_boundary(self):
        user = personal_user()
        account = user.personal_account
        deposit_business_user, _business, _access = business_authoriser(email="b@example.com", uen="202400002B")

        deposit_personal(user, account, "100.00")
        account.refresh_from_db()
        self.assertEqual(account.balance, Decimal("100.00"))

        withdraw_personal(user, account, "100.00")
        account.refresh_from_db()
        self.assertEqual(account.balance, Decimal("0.00"))
        with self.assertRaises(BankingError):
            withdraw_personal(user, account, "0.01")
        with self.assertRaises(BankingError):
            deposit_personal(deposit_business_user, account, "1.00")

    def test_personal_transfer_creates_operation_and_two_transactions(self):
        sender = personal_user(email="sender@example.com", phone="+6590000001")
        recipient = personal_user(email="recipient@example.com", phone="+6590000002")
        deposit_personal(sender, sender.personal_account, "50.00")
        transfer, debit, credit = transfer_from_personal(sender, sender.personal_account, "PERSONAL", recipient.personal_account.phone_number, "50.00")
        sender.personal_account.refresh_from_db()
        recipient.personal_account.refresh_from_db()
        self.assertEqual(sender.personal_account.balance, Decimal("0.00"))
        self.assertEqual(recipient.personal_account.balance, Decimal("50.00"))
        self.assertEqual(transfer, debit.transfer_operation)
        self.assertEqual(transfer, credit.transfer_operation)
        self.assertEqual(TransferOperation.objects.count(), 1)

    def test_business_deposit_and_pending_request_no_movement(self):
        authoriser, account, _access = business_authoriser(balance=Decimal("7000.00"))
        member, _member_access = business_member(account)
        deposit_business(member, account, "1000.00")
        account.refresh_from_db()
        self.assertEqual(account.balance, Decimal("8000.00"))
        request = submit_business_withdrawal_request(member, account, "500.00")
        account.refresh_from_db()
        self.assertEqual(request.status, BusinessOutgoingRequest.PENDING)
        self.assertEqual(account.balance, Decimal("8000.00"))
        self.assertEqual(CompletedFinancialTransaction.objects.filter(transaction_type=CompletedFinancialTransaction.WITHDRAWAL).count(), 0)

    def test_business_approval_completion_failure_rejection_and_cancellation(self):
        authoriser, account, _access = business_authoriser(balance=Decimal("8000.00"))
        member, _member_access = business_member(account)
        valid = submit_business_withdrawal_request(member, account, "1000.00")
        approve_business_request(authoriser, valid)
        valid.refresh_from_db()
        account.refresh_from_db()
        self.assertEqual(valid.status, BusinessOutgoingRequest.COMPLETED)
        self.assertEqual(account.balance, Decimal("7000.00"))

        failed = submit_business_withdrawal_request(member, account, "0.01")
        approve_business_request(authoriser, failed)
        failed.refresh_from_db()
        self.assertEqual(failed.status, BusinessOutgoingRequest.FAILED)

        reject = submit_business_withdrawal_request(member, account, "1.00")
        reject_business_request(authoriser, reject)
        reject.refresh_from_db()
        self.assertEqual(reject.status, BusinessOutgoingRequest.REJECTED)

        cancel = submit_business_withdrawal_request(member, account, "1.00")
        cancel_business_request(member, cancel)
        cancel.refresh_from_db()
        self.assertEqual(cancel.status, BusinessOutgoingRequest.CANCELLED)
        with self.assertRaises(BankingError):
            cancel_business_request(member, cancel)

    def test_business_transfer_request_approves_to_personal(self):
        authoriser, account, _access = business_authoriser(balance=Decimal("8000.00"))
        recipient = personal_user(email="p2@example.com", phone="+6591111111")
        request = submit_business_transfer_request(authoriser, account, "PERSONAL", recipient.personal_account.phone_number, "1000.00")
        approve_business_request(authoriser, request)
        request.refresh_from_db()
        recipient.personal_account.refresh_from_db()
        self.assertEqual(request.status, BusinessOutgoingRequest.COMPLETED)
        self.assertEqual(recipient.personal_account.balance, Decimal("1000.00"))
