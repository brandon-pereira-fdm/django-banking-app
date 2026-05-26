from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def personal_required(view_func):
    @login_required
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.access_context != "PERSONAL":
            raise PermissionDenied("Personal access is required.")
        return view_func(request, *args, **kwargs)

    return wrapper


def business_required(view_func):
    @login_required
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.access_context != "BUSINESS":
            raise PermissionDenied("Business access is required.")
        return view_func(request, *args, **kwargs)

    return wrapper
