from django import forms

from banking.models import BusinessEmployeeAccess
from banking.services.money import validate_sgd_amount
from banking.services.transfers import BUSINESS_DESTINATION, PERSONAL_DESTINATION


class AmountForm(forms.Form):
    amount = forms.CharField(label="Amount")

    def clean_amount(self):
        try:
            return validate_sgd_amount(self.cleaned_data["amount"])
        except Exception as exc:
            raise forms.ValidationError(str(exc))


class TransferForm(AmountForm):
    RECIPIENT_CHOICES = (
        (PERSONAL_DESTINATION, "Personal Account by phone number"),
        (BUSINESS_DESTINATION, "Business Account by UEN"),
    )
    recipient_type = forms.ChoiceField(label="Recipient type", choices=RECIPIENT_CHOICES)
    recipient_identifier = forms.CharField(label="Recipient phone number or UEN", max_length=80)


class AddEmployeeAccessForm(forms.Form):
    display_name = forms.CharField(label="Employee display name", max_length=150)
    email = forms.EmailField(label="Employee login email")
    role = forms.ChoiceField(label="Assigned role", choices=BusinessEmployeeAccess.ROLE_CHOICES)
    temporary_password1 = forms.CharField(label="Temporary password", widget=forms.PasswordInput)
    temporary_password2 = forms.CharField(label="Confirm temporary password", widget=forms.PasswordInput)
    confirm_authoriser = forms.BooleanField(
        label="I understand this grants AUTHORISER access",
        required=False,
    )

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("temporary_password1") and cleaned.get("temporary_password2") and cleaned["temporary_password1"] != cleaned["temporary_password2"]:
            raise forms.ValidationError("The two temporary password fields did not match.")
        if cleaned.get("role") == BusinessEmployeeAccess.AUTHORISER and not cleaned.get("confirm_authoriser"):
            raise forms.ValidationError("Confirm before granting AUTHORISER access.")
        return cleaned


class TemporaryPasswordForm(forms.Form):
    temporary_password1 = forms.CharField(label="New temporary password", widget=forms.PasswordInput)
    temporary_password2 = forms.CharField(label="Confirm temporary password", widget=forms.PasswordInput)

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("temporary_password1") and cleaned.get("temporary_password2") and cleaned["temporary_password1"] != cleaned["temporary_password2"]:
            raise forms.ValidationError("The two temporary password fields did not match.")
        return cleaned


class ResolutionForm(forms.Form):
    reason = forms.CharField(label="Reason", max_length=255, required=False)
