from decimal import Decimal

from django.contrib.auth import get_user_model
from django.utils import timezone

from banking.models import BusinessAccount, BusinessEmployeeAccess, PersonalAccount


def personal_user(email="personal@example.com", password="pass12345", username="Personal User", phone="+6590000000"):
    user = get_user_model().objects.create_user(email=email, username=username, password=password, login_context="PERSONAL")
    PersonalAccount.objects.create(owner=user, phone_number=phone, balance=Decimal("0.00"))
    return user


def business_authoriser(
    email="authoriser@example.com",
    password="pass12345",
    username="Authoriser",
    business_name="Acme Pte Ltd",
    uen="202400001A",
    balance=Decimal("7000.00"),
):
    user = get_user_model().objects.create_user(email=email, username=username, password=password, login_context="BUSINESS_EMPLOYEE")
    account = BusinessAccount.objects.create(business_display_name=business_name, uen=uen, balance=balance)
    access = BusinessEmployeeAccess.objects.create(
        user=user,
        business_account=account,
        role=BusinessEmployeeAccess.AUTHORISER,
        access_status=BusinessEmployeeAccess.ACTIVE,
        activated_at=timezone.now(),
    )
    return user, account, access


def business_member(account, email="member@example.com", password="pass12345", username="Member", status=BusinessEmployeeAccess.ACTIVE):
    user = get_user_model().objects.create_user(email=email, username=username, password=password, login_context="BUSINESS_EMPLOYEE")
    access = BusinessEmployeeAccess.objects.create(
        user=user,
        business_account=account,
        role=BusinessEmployeeAccess.MEMBER,
        access_status=status,
        activated_at=timezone.now() if status == BusinessEmployeeAccess.ACTIVE else None,
    )
    return user, access
