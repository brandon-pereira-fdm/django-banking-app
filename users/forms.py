from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import UserCreationForm

from banking.models import BusinessAccount, BusinessInvitation, PersonalAccount
from banking.services.money import normalize_phone, normalize_uen


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
    access_context_value = None

    class Meta:
        model = get_user_model()
        fields = ("email", "username", "password1", "password2")
        labels = {"email": "Email address", "username": "Username"}

    def clean(self):
        cleaned_data = super().clean()
        if self.access_context_value:
            self.instance.access_context = self.access_context_value
        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if get_user_model().objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email address already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.access_context_value:
            user.access_context = self.access_context_value
        if commit:
            user.save()
        return user


class PersonalRegistrationForm(BaseAccessRegistrationForm):
    access_context_value = "PERSONAL"
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
    access_context_value = "BUSINESS"
    business_display_name = forms.CharField(label="Business display name", max_length=160)
    uen = forms.CharField(label="UEN", max_length=32)
    opening_deposit = forms.DecimalField(label="Opening deposit", max_digits=12, decimal_places=2)

    class Meta(BaseAccessRegistrationForm.Meta):
        fields = BaseAccessRegistrationForm.Meta.fields + ("business_display_name", "uen", "opening_deposit")

    def clean_uen(self):
        uen = normalize_uen(self.cleaned_data["uen"])
        if not uen:
            raise forms.ValidationError("A UEN is required.")
        if BusinessAccount.objects.filter(uen=uen).exists():
            raise forms.ValidationError("This UEN is already registered.")
        return uen


class InvitedBusinessRegistrationForm(BaseAccessRegistrationForm):
    access_context_value = "BUSINESS"

    def __init__(self, *args, invitation=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.invitation = invitation
        if invitation:
            self.fields["email"].initial = invitation.invited_email
            self.fields["email"].disabled = True

    def clean_email(self):
        if self.invitation:
            email = self.invitation.invited_email.lower()
            if get_user_model().objects.filter(email__iexact=email).exists():
                raise forms.ValidationError("An account with this invitation email already exists. Sign in to accept it.")
            return email
        return super().clean_email()
