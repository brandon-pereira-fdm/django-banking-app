from decimal import Decimal

from django.contrib.auth import get_user_model

from banking.models import BankAccount
from banking.services import create_business_account, create_personal_account, deposit, user_personal_account


User = get_user_model()


def make_user(email="user@example.com", username="User"):
    return User.objects.create_user(email=email, username=username, password="ComplexPass123!")


def make_personal(user=None, phone="91234567", balance=Decimal("0.00")):
    user = user or make_user()
    account = create_personal_account(user, phone)
    if balance:
        deposit(user, account, balance)
        account.refresh_from_db()
    return account


def make_business(user=None, phone="91234567", uen="202612345A", opening=Decimal("7000.00"), name="Acme Pte Ltd"):
    user = user or make_user()
    personal = user_personal_account(user) or create_personal_account(user, phone)
    business, tx = create_business_account(user, name, uen, opening)
    return personal, business, tx


def make_other_personal(email="other@example.com", username="Other", phone="92345678", balance=Decimal("0.00")):
    user = make_user(email, username)
    return make_personal(user, phone, balance)
