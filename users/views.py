from django.contrib import messages
from django.contrib.auth import login, logout
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from banking.models import BusinessInvitation
from banking.services import (
    BankingError,
    register_business_creator,
    register_business_user_from_invitation,
    register_personal_user,
)

from .forms import (
    BusinessRegistrationForm,
    EmailAuthenticationForm,
    InvitedBusinessRegistrationForm,
    PersonalRegistrationForm,
)


def account_type_selection(request):
    return render(request, "users/account_type_selection.html")


@require_http_methods(["GET", "POST"])
def register_personal(request):
    form = PersonalRegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            user, account = register_personal_user(
                form.cleaned_data["username"],
                form.cleaned_data["email"],
                form.cleaned_data["password1"],
                form.cleaned_data["phone_number"],
            )
        except Exception as exc:
            form.add_error(None, str(exc))
        else:
            login(request, user)
            messages.success(request, "Personal Account created.")
            return redirect("personal_dashboard")
    return render(request, "users/register_personal.html", {"form": form})


@require_http_methods(["GET", "POST"])
def register_business(request):
    form = BusinessRegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            user, account, membership = register_business_creator(
                form.cleaned_data["username"],
                form.cleaned_data["email"],
                form.cleaned_data["password1"],
                form.cleaned_data["business_display_name"],
                form.cleaned_data["uen"],
                form.cleaned_data["opening_deposit"],
            )
        except BankingError as exc:
            form.add_error(None, str(exc))
        except Exception as exc:
            form.add_error(None, str(exc))
        else:
            login(request, user)
            messages.success(request, "Business Account created.")
            return redirect("business_dashboard", account_id=account.account_id)
    return render(request, "users/register_business.html", {"form": form})


@require_http_methods(["GET", "POST"])
def register_business_invited(request, invitation_id):
    invitation = get_object_or_404(BusinessInvitation, invitation_id=invitation_id, status=BusinessInvitation.PENDING)
    form = InvitedBusinessRegistrationForm(request.POST or None, invitation=invitation)
    if request.method == "POST" and form.is_valid():
        try:
            user, membership = register_business_user_from_invitation(
                invitation,
                form.cleaned_data["username"],
                form.cleaned_data["password1"],
            )
        except Exception as exc:
            form.add_error(None, str(exc))
        else:
            login(request, user)
            messages.success(request, "Invitation accepted.")
            return redirect("business_dashboard", account_id=membership.business_account.account_id)
    return render(request, "users/register_business_invited.html", {"form": form, "invitation": invitation})


@require_http_methods(["GET", "POST"])
def login_view(request):
    form = EmailAuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        if user.access_context == "PERSONAL":
            return redirect("personal_dashboard")
        return redirect("business_home")
    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")
