from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

from banking.models import BusinessEmployeeAccess


def personal_required(view_func):
    @login_required
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.login_context != "PERSONAL":
            raise PermissionDenied("Personal access is required.")
        return view_func(request, *args, **kwargs)

    return wrapper


def business_employee_required(view_func):
    @login_required
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.login_context != "BUSINESS_EMPLOYEE":
            raise PermissionDenied("Business Employee access is required.")
        return view_func(request, *args, **kwargs)

    return wrapper


def active_business_employee_required(view_func):
    @business_employee_required
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        try:
            access = request.user.business_access
        except BusinessEmployeeAccess.DoesNotExist:
            raise PermissionDenied("Business Employee access is required.")
        if access.access_status == BusinessEmployeeAccess.PASSWORD_CHANGE_REQUIRED:
            return redirect("password_change_required")
        if access.access_status == BusinessEmployeeAccess.DEACTIVATED:
            raise PermissionDenied("Business Employee access is deactivated.")
        request.business_access = access
        request.business_account = access.business_account
        return view_func(request, *args, **kwargs)

    return wrapper


business_required = active_business_employee_required
