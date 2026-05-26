from decimal import Decimal

from django.contrib.auth import get_user_model

from banking.models import BusinessAccount, BusinessMembership, PersonalAccount


def personal_user(email="personal@example.com", username="Personal"):
    return get_user_model().objects.create_user(email=email, username=username, password="Str0ngPass123", access_context="PERSONAL")


def business_user(email="business@example.com", username="Business"):
    return get_user_model().objects.create_user(email=email, username=username, password="Str0ngPass123", access_context="BUSINESS")


def personal_account(user=None, phone="+6590000000", balance=Decimal("0.00")):
    user = user or personal_user()
    return PersonalAccount.objects.create(owner=user, phone_number=phone, balance=balance)


def business_account(name="Acme Pte Ltd", uen="202400001A", balance=Decimal("7000.00")):
    return BusinessAccount.objects.create(business_display_name=name, uen=uen, balance=balance)


def membership(user=None, account=None, role=BusinessMembership.AUTHORISER):
    user = user or business_user()
    account = account or business_account()
    return BusinessMembership.objects.create(user=user, business_account=account, role=role)
