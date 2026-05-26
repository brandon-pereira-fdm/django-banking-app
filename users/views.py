from django.contrib.auth import login, logout
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import EmailAuthenticationForm, RegistrationForm


def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("dashboard")
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = EmailAuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect("dashboard")
    return render(request, "users/login.html", {"form": form})


@require_POST
def logout_view(request):
    logout(request)
    return redirect("login")
