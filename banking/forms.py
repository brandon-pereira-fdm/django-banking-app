from django import forms

from banking.models import BusinessMembership
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


class InvitationForm(forms.Form):
    invited_email = forms.EmailField(label="Invitee email")
    intended_role = forms.ChoiceField(label="Role", choices=BusinessMembership.ROLE_CHOICES)


class ResolutionForm(forms.Form):
    reason = forms.CharField(label="Reason", max_length=255, required=False)
