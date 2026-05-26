from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import re

from django.db import IntegrityError, transaction
from django.utils import timezone

from .models import ApprovalRequest, BankAccount, CompletedTransaction, TransferOperation


MIN_BUSINESS_BALANCE = Decimal("7000.00")
MAX_MONEY = Decimal("9999999999.99")


class BankingError(Exception):
    """Safe domain error suitable for user-facing form messages."""


class PermissionDeniedError(BankingError):
    pass


@dataclass(frozen=True)
class TransferPreview:
    sender: BankAccount
    recipient: BankAccount
    amount: Decimal
    approval_required: bool
    recipient_label: str
    recipient_identifier: str


def normalize_phone(value):
    value = (value or "").strip()
    return re.sub(r"[\s-]+", "", value)


def normalize_uen(value):
    return (value or "").strip().upper()


def validate_sgd_amount(value, *, allow_zero=False):
    if isinstance(value, Decimal):
        amount = value
    else:
        raw = str(value or "").strip()
        if raw.upper().startswith("SGD "):
            raw = raw[4:].strip()
        try:
            amount = Decimal(raw)
        except (InvalidOperation, ValueError):
            raise BankingError("Enter a valid SGD amount.")

    if not amount.is_finite():
        raise BankingError("Enter a valid SGD amount.")
    if amount.as_tuple().exponent < -2:
        raise BankingError("Enter an amount with no more than two decimal places.")
    amount = amount.quantize(Decimal("0.01"))
    if amount < Decimal("0.00") or (amount == Decimal("0.00") and not allow_zero):
        raise BankingError("Enter an amount greater than SGD 0.00.")
    if amount > MAX_MONEY:
        raise BankingError("Enter a smaller SGD amount.")
    return amount


def format_sgd(value):
    return f"SGD {Decimal(value).quantize(Decimal('0.01')):,.2f}"


def mask_identifier(value):
    value = str(value or "")
    if len(value) <= 4:
        return value
    return f"{value[:2]}...{value[-2:]}"


def user_personal_account(user):
    return BankAccount.objects.filter(owner=user, account_type=BankAccount.PERSONAL).first()


def user_business_account(user):
    return BankAccount.objects.filter(owner=user, account_type=BankAccount.BUSINESS).first()


def require_owner(account, user):
    if account.owner_id != user.id:
        raise PermissionDeniedError("You can only use accounts that belong to you.")


def require_authorised_personal_account(request_obj, user):
    if request_obj.authorised_personal_account.owner_id != user.id:
        raise PermissionDeniedError("Only the authorised Personal Account holder can perform this action.")


def _save_account(account):
    account.full_clean()
    account.save()
    return account


def _completed_transaction(account, transaction_type, amount, *, transfer_operation=None, approval_request=None):
    tx = CompletedTransaction.objects.create(
        account=account,
        transaction_type=transaction_type,
        amount=amount,
        transfer_operation=transfer_operation,
        approval_request=approval_request,
    )
    return tx


def create_personal_account(user, phone_number):
    phone = normalize_phone(phone_number)
    if not phone:
        raise BankingError("Enter the phone number used to receive Personal Account transfers.")
    if user_personal_account(user):
        raise BankingError("You already have a Personal Account.")
    if BankAccount.objects.filter(account_type=BankAccount.PERSONAL, phone_number=phone).exists():
        raise BankingError("This phone number is already registered to a Personal Account.")
    account = BankAccount(
        owner=user,
        account_type=BankAccount.PERSONAL,
        balance=Decimal("0.00"),
        phone_number=phone,
    )
    return _save_account(account)


def create_business_account(user, business_display_name, uen, opening_deposit):
    personal = user_personal_account(user)
    if not personal:
        raise BankingError("Open a Personal Account before opening a Business Account.")
    if user_business_account(user):
        raise BankingError("You already have a Business Account.")
    display_name = (business_display_name or "").strip()
    if not display_name:
        raise BankingError("Enter the business display name.")
    normalised_uen = normalize_uen(uen)
    if not normalised_uen:
        raise BankingError("Enter the company UEN used to receive Business Account transfers.")
    if BankAccount.objects.filter(account_type=BankAccount.BUSINESS, uen=normalised_uen).exists():
        raise BankingError("This UEN is already registered to a Business Account.")
    amount = validate_sgd_amount(opening_deposit)
    if amount < MIN_BUSINESS_BALANCE:
        raise BankingError("Business Account opening deposit must be at least SGD 7,000.00.")
    with transaction.atomic():
        account = BankAccount(
            owner=user,
            account_type=BankAccount.BUSINESS,
            balance=amount,
            business_display_name=display_name,
            uen=normalised_uen,
            authorised_personal_account=personal,
        )
        _save_account(account)
        tx = _completed_transaction(account, CompletedTransaction.BUSINESS_OPENING_DEPOSIT, amount)
    return account, tx


