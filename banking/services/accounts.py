from decimal import Decimal

from django.db import transaction

from banking.models import BusinessAccount, CompletedFinancialTransaction, PersonalAccount

from . import ValidationBankingError
from .access import require_active_employee, require_personal_owner
from .money import validate_sgd_amount


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
        description="Personal deposit",
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
        description="Personal withdrawal",
    )


@transaction.atomic
def deposit_business(actor, business_account, amount):
    access = require_active_employee(actor, business_account)
    amount = validate_sgd_amount(amount)
    account = BusinessAccount.objects.select_for_update().get(pk=business_account.pk)
    account.balance += amount
    account.save(update_fields=["balance"])
    return CompletedFinancialTransaction.objects.create(
        business_account=account,
        transaction_type=CompletedFinancialTransaction.DEPOSIT,
        amount=amount,
        actor_user=actor,
        description=f"Business deposit by {access.user.email}",
    )
