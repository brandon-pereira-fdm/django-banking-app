from django.db import transaction
from django.utils import timezone

from banking.models import (
    BusinessAccount,
    BusinessEmployeeAccess,
    BusinessOutgoingRequest,
    CompletedFinancialTransaction,
    PersonalAccount,
)

from . import PermissionDeniedError, ValidationBankingError
from .access import require_active_employee, require_authoriser
from .money import MIN_BUSINESS_BALANCE, mask_identifier, validate_sgd_amount
from .transfers import create_transfer_operation, resolve_transfer_recipient


def _ensure_pending(request_obj):
    if request_obj.status != BusinessOutgoingRequest.PENDING:
        raise ValidationBankingError("Only Pending requests can be actioned.")


def _snapshot_recipient(recipient):
    if isinstance(recipient, PersonalAccount):
        return "PERSONAL", recipient.phone_number, recipient.display_name
    return "BUSINESS", recipient.uen, recipient.display_name


@transaction.atomic
def submit_business_withdrawal_request(actor, business_account, amount):
    access = require_active_employee(actor, business_account)
    amount = validate_sgd_amount(amount)
    return BusinessOutgoingRequest.objects.create(
        business_account=business_account,
        requested_by=access,
        request_type=BusinessOutgoingRequest.BUSINESS_WITHDRAWAL,
        amount=amount,
    )


@transaction.atomic
def submit_business_transfer_request(actor, business_account, destination_type, identifier, amount):
    access = require_active_employee(actor, business_account)
    amount = validate_sgd_amount(amount)
    recipient = resolve_transfer_recipient(destination_type, identifier, source_account=business_account)
    recipient_type, recipient_identifier, recipient_name = _snapshot_recipient(recipient)
    kwargs = {
        "business_account": business_account,
        "requested_by": access,
        "request_type": BusinessOutgoingRequest.BUSINESS_TRANSFER,
        "amount": amount,
        "recipient_type_snapshot": recipient_type,
        "recipient_identifier_snapshot": mask_identifier(recipient_identifier),
        "recipient_name_snapshot": recipient_name,
    }
    if isinstance(recipient, PersonalAccount):
        kwargs["recipient_personal_account"] = recipient
    else:
        kwargs["recipient_business_account"] = recipient
    return BusinessOutgoingRequest.objects.create(**kwargs)


@transaction.atomic
def approve_business_request(actor, request_obj):
    request_obj = BusinessOutgoingRequest.objects.select_for_update().select_related("business_account").get(pk=request_obj.pk)
    _ensure_pending(request_obj)
    authoriser = require_authoriser(actor, request_obj.business_account)
    account = BusinessAccount.objects.select_for_update().get(pk=request_obj.business_account.pk)
    request_obj.actioned_by = authoriser
    request_obj.resolved_at = timezone.now()
    if account.balance - request_obj.amount < MIN_BUSINESS_BALANCE:
        request_obj.status = BusinessOutgoingRequest.FAILED
        request_obj.safe_reason = "Retained minimum would be breached."
        request_obj.save(update_fields=["actioned_by", "resolved_at", "status", "safe_reason"])
        return request_obj
    if request_obj.request_type == BusinessOutgoingRequest.BUSINESS_WITHDRAWAL:
        account.balance -= request_obj.amount
        account.save(update_fields=["balance"])
        transaction_record = CompletedFinancialTransaction.objects.create(
            business_account=account,
            transaction_type=CompletedFinancialTransaction.WITHDRAWAL,
            amount=request_obj.amount,
            business_outgoing_request=request_obj,
            actor_user=actor,
            description="Business withdrawal approved",
        )
        request_obj.completed_transaction = transaction_record
    elif request_obj.request_type == BusinessOutgoingRequest.BUSINESS_TRANSFER:
        recipient = request_obj.recipient_personal_account or request_obj.recipient_business_account
        if recipient is None:
            request_obj.status = BusinessOutgoingRequest.FAILED
            request_obj.safe_reason = "Recipient is no longer available."
            request_obj.save(update_fields=["actioned_by", "resolved_at", "status", "safe_reason"])
            return request_obj
        account.balance -= request_obj.amount
        account.save(update_fields=["balance"])
        if isinstance(recipient, PersonalAccount):
            recipient_locked = PersonalAccount.objects.select_for_update().get(pk=recipient.pk)
        else:
            recipient_locked = BusinessAccount.objects.select_for_update().get(pk=recipient.pk)
        recipient_locked.balance += request_obj.amount
        recipient_locked.save(update_fields=["balance"])
        transfer, debit, _credit = create_transfer_operation(
            account,
            recipient_locked,
            request_obj.amount,
            business_outgoing_request=request_obj,
            actor=actor,
        )
        request_obj.transfer_operation = transfer
        request_obj.completed_transaction = debit
    else:
        raise ValidationBankingError("Unsupported request type.")
    request_obj.status = BusinessOutgoingRequest.COMPLETED
    request_obj.safe_reason = "Completed by AUTHORISER approval."
    request_obj.save(
        update_fields=[
            "actioned_by",
            "resolved_at",
            "status",
            "safe_reason",
            "completed_transaction",
            "transfer_operation",
        ]
    )
    return request_obj


@transaction.atomic
def reject_business_request(actor, request_obj, reason="Rejected by AUTHORISER."):
    request_obj = BusinessOutgoingRequest.objects.select_for_update().get(pk=request_obj.pk)
    _ensure_pending(request_obj)
    authoriser = require_authoriser(actor, request_obj.business_account)
    request_obj.status = BusinessOutgoingRequest.REJECTED
    request_obj.actioned_by = authoriser
    request_obj.resolved_at = timezone.now()
    request_obj.safe_reason = reason[:255]
    request_obj.save(update_fields=["status", "actioned_by", "resolved_at", "safe_reason"])
    return request_obj


@transaction.atomic
def cancel_business_request(actor, request_obj):
    request_obj = BusinessOutgoingRequest.objects.select_for_update().get(pk=request_obj.pk)
    _ensure_pending(request_obj)
    access = require_active_employee(actor, request_obj.business_account)
    if access.role != BusinessEmployeeAccess.AUTHORISER and request_obj.requested_by_id != access.id:
        raise PermissionDeniedError("Members may cancel only their own Pending requests.")
    request_obj.status = BusinessOutgoingRequest.CANCELLED
    request_obj.actioned_by = access
    request_obj.resolved_at = timezone.now()
    request_obj.safe_reason = "Cancelled."
    request_obj.save(update_fields=["status", "actioned_by", "resolved_at", "safe_reason"])
    return request_obj
