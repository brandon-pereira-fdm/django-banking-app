from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from banking.models import (
    AccessAuditEvent,
    BusinessAccount,
    BusinessEmployeeAccess,
    CompletedFinancialTransaction,
    PersonalAccount,
)

from . import ValidationBankingError
from .access_audit import create_access_audit_event
from .money import MIN_BUSINESS_BALANCE, normalize_phone, normalize_uen, validate_sgd_amount


@transaction.atomic
def register_personal_account(display_name, email, password, phone_number):
    User = get_user_model()
    normalized_email = User.objects.normalize_email(email).lower()
    if User.objects.filter(email__iexact=normalized_email).exists():
        raise ValidationBankingError("An account with this email address already exists.")
    normalized_phone = normalize_phone(phone_number)
    if PersonalAccount.objects.filter(phone_number=normalized_phone).exists():
        raise ValidationBankingError("This receiving phone number is already registered.")
    user = User.objects.create_user(
        email=normalized_email,
        username=display_name.strip(),
        password=password,
        login_context=User.PERSONAL,
    )
    account = PersonalAccount(owner=user, phone_number=normalized_phone, balance=Decimal("0.00"))
    account.full_clean()
    account.save()
    return user, account


@transaction.atomic
def register_business_account(display_name, email, password, business_display_name, uen, opening_deposit):
    amount = validate_sgd_amount(opening_deposit)
    if amount < MIN_BUSINESS_BALANCE:
        raise ValidationBankingError("Business opening deposit must be at least SGD 7,000.00.")
    User = get_user_model()
    normalized_email = User.objects.normalize_email(email).lower()
    if User.objects.filter(email__iexact=normalized_email).exists():
        raise ValidationBankingError("An account with this email address already exists.")
    normalized_uen = normalize_uen(uen)
    if BusinessAccount.objects.filter(uen__iexact=normalized_uen).exists():
        raise ValidationBankingError("This UEN is already registered.")
    user = User.objects.create_user(
        email=normalized_email,
        username=display_name.strip(),
        password=password,
        login_context=User.BUSINESS_EMPLOYEE,
    )
    account = BusinessAccount.objects.create(
        business_display_name=business_display_name.strip(),
        uen=normalized_uen,
        balance=amount,
    )
    access = BusinessEmployeeAccess.objects.create(
        user=user,
        business_account=account,
        role=BusinessEmployeeAccess.AUTHORISER,
        access_status=BusinessEmployeeAccess.ACTIVE,
        activated_at=timezone.now(),
    )
    CompletedFinancialTransaction.objects.create(
        business_account=account,
        transaction_type=CompletedFinancialTransaction.BUSINESS_OPENING_DEPOSIT,
        amount=amount,
        actor_user=user,
        description="Business opening deposit",
    )
    create_access_audit_event(
        business_account=account,
        acting_employee=access,
        affected_employee=access,
        event_type=AccessAuditEvent.BUSINESS_ACCOUNT_CREATED,
        new_status=BusinessEmployeeAccess.ACTIVE,
        safe_metadata=f"Business Account {account.uen} created.",
    )
    create_access_audit_event(
        business_account=account,
        acting_employee=access,
        affected_employee=access,
        event_type=AccessAuditEvent.INITIAL_AUTHORISER_CREATED,
        new_role=BusinessEmployeeAccess.AUTHORISER,
        new_status=BusinessEmployeeAccess.ACTIVE,
        safe_metadata=f"Initial AUTHORISER created for {user.email}.",
    )
    return user, account, access
