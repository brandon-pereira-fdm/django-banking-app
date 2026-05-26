from django import forms

from .models import ApprovalRequest, BankAccount, CompletedTransaction
from .services import BankingError, normalize_phone, normalize_uen, validate_sgd_amount


class SgdAmountField(forms.CharField):
    def clean(self, value):
        value = super().clean(value)
        try:
            return validate_sgd_amount(value)
        except BankingError as exc:
            raise forms.ValidationError(str(exc))


class PersonalAccountForm(forms.Form):
    phone_number = forms.CharField(label="Receiving phone number", max_length=32)

    def clean_phone_number(self):
        phone = normalize_phone(self.cleaned_data["phone_number"])
        if not phone:
            raise forms.ValidationError("Enter the phone number used to receive transfers.")
        if BankAccount.objects.filter(account_type=BankAccount.PERSONAL, phone_number=phone).exists():
            raise forms.ValidationError("This phone number is already registered to a Personal Account.")
        return phone


class BusinessAccountForm(forms.Form):
    business_display_name = forms.CharField(label="Business display name", max_length=160)
    uen = forms.CharField(label="Company UEN", max_length=32)
    opening_deposit = SgdAmountField(label="Opening deposit in SGD")

    def clean_uen(self):
        uen = normalize_uen(self.cleaned_data["uen"])
        if not uen:
            raise forms.ValidationError("Enter the company UEN.")
        if BankAccount.objects.filter(account_type=BankAccount.BUSINESS, uen=uen).exists():
            raise forms.ValidationError("This UEN is already registered to a Business Account.")
        return uen


class AccountAmountForm(forms.Form):
    account = forms.ModelChoiceField(queryset=BankAccount.objects.none(), label="Account")
    amount = SgdAmountField(label="Amount in SGD")

    def __init__(self, *args, user=None, account_type=None, **kwargs):
        super().__init__(*args, **kwargs)
        qs = BankAccount.objects.none()
        if user and user.is_authenticated:
            qs = BankAccount.objects.filter(owner=user)
            if account_type:
                qs = qs.filter(account_type=account_type)
        self.fields["account"].queryset = qs


class DepositForm(AccountAmountForm):
    pass


class WithdrawalForm(AccountAmountForm):
    def __init__(self, *args, user=None, business=False, **kwargs):
        account_type = BankAccount.BUSINESS if business else BankAccount.PERSONAL
        super().__init__(*args, user=user, account_type=account_type, **kwargs)


class TransferStartForm(forms.Form):
    RECIPIENT_TYPES = (
        (BankAccount.PERSONAL, "Personal Account"),
        (BankAccount.BUSINESS, "Business Account"),
    )

    source_account = forms.ModelChoiceField(queryset=BankAccount.objects.none(), label="Source account")
    recipient_type = forms.ChoiceField(choices=RECIPIENT_TYPES, label="Recipient account type")
    identifier = forms.CharField(label="Phone number or UEN", max_length=64)
    amount = SgdAmountField(label="Amount in SGD")

    def __init__(self, *args, user=None, source_type=None, **kwargs):
        super().__init__(*args, **kwargs)
        qs = BankAccount.objects.none()
        if user and user.is_authenticated:
            qs = BankAccount.objects.filter(owner=user)
            if source_type:
                qs = qs.filter(account_type=source_type)
        self.fields["source_account"].queryset = qs


class BusinessWithdrawalRequestForm(WithdrawalForm):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, user=user, business=True, **kwargs)


class ApprovalActionForm(forms.Form):
    ACTION_APPROVE = "approve"
    ACTION_REJECT = "reject"
    ACTION_CANCEL = "cancel"
    ACTIONS = (
        (ACTION_APPROVE, "Approve"),
        (ACTION_REJECT, "Reject"),
        (ACTION_CANCEL, "Cancel"),
    )
    action = forms.ChoiceField(choices=ACTIONS)


class TransactionFilterForm(forms.Form):
    account = forms.ModelChoiceField(queryset=BankAccount.objects.none(), required=False, label="Account")
    transaction_type = forms.ChoiceField(required=False, choices=(("", "All transaction types"),) + tuple(CompletedTransaction.TRANSACTION_TYPES))

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user and user.is_authenticated:
            self.fields["account"].queryset = BankAccount.objects.filter(owner=user)


class ApprovalFilterForm(forms.Form):
    status = forms.ChoiceField(required=False, choices=(("", "All statuses"),) + ApprovalRequest.STATUSES)