def deposit(user, account, amount):
    require_owner(account, user)
    amount = validate_sgd_amount(amount)
    with transaction.atomic():
        account = BankAccount.objects.select_for_update().get(pk=account.pk)
        require_owner(account, user)
        account.balance += amount
        _save_account(account)
        tx = _completed_transaction(account, CompletedTransaction.DEPOSIT, amount)
    return tx


def withdraw_personal(user, account, amount):
    require_owner(account, user)
    if account.account_type != BankAccount.PERSONAL:
        raise BankingError("Business Account withdrawals must be submitted for approval.")
    amount = validate_sgd_amount(amount)
    with transaction.atomic():
        account = BankAccount.objects.select_for_update().get(pk=account.pk)
        require_owner(account, user)
        if account.balance - amount < Decimal("0.00"):
            raise BankingError("This withdrawal would make the Personal Account balance negative.")
        account.balance -= amount
        _save_account(account)
        tx = _completed_transaction(account, CompletedTransaction.WITHDRAWAL, amount)
    return tx


def resolve_transfer_recipient(sender_account, recipient_type, identifier):
    recipient_type = (recipient_type or "").upper()
    if recipient_type == BankAccount.PERSONAL:
        phone = normalize_phone(identifier)
        if BankAccount.objects.filter(account_type=BankAccount.BUSINESS, uen=normalize_uen(identifier)).exists():
            raise BankingError("The selected recipient type does not match the identifier.")
        recipient = BankAccount.objects.filter(account_type=BankAccount.PERSONAL, phone_number=phone).first()
        if not recipient:
            raise BankingError("No Personal Account was found for that phone number.")
    elif recipient_type == BankAccount.BUSINESS:
        uen = normalize_uen(identifier)
        if BankAccount.objects.filter(account_type=BankAccount.PERSONAL, phone_number=normalize_phone(identifier)).exists():
            raise BankingError("The selected recipient type does not match the identifier.")
        recipient = BankAccount.objects.filter(account_type=BankAccount.BUSINESS, uen=uen).first()
        if not recipient:
            raise BankingError("No Business Account was found for that UEN.")
    else:
        raise BankingError("Select whether the recipient is a Personal Account or Business Account.")

    if recipient.pk == sender_account.pk:
        raise BankingError("Self-transfers are not supported in the MVP.")
    if recipient.owner_id == sender_account.owner_id:
        raise BankingError("Transfers between your own Personal and Business Accounts are not supported in the MVP.")
    return recipient


def preview_transfer(user, sender_account, recipient_type, identifier, amount):
    require_owner(sender_account, user)
    amount = validate_sgd_amount(amount)
    recipient = resolve_transfer_recipient(sender_account, recipient_type, identifier)
    return TransferPreview(
        sender=sender_account,
        recipient=recipient,
        amount=amount,
        approval_required=sender_account.account_type == BankAccount.BUSINESS,
        recipient_label=recipient.display_name,
        recipient_identifier=mask_identifier(recipient.receiving_identifier),
    )


def _create_transfer(sender, recipient, amount, *, approval_request=None):
    op = TransferOperation.objects.create(sender_account=sender, recipient_account=recipient, amount=amount)
    debit = _completed_transaction(
        sender,
        CompletedTransaction.TRANSFER_DEBIT,
        amount,
        transfer_operation=op,
        approval_request=approval_request,
    )
    credit = _completed_transaction(
        recipient,
        CompletedTransaction.TRANSFER_CREDIT,
        amount,
        transfer_operation=op,
        approval_request=approval_request,
    )
    return op, debit, credit


def transfer_from_personal(user, sender_account, recipient_type, identifier, amount):
    require_owner(sender_account, user)
    if sender_account.account_type != BankAccount.PERSONAL:
        raise BankingError("Business Account transfers must be submitted for approval.")
    amount = validate_sgd_amount(amount)
    recipient = resolve_transfer_recipient(sender_account, recipient_type, identifier)
    with transaction.atomic():
        sender = BankAccount.objects.select_for_update().get(pk=sender_account.pk)
        recipient = BankAccount.objects.select_for_update().get(pk=recipient.pk)
        require_owner(sender, user)
        if sender.balance - amount < Decimal("0.00"):
            raise BankingError("This transfer would make the Personal Account balance negative.")
        sender.balance -= amount
        recipient.balance += amount
        _save_account(sender)
        _save_account(recipient)
        op, debit, credit = _create_transfer(sender, recipient, amount)
    return op, debit, credit


def request_business_withdrawal(user, business_account, amount):
    require_owner(business_account, user)
    if business_account.account_type != BankAccount.BUSINESS:
        raise BankingError("Select a Business Account for approval withdrawals.")
    amount = validate_sgd_amount(amount)
    return ApprovalRequest.objects.create(
        business_account=business_account,
        authorised_personal_account=business_account.authorised_personal_account,
        request_type=ApprovalRequest.BUSINESS_WITHDRAWAL,
        amount=amount,
    )


