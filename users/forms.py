from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm

from .models import CustomUser


class RegistrationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("email", "username", "password1", "password2")
        labels = {
            "email": "Email address",
            "username": "Username",
        }

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email address already exists.")
        return email


class EmailAuthenticationForm(forms.Form):
    email = forms.EmailField(label="Email address")
    password = forms.CharField(label="Password", widget=forms.PasswordInput)

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.user_cache = None

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")
        if email and password:
            self.user_cache = authenticate(self.request, username=email.strip().lower(), password=password)
            if self.user_cache is None:
                raise forms.ValidationError("The email address or password is incorrect.")
        return cleaned_data

    def get_user(self):
        return self.user_cache
