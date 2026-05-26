from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from banking.models import (
    BusinessAccount,
    BusinessApprovalRequest,
    BusinessMembership,
    CompletedFinancialTransaction,
    PersonalAccount,
)

from . import PermissionDeniedError, ValidationBankingError
from .memberships import require_authoriser, require_business_membership
from .money import MIN_BUSINESS_BALANCE, mask_identifier, validate_sgd_amount
from .transfers import _create_transfer_operation, resolve_transfer_recipient


def _ensure_pending(request_obj):
    if request_obj.status != BusinessApprovalRequest.PENDING:
        raise ValidationBankingError("Only Pending requests can be actioned.")


def _snapshot_recipient(recipient):
    if isinstance(recipient, PersonalAccount):
        return "PERSONAL", recipient.phone_number, recipient.display_name
    return "BUSINESS", recipient.uen, recipient.display_name


@transaction.atomic
def request_business_withdrawal(actor, business_account, amount):
    membership = require_business_membership(actor, business_account)
    amount = validate_sgd_amount(amount)
    return BusinessApprovalRequest.objects.create(
        business_account=business_account,
        requesting_membership=membership,
        requested_by=actor,
        request_type=BusinessApprovalRequest.BUSINESS_WITHDRAWAL,
        amount=amount,
    )


@transaction.atomic
def request_business_transfer(actor, business_account, destination_type, identifier, amount):
    membership = require_business_membership(actor, business_account)
    amount = validate_sgd_amount(amount)
    recipient = resolve_transfer_recipient(destination_type, identifier, source_account=business_account)
    recipient_type, recipient_identifier, recipient_name = _snapshot_recipient(recipient)
    kwargs = {
        "business_account": business_account,
        "requesting_membership": membership,
        "requested_by": actor,
        "request_type": BusinessApprovalRequest.BUSINESS_TRANSFER,
        "amount": amount,
        "recipient_type_snapshot": recipient_type,
        "recipient_identifier_snapshot": mask_identifier(recipient_identifier),
        "recipient_name_snapshot": recipient_name,
    }
    if isinstance(recipient, PersonalAccount):
        kwargs["recipient_personal_account"] = recipient
    else:
        kwargs["recipient_business_account"] = recipient
    return BusinessApprovalRequest.objects.create(**kwargs)


@transaction.atomic
def approve_request(actor, request_obj):
    request_obj = BusinessApprovalRequest.objects.select_for_update().get(pk=request_obj.pk)
    _ensure_pending(request_obj)
    authoriser_membership = require_authoriser(actor, request_obj.business_account)
    account = BusinessAccount.objects.select_for_update().get(pk=request_obj.business_account.pk)
    request_obj.actioning_membership = authoriser_membership
    request_obj.actioned_by = actor
    request_obj.resolved_at = timezone.now()
    if account.balance - request_obj.amount < MIN_BUSINESS_BALANCE:
        request_obj.status = BusinessApprovalRequest.FAILED
        request_obj.resolution_note = "Retained minimum would be breached."
        request_obj.save(update_fields=["actioning_membership", "actioned_by", "resolved_at", "status", "resolution_note"])
        return request_obj
    if request_obj.request_type == BusinessApprovalRequest.BUSINESS_WITHDRAWAL:
        account.balance -= request_obj.amount
        account.save(update_fields=["balance"])
        transaction_record = CompletedFinancialTransaction.objects.create(
            business_account=account,
            transaction_type=CompletedFinancialTransaction.WITHDRAWAL,
            amount=request_obj.amount,
            business_approval_request=request_obj,
            actor_user=actor,
        )
        request_obj.completed_transaction = transaction_record
    elif request_obj.request_type == BusinessApprovalRequest.BUSINESS_TRANSFER:
        recipient = request_obj.recipient_personal_account or request_obj.recipient_business_account
        if recipient is None:
            request_obj.status = BusinessApprovalRequest.FAILED
            request_obj.resolution_note = "Recipient is no longer available."
            request_obj.save(update_fields=["actioning_membership", "actioned_by", "resolved_at", "status", "resolution_note"])
            return request_obj
        account.balance -= request_obj.amount
        account.save(update_fields=["balance"])
        if isinstance(recipient, PersonalAccount):
            recipient_locked = PersonalAccount.objects.select_for_update().get(pk=recipient.pk)
        else:
            recipient_locked = BusinessAccount.objects.select_for_update().get(pk=recipient.pk)
        recipient_locked.balance += request_obj.amount
        recipient_locked.save(update_fields=["balance"])
        transfer, debit, credit = _create_transfer_operation(
            account,
            recipient_locked,
            request_obj.amount,
            approval_request=request_obj,
            actor=actor,
        )
        request_obj.transfer_operation = transfer
        request_obj.completed_transaction = debit
    else:
        raise ValidationBankingError("Unsupported request type.")
    request_obj.status = BusinessApprovalRequest.COMPLETED
    request_obj.resolution_note = "Completed by AUTHORISER approval."
    request_obj.save(
        update_fields=[
            "actioning_membership",
            "actioned_by",
            "resolved_at",
            "status",
            "resolution_note",
            "completed_transaction",
            "transfer_operation",
        ]
    )
    return request_obj


@transaction.atomic
def reject_request(actor, request_obj, reason="Rejected by AUTHORISER."):
    request_obj = BusinessApprovalRequest.objects.select_for_update().get(pk=request_obj.pk)
    _ensure_pending(request_obj)
    authoriser_membership = require_authoriser(actor, request_obj.business_account)
    request_obj.status = BusinessApprovalRequest.REJECTED
    request_obj.actioning_membership = authoriser_membership
    request_obj.actioned_by = actor
    request_obj.resolved_at = timezone.now()
    request_obj.resolution_note = reason[:255]
    request_obj.save(update_fields=["status", "actioning_membership", "actioned_by", "resolved_at", "resolution_note"])
    return request_obj


@transaction.atomic
def cancel_request(actor, request_obj):
    request_obj = BusinessApprovalRequest.objects.select_for_update().get(pk=request_obj.pk)
    _ensure_pending(request_obj)
    membership = require_business_membership(actor, request_obj.business_account)
    if membership.role != BusinessMembership.AUTHORISER and request_obj.requested_by_id != actor.id:
        raise PermissionDeniedError("Members may cancel only their own Pending requests.")
    request_obj.status = BusinessApprovalRequest.CANCELLED
    request_obj.actioning_membership = membership
    request_obj.actioned_by = actor
    request_obj.resolved_at = timezone.now()
    request_obj.resolution_note = "Cancelled."
    request_obj.save(update_fields=["status", "actioning_membership", "actioned_by", "resolved_at", "resolution_note"])
    return request_obj
