from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import UserCreationForm

from banking.models import BusinessAccount, PersonalAccount
from banking.services.money import MIN_BUSINESS_BALANCE, normalize_phone, normalize_uen, validate_sgd_amount


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


class BaseAccessRegistrationForm(UserCreationForm):
    login_context_value = None

    class Meta:
        model = get_user_model()
        fields = ("email", "username", "password1", "password2")
        labels = {"email": "Email address", "username": "Display name"}

    def clean(self):
        cleaned_data = super().clean()
        if self.login_context_value:
            self.instance.login_context = self.login_context_value
        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if get_user_model().objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email address already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.login_context_value:
            user.login_context = self.login_context_value
        if commit:
            user.save()
        return user


class PersonalRegistrationForm(BaseAccessRegistrationForm):
    login_context_value = "PERSONAL"
    phone_number = forms.CharField(label="Receiving phone number", max_length=32)

    class Meta(BaseAccessRegistrationForm.Meta):
        fields = BaseAccessRegistrationForm.Meta.fields + ("phone_number",)

    def clean_phone_number(self):
        phone = normalize_phone(self.cleaned_data["phone_number"])
        if not phone:
            raise forms.ValidationError("A receiving phone number is required.")
        if PersonalAccount.objects.filter(phone_number=phone).exists():
            raise forms.ValidationError("This receiving phone number is already registered.")
        return phone


class BusinessRegistrationForm(BaseAccessRegistrationForm):
    login_context_value = "BUSINESS_EMPLOYEE"
    business_display_name = forms.CharField(label="Business display name", max_length=160)
    uen = forms.CharField(label="UEN", max_length=32)
    opening_deposit = forms.CharField(label="Opening deposit")

    class Meta(BaseAccessRegistrationForm.Meta):
        fields = BaseAccessRegistrationForm.Meta.fields + ("business_display_name", "uen", "opening_deposit")

    def clean_business_display_name(self):
        value = self.cleaned_data["business_display_name"].strip()
        if not value:
            raise forms.ValidationError("Business display name is required.")
        return value

    def clean_uen(self):
        uen = normalize_uen(self.cleaned_data["uen"])
        if not uen:
            raise forms.ValidationError("A UEN is required.")
        if BusinessAccount.objects.filter(uen__iexact=uen).exists():
            raise forms.ValidationError("This UEN is already registered.")
        return uen

    def clean_opening_deposit(self):
        try:
            amount = validate_sgd_amount(self.cleaned_data["opening_deposit"])
        except Exception as exc:
            raise forms.ValidationError(str(exc))
        if amount < MIN_BUSINESS_BALANCE:
            raise forms.ValidationError("Business opening deposit must be at least SGD 7,000.00.")
        return amount


class MandatoryPasswordChangeForm(forms.Form):
    password1 = forms.CharField(label="New password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm new password", widget=forms.PasswordInput)

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password1") and cleaned.get("password2") and cleaned["password1"] != cleaned["password2"]:
            raise forms.ValidationError("The two password fields did not match.")
        return cleaned
