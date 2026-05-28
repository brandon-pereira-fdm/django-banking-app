from django.contrib import messages
from django.contrib.auth import login, logout
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from banking.models import BusinessEmployeeAccess
from banking.services import BankingError, complete_mandatory_password_change, register_business_account, register_personal_account

from .forms import BusinessRegistrationForm, EmailAuthenticationForm, MandatoryPasswordChangeForm, PersonalRegistrationForm


def account_type_selection(request):
    return render(request, "users/account_type_selection.html")


@require_http_methods(["GET", "POST"])
def register_personal(request):
    form = PersonalRegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            user, _account = register_personal_account(
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
            user, _account, _access = register_business_account(
                form.cleaned_data["username"],
                form.cleaned_data["email"],
                form.cleaned_data["password1"],
                form.cleaned_data["business_display_name"],
                form.cleaned_data["uen"],
                form.cleaned_data["opening_deposit"],
            )
        except Exception as exc:
            form.add_error(None, str(exc))
        else:
            login(request, user)
            messages.success(request, "Business Account created.")
            return redirect("business_dashboard")
    return render(request, "users/register_business.html", {"form": form})


@require_http_methods(["GET", "POST"])
def login_view(request):
    form = EmailAuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        if user.login_context == "BUSINESS_EMPLOYEE":
            try:
                access = user.business_access
            except BusinessEmployeeAccess.DoesNotExist:
                raise PermissionDenied("Business Employee access is required.")
            if access.access_status == BusinessEmployeeAccess.DEACTIVATED:
                form.add_error(None, "This Business Employee access is deactivated.")
                return render(request, "users/login.html", {"form": form})
        login(request, user)
        if user.login_context == "PERSONAL":
            return redirect("personal_dashboard")
        if user.business_access.access_status == BusinessEmployeeAccess.PASSWORD_CHANGE_REQUIRED:
            return redirect("password_change_required")
        return redirect("business_dashboard")
    return render(request, "users/login.html", {"form": form})


@require_http_methods(["GET", "POST"])
def password_change_required(request):
    if not request.user.is_authenticated or request.user.login_context != "BUSINESS_EMPLOYEE":
        raise PermissionDenied("Business Employee access is required.")
    if request.user.business_access.access_status == BusinessEmployeeAccess.ACTIVE:
        return redirect("business_dashboard")
    if request.user.business_access.access_status == BusinessEmployeeAccess.DEACTIVATED:
        raise PermissionDenied("Business Employee access is deactivated.")
    form = MandatoryPasswordChangeForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            complete_mandatory_password_change(request.user, form.cleaned_data["password1"])
        except BankingError as exc:
            form.add_error(None, str(exc))
        else:
            messages.success(request, "Your private password has been set. Business access is active.")
            return redirect("business_dashboard")
    return render(request, "users/password_change_required.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")
