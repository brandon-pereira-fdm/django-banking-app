import uuid
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


class BankAccount(models.Model):
    PERSONAL = "PERSONAL"
    BUSINESS = "BUSINESS"
    ACCOUNT_TYPES = (
        (PERSONAL, "Personal Account"),
        (BUSINESS, "Business Account"),
    )

    account_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bank_accounts")
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    phone_number = models.CharField(max_length=32, blank=True, null=True)
    business_display_name = models.CharField(max_length=160, blank=True)
    uen = models.CharField(max_length=32, blank=True, null=True)
    authorised_personal_account = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="authorised_business_accounts",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["owner", "account_type"], name="one_account_type_per_owner"),
            models.UniqueConstraint(
                fields=["phone_number"],
                condition=Q(account_type="PERSONAL"),
                name="unique_personal_phone_number",
            ),
            models.UniqueConstraint(
                fields=["uen"],
                condition=Q(account_type="BUSINESS"),
                name="unique_business_uen",
            ),
            models.CheckConstraint(check=Q(balance__gte=0), name="bank_account_non_negative_balance"),
            models.CheckConstraint(
                check=(
                    Q(account_type="PERSONAL", phone_number__isnull=False, uen__isnull=True, business_display_name="", authorised_personal_account__isnull=True)
                    | Q(account_type="BUSINESS", phone_number__isnull=True, uen__isnull=False, business_display_name__gt="", authorised_personal_account__isnull=False)
                ),
                name="bank_account_type_specific_fields",
            ),
        ]

    def clean(self):
        errors = {}
        if self.balance is not None and self.balance < Decimal("0.00"):
            errors["balance"] = "Account balance cannot be negative."
        if self.account_type == self.PERSONAL:
            if not self.phone_number:
                errors["phone_number"] = "Personal Accounts require a receiving phone number."
            if self.uen:
                errors["uen"] = "Personal Accounts cannot use a UEN."
            if self.business_display_name:
                errors["business_display_name"] = "Personal Accounts cannot have a business display name."
            if self.authorised_personal_account_id:
                errors["authorised_personal_account"] = "Personal Accounts cannot have an authorised Personal Account."
        elif self.account_type == self.BUSINESS:
            if self.phone_number:
                errors["phone_number"] = "Business Accounts do not use phone numbers for receiving transfers."
            if not self.business_display_name:
                errors["business_display_name"] = "Business Accounts require a business display name."
            if not self.uen:
                errors["uen"] = "Business Accounts require a UEN."
            if not self.authorised_personal_account_id:
                errors["authorised_personal_account"] = "Business Accounts require one authorised Personal Account."
            elif self.authorised_personal_account.account_type != self.PERSONAL:
                errors["authorised_personal_account"] = "The authorised account must be a Personal Account."
            elif self.authorised_personal_account.owner_id != self.owner_id:
                errors["authorised_personal_account"] = "The authorised Personal Account must belong to the Business Account owner."
        else:
            errors["account_type"] = "Unsupported account type."
        if errors:
            raise ValidationError(errors)

    @property
    def display_name(self):
        if self.account_type == self.BUSINESS:
            return self.business_display_name
        return self.owner.username

    @property
    def receiving_identifier(self):
        return self.phone_number if self.account_type == self.PERSONAL else self.uen

    def __str__(self):
        return f"{self.get_account_type_display()} - {self.display_name}"


class TransferOperation(models.Model):
    COMPLETED = "COMPLETED"

    transfer_operation_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    sender_account = models.ForeignKey(BankAccount, on_delete=models.PROTECT, related_name="outgoing_transfer_operations")
    recipient_account = models.ForeignKey(BankAccount, on_delete=models.PROTECT, related_name="incoming_transfer_operations")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="SGD", editable=False)
    status = models.CharField(max_length=20, default=COMPLETED)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.transfer_operation_id)


class CompletedTransaction(models.Model):
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    TRANSFER_DEBIT = "TRANSFER_DEBIT"
    TRANSFER_CREDIT = "TRANSFER_CREDIT"
    BUSINESS_OPENING_DEPOSIT = "BUSINESS_OPENING_DEPOSIT"
    COMPLETED = "COMPLETED"
    TRANSACTION_TYPES = (
        (DEPOSIT, "Deposit"),
        (WITHDRAWAL, "Withdrawal"),
        (TRANSFER_DEBIT, "Transfer debit"),
        (TRANSFER_CREDIT, "Transfer credit"),
        (BUSINESS_OPENING_DEPOSIT, "Business opening deposit"),
    )

    transaction_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    account = models.ForeignKey(BankAccount, on_delete=models.PROTECT, related_name="transactions")
    transaction_type = models.CharField(max_length=32, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="SGD", editable=False)
    status = models.CharField(max_length=20, default=COMPLETED, editable=False)
    transfer_operation = models.ForeignKey(
        TransferOperation,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="transactions",
    )
    approval_request = models.ForeignKey(
        "ApprovalRequest",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="completed_transactions",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-completed_at",)

    def __str__(self):
        return f"{self.transaction_type} {self.amount} {self.transaction_id}"


class ApprovalRequest(models.Model):
    BUSINESS_WITHDRAWAL = "BUSINESS_WITHDRAWAL"
    BUSINESS_TRANSFER = "BUSINESS_TRANSFER"
    REQUEST_TYPES = (
        (BUSINESS_WITHDRAWAL, "Business withdrawal"),
        (BUSINESS_TRANSFER, "Business transfer"),
    )

    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"
    STATUSES = (
        (PENDING, "Pending"),
        (COMPLETED, "Completed"),
        (REJECTED, "Rejected"),
        (CANCELLED, "Cancelled"),
        (FAILED, "Failed"),
    )

    request_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    business_account = models.ForeignKey(BankAccount, on_delete=models.PROTECT, related_name="approval_requests")
    authorised_personal_account = models.ForeignKey(BankAccount, on_delete=models.PROTECT, related_name="assigned_approval_requests")
    request_type = models.CharField(max_length=32, choices=REQUEST_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    recipient_account = models.ForeignKey(
        BankAccount,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="incoming_approval_requests",
    )
    recipient_type_snapshot = models.CharField(max_length=20, blank=True)
    recipient_identifier_snapshot = models.CharField(max_length=80, blank=True)
    status = models.CharField(max_length=20, choices=STATUSES, default=PENDING)
    requested_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(blank=True, null=True)
    resolution_note = models.CharField(max_length=255, blank=True)
    completed_transaction = models.ForeignKey(
        CompletedTransaction,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="approval_completion",
    )
    transfer_operation = models.ForeignKey(
        TransferOperation,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="approval_requests",
    )

    class Meta:
        ordering = ("-requested_at",)

    def clean(self):
        errors = {}
        if self.business_account_id and self.business_account.account_type != BankAccount.BUSINESS:
            errors["business_account"] = "Approval requests require a Business Account."
        if self.authorised_personal_account_id and self.authorised_personal_account.account_type != BankAccount.PERSONAL:
            errors["authorised_personal_account"] = "Authoriser must be a Personal Account."
        if self.request_type == self.BUSINESS_TRANSFER and not self.recipient_account_id:
            errors["recipient_account"] = "Business transfer requests require a recipient."
        if self.request_type == self.BUSINESS_WITHDRAWAL and self.recipient_account_id:
            errors["recipient_account"] = "Business withdrawal requests cannot have a recipient."
        if self.amount is not None and self.amount <= Decimal("0.00"):
            errors["amount"] = "Approval request amount must be positive."
        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.request_type} {self.status} {self.request_id}"
