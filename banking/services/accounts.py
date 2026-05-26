from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction

from banking.models import (
    BusinessAccessAuditEvent,
    BusinessAccount,
    BusinessMembership,
    CompletedFinancialTransaction,
    PersonalAccount,
)

from . import ValidationBankingError
from .memberships import require_business_membership, require_personal_owner
from .money import MIN_BUSINESS_BALANCE, normalize_phone, normalize_uen, validate_sgd_amount


def _full_clean_save(instance):
    instance.full_clean()
    instance.save()
    return instance


@transaction.atomic
def register_personal_user(username, email, password, phone_number):
    User = get_user_model()
    normalized_phone = normalize_phone(phone_number)
    user = User.objects.create_user(
        email=email.strip().lower(),
        username=username.strip(),
        password=password,
        access_context=User.PERSONAL,
    )
    account = PersonalAccount(owner=user, phone_number=normalized_phone, balance=Decimal("0.00"))
    _full_clean_save(account)
    return user, account


@transaction.atomic
def register_business_creator(username, email, password, business_display_name, uen, opening_deposit):
    amount = validate_sgd_amount(opening_deposit)
    if amount < MIN_BUSINESS_BALANCE:
        raise ValidationBankingError("Business opening deposit must be at least SGD 7,000.00.")
    User = get_user_model()
    user = User.objects.create_user(
        email=email.strip().lower(),
        username=username.strip(),
        password=password,
        access_context=User.BUSINESS,
    )
    account = BusinessAccount(
        business_display_name=business_display_name.strip(),
        uen=normalize_uen(uen),
        balance=amount,
    )
    _full_clean_save(account)
    membership = BusinessMembership(business_account=account, user=user, role=BusinessMembership.AUTHORISER)
    _full_clean_save(membership)
    CompletedFinancialTransaction.objects.create(
        business_account=account,
        transaction_type=CompletedFinancialTransaction.BUSINESS_OPENING_DEPOSIT,
        amount=amount,
        actor_user=user,
    )
    BusinessAccessAuditEvent.objects.create(
        business_account=account,
        acting_user=user,
        affected_user=user,
        event_type=BusinessAccessAuditEvent.BUSINESS_ACCOUNT_CREATED,
        details="Business Account created.",
    )
    BusinessAccessAuditEvent.objects.create(
        business_account=account,
        acting_user=user,
        affected_user=user,
        role=BusinessMembership.AUTHORISER,
        event_type=BusinessAccessAuditEvent.INITIAL_AUTHORISER_ASSIGNED,
        details="Creator assigned as initial AUTHORISER.",
    )
    return user, account, membership


@transaction.atomic
def deposit_personal(actor, personal_account, amount):
    require_personal_owner(actor, personal_account)
    amount = validate_sgd_amount(amount)
    account = PersonalAccount.objects.select_for_update().get(pk=personal_account.pk)
    account.balance += amount
    account.save(update_fields=["balance"])
    return CompletedFinancialTransaction.objects.create(
        personal_account=account,
        transaction_type=CompletedFinancialTransaction.DEPOSIT,
        amount=amount,
        actor_user=actor,
    )


@transaction.atomic
def withdraw_personal(actor, personal_account, amount):
    require_personal_owner(actor, personal_account)
    amount = validate_sgd_amount(amount)
    account = PersonalAccount.objects.select_for_update().get(pk=personal_account.pk)
    if account.balance - amount < Decimal("0.00"):
        raise ValidationBankingError("Insufficient funds.")
    account.balance -= amount
    account.save(update_fields=["balance"])
    return CompletedFinancialTransaction.objects.create(
        personal_account=account,
        transaction_type=CompletedFinancialTransaction.WITHDRAWAL,
        amount=amount,
        actor_user=actor,
    )


@transaction.atomic
def deposit_business(actor, business_account, amount):
    membership = require_business_membership(actor, business_account)
    amount = validate_sgd_amount(amount)
    account = BusinessAccount.objects.select_for_update().get(pk=business_account.pk)
    account.balance += amount
    account.save(update_fields=["balance"])
    return CompletedFinancialTransaction.objects.create(
        business_account=account,
        transaction_type=CompletedFinancialTransaction.DEPOSIT,
        amount=amount,
        actor_user=membership.user,
    )


def translate_validation_error(error):
    if isinstance(error, ValidationError):
        if hasattr(error, "message_dict"):
            first = next(iter(error.message_dict.values()))
            if isinstance(first, list):
                return first[0]
            return str(first)
        return "; ".join(error.messages)
    return str(error)