def request_business_transfer(user, business_account, recipient_type, identifier, amount):
    require_owner(business_account, user)
    if business_account.account_type != BankAccount.BUSINESS:
        raise BankingError("Select a Business Account for approval transfers.")
    amount = validate_sgd_amount(amount)
    recipient = resolve_transfer_recipient(business_account, recipient_type, identifier)
    return ApprovalRequest.objects.create(
        business_account=business_account,
        authorised_personal_account=business_account.authorised_personal_account,
        request_type=ApprovalRequest.BUSINESS_TRANSFER,
        amount=amount,
        recipient_account=recipient,
        recipient_type_snapshot=recipient.account_type,
        recipient_identifier_snapshot=mask_identifier(recipient.receiving_identifier),
    )


def cancel_request(request_obj, actor):
    if request_obj.business_account.owner_id != actor.id:
        raise PermissionDeniedError("Only the Business Account owner can cancel this request.")
    if request_obj.status != ApprovalRequest.PENDING:
        raise BankingError("Only pending requests can be cancelled.")
    request_obj.status = ApprovalRequest.CANCELLED
    request_obj.resolved_at = timezone.now()
    request_obj.resolution_note = "Cancelled by Business Account owner."
    request_obj.save(update_fields=["status", "resolved_at", "resolution_note"])
    return request_obj


def reject_request(request_obj, actor):
    require_authorised_personal_account(request_obj, actor)
    if request_obj.status != ApprovalRequest.PENDING:
        raise BankingError("Only pending requests can be rejected.")
    request_obj.status = ApprovalRequest.REJECTED
    request_obj.resolved_at = timezone.now()
    request_obj.resolution_note = "Rejected by authorised Personal Account."
    request_obj.save(update_fields=["status", "resolved_at", "resolution_note"])
    return request_obj


def approve_request(request_obj, actor):
    require_authorised_personal_account(request_obj, actor)
    if request_obj.status != ApprovalRequest.PENDING:
        raise BankingError("Only pending requests can be approved.")
    try:
        with transaction.atomic():
            request_obj = ApprovalRequest.objects.select_for_update().get(pk=request_obj.pk)
            business = BankAccount.objects.select_for_update().get(pk=request_obj.business_account_id)
            if business.authorised_personal_account.owner_id != actor.id:
                raise PermissionDeniedError("Only the authorised Personal Account holder can approve this request.")
            amount = validate_sgd_amount(request_obj.amount)
            if business.balance - amount < MIN_BUSINESS_BALANCE:
                raise BankingError("Completing this request would leave less than SGD 7,000.00 in the Business Account.")

            if request_obj.request_type == ApprovalRequest.BUSINESS_WITHDRAWAL:
                business.balance -= amount
                _save_account(business)
                tx = _completed_transaction(
                    business,
                    CompletedTransaction.WITHDRAWAL,
                    amount,
                    approval_request=request_obj,
                )
                request_obj.completed_transaction = tx
            elif request_obj.request_type == ApprovalRequest.BUSINESS_TRANSFER:
                recipient = BankAccount.objects.select_for_update().get(pk=request_obj.recipient_account_id)
                business.balance -= amount
                recipient.balance += amount
                _save_account(business)
                _save_account(recipient)
                op, debit, credit = _create_transfer(
                    business,
                    recipient,
                    amount,
                    approval_request=request_obj,
                )
                request_obj.transfer_operation = op
            else:
                raise BankingError("Unsupported approval request type.")

            request_obj.status = ApprovalRequest.COMPLETED
            request_obj.resolved_at = timezone.now()
            request_obj.resolution_note = "Approved and completed."
            request_obj.save()
            return request_obj
    except BankingError as exc:
        ApprovalRequest.objects.filter(pk=request_obj.pk, status=ApprovalRequest.PENDING).update(
            status=ApprovalRequest.FAILED,
            resolved_at=timezone.now(),
            resolution_note=str(exc),
        )
        request_obj.refresh_from_db()
        return request_obj
    except IntegrityError as exc:
        ApprovalRequest.objects.filter(pk=request_obj.pk, status=ApprovalRequest.PENDING).update(
            status=ApprovalRequest.FAILED,
            resolved_at=timezone.now(),
            resolution_note="Completion failed validation.",
        )
        request_obj.refresh_from_db()
        return request_obj


def completed_transactions_for_user(user):
    return CompletedTransaction.objects.filter(account__owner=user).select_related("account", "transfer_operation")


def approval_requests_for_user(user):
    return ApprovalRequest.objects.filter(
        Q_business_owner(user) | Q_authorised_owner(user)
    ).select_related("business_account", "recipient_account")


def Q_business_owner(user):
    from django.db.models import Q

    return Q(business_account__owner=user)


def Q_authorised_owner(user):
    from django.db.models import Q

    return Q(authorised_personal_account__owner=user)
