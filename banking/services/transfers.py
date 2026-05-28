from decimal import Decimal

from django.db import transaction

from banking.models import BusinessAccount, CompletedFinancialTransaction, PersonalAccount, TransferOperation

from . import ValidationBankingError
from .access import require_personal_owner
from .money import mask_identifier, normalize_phone, normalize_uen, validate_sgd_amount


PERSONAL_DESTINATION = "PERSONAL"
BUSINESS_DESTINATION = "BUSINESS"


def _source_matches_destination(source_account, destination_account):
    return source_account.__class__ == destination_account.__class__ and source_account.pk == destination_account.pk


def resolve_transfer_recipient(destination_type, identifier, source_account=None):
    if destination_type == PERSONAL_DESTINATION:
        normalized = normalize_phone(identifier)
        try:
            recipient = PersonalAccount.objects.select_related("owner").get(phone_number=normalized)
        except PersonalAccount.DoesNotExist:
            raise ValidationBankingError("No Personal Account matches that phone number.")
    elif destination_type == BUSINESS_DESTINATION:
        normalized = normalize_uen(identifier)
        try:
            recipient = BusinessAccount.objects.get(uen=normalized)
        except BusinessAccount.DoesNotExist:
            raise ValidationBankingError("No Business Account matches that UEN.")
    else:
        raise ValidationBankingError("Choose Personal or Business recipient type.")
    if source_account is not None and _source_matches_destination(source_account, recipient):
        raise ValidationBankingError("Transfers to the same account are not supported.")
    return recipient


def preview_transfer_recipient(destination_type, identifier, source_account=None):
    recipient = resolve_transfer_recipient(destination_type, identifier, source_account=source_account)
    return {
        "recipient": recipient,
        "recipient_type": destination_type,
        "display_name": recipient.display_name,
        "masked_identifier": mask_identifier(recipient.receiving_identifier),
    }


def create_transfer_operation(sender_account, recipient_account, amount, business_outgoing_request=None, actor=None):
    kwargs = {"amount": amount, "business_outgoing_request": business_outgoing_request}
    if isinstance(sender_account, PersonalAccount):
        kwargs["sender_personal_account"] = sender_account
    else:
        kwargs["sender_business_account"] = sender_account
    if isinstance(recipient_account, PersonalAccount):
        kwargs["recipient_personal_account"] = recipient_account
    else:
        kwargs["recipient_business_account"] = recipient_account
    transfer = TransferOperation.objects.create(**kwargs)
    debit_kwargs = {
        "transaction_type": CompletedFinancialTransaction.TRANSFER_DEBIT,
        "amount": amount,
        "transfer_operation": transfer,
        "business_outgoing_request": business_outgoing_request,
        "actor_user": actor,
        "description": "Transfer debit",
    }
    credit_kwargs = {
        "transaction_type": CompletedFinancialTransaction.TRANSFER_CREDIT,
        "amount": amount,
        "transfer_operation": transfer,
        "business_outgoing_request": business_outgoing_request,
        "actor_user": actor,
        "description": "Transfer credit",
    }
    if isinstance(sender_account, PersonalAccount):
        debit_kwargs["personal_account"] = sender_account
    else:
        debit_kwargs["business_account"] = sender_account
    if isinstance(recipient_account, PersonalAccount):
        credit_kwargs["personal_account"] = recipient_account
    else:
        credit_kwargs["business_account"] = recipient_account
    return transfer, CompletedFinancialTransaction.objects.create(**debit_kwargs), CompletedFinancialTransaction.objects.create(**credit_kwargs)


@transaction.atomic
def transfer_from_personal(actor, personal_account, destination_type, identifier, amount):
    require_personal_owner(actor, personal_account)
    amount = validate_sgd_amount(amount)
    sender = PersonalAccount.objects.select_for_update().get(pk=personal_account.pk)
    recipient = resolve_transfer_recipient(destination_type, identifier, source_account=sender)
    if sender.balance - amount < Decimal("0.00"):
        raise ValidationBankingError("Insufficient funds.")
    sender.balance -= amount
    sender.save(update_fields=["balance"])
    if isinstance(recipient, PersonalAccount):
        recipient_locked = PersonalAccount.objects.select_for_update().get(pk=recipient.pk)
    else:
        recipient_locked = BusinessAccount.objects.select_for_update().get(pk=recipient.pk)
    recipient_locked.balance += amount
    recipient_locked.save(update_fields=["balance"])
    return create_transfer_operation(sender, recipient_locked, amount, actor=actor)
