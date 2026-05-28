import uuid
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


class PersonalAccount(models.Model):
    account_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="personal_account")
    phone_number = models.CharField(max_length=32, unique=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_at",)
        constraints = [models.CheckConstraint(check=Q(balance__gte=0), name="personal_account_non_negative_balance")]

    def clean(self):
        if self.owner_id and self.owner.login_context != "PERSONAL":
            raise ValidationError({"owner": "Only Personal logins may own Personal Accounts."})
        if self.balance is not None and self.balance < Decimal("0.00"):
            raise ValidationError({"balance": "Personal Account balance cannot be negative."})

    @property
    def display_name(self):
        return self.owner.username

    @property
    def receiving_identifier(self):
        return self.phone_number

    def __str__(self):
        return f"Personal Account {self.phone_number}"


class BusinessAccount(models.Model):
    account_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    business_display_name = models.CharField(max_length=160)
    uen = models.CharField(max_length=32, unique=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("business_display_name",)
        constraints = [models.CheckConstraint(check=Q(balance__gte=0), name="business_account_non_negative_balance")]

    @property
    def display_name(self):
        return self.business_display_name

    @property
    def receiving_identifier(self):
        return self.uen

    def __str__(self):
        return self.business_display_name


class BusinessEmployeeAccess(models.Model):
    MEMBER = "MEMBER"
    AUTHORISER = "AUTHORISER"
    ROLE_CHOICES = ((MEMBER, "Member"), (AUTHORISER, "Authoriser"))

    PASSWORD_CHANGE_REQUIRED = "PASSWORD_CHANGE_REQUIRED"
    ACTIVE = "ACTIVE"
    DEACTIVATED = "DEACTIVATED"
    STATUS_CHOICES = (
        (PASSWORD_CHANGE_REQUIRED, "Password Change Required"),
        (ACTIVE, "Active"),
        (DEACTIVATED, "Deactivated"),
    )

    access_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="business_access")
    business_account = models.ForeignKey(BusinessAccount, on_delete=models.CASCADE, related_name="employee_accesses")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    access_status = models.CharField(max_length=32, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    activated_at = models.DateTimeField(blank=True, null=True)
    deactivated_at = models.DateTimeField(blank=True, null=True)
    deactivated_by = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="deactivated_employee_accesses",
    )
    reactivated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ("business_account__business_display_name", "user__email")

    def clean(self):
        if self.user_id and self.user.login_context != "BUSINESS_EMPLOYEE":
            raise ValidationError({"user": "Only Business Employee logins may have employee access."})
        if self.role not in {self.MEMBER, self.AUTHORISER}:
            raise ValidationError({"role": "Unsupported Business role."})
        if self.access_status not in {self.PASSWORD_CHANGE_REQUIRED, self.ACTIVE, self.DEACTIVATED}:
            raise ValidationError({"access_status": "Unsupported employee access status."})

    @property
    def is_active_access(self):
        return self.access_status == self.ACTIVE

    def __str__(self):
        return f"{self.user.email} {self.role} at {self.business_account}"


class BusinessOutgoingRequest(models.Model):
    BUSINESS_WITHDRAWAL = "BUSINESS_WITHDRAWAL"
    BUSINESS_TRANSFER = "BUSINESS_TRANSFER"
    REQUEST_TYPE_CHOICES = (
        (BUSINESS_WITHDRAWAL, "Business withdrawal"),
        (BUSINESS_TRANSFER, "Business transfer"),
    )

    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"
    STATUS_CHOICES = (
        (PENDING, "Pending"),
        (COMPLETED, "Completed"),
        (REJECTED, "Rejected"),
        (CANCELLED, "Cancelled"),
        (FAILED, "Failed"),
    )
    TERMINAL_STATUSES = {COMPLETED, REJECTED, CANCELLED, FAILED}

    request_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    business_account = models.ForeignKey(BusinessAccount, on_delete=models.PROTECT, related_name="outgoing_requests")
    requested_by = models.ForeignKey(
        BusinessEmployeeAccess,
        on_delete=models.PROTECT,
        related_name="submitted_outgoing_requests",
    )
    request_type = models.CharField(max_length=32, choices=REQUEST_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    recipient_personal_account = models.ForeignKey(
        PersonalAccount,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="incoming_business_transfer_requests",
    )
    recipient_business_account = models.ForeignKey(
        BusinessAccount,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="incoming_business_transfer_requests",
    )
    recipient_type_snapshot = models.CharField(max_length=20, blank=True)
    recipient_identifier_snapshot = models.CharField(max_length=80, blank=True)
    recipient_name_snapshot = models.CharField(max_length=160, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    actioned_by = models.ForeignKey(
        BusinessEmployeeAccess,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="actioned_outgoing_requests",
    )
    requested_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(blank=True, null=True)
    safe_reason = models.CharField(max_length=255, blank=True)
    completed_transaction = models.ForeignKey(
        "CompletedFinancialTransaction",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="completed_business_requests",
    )
    transfer_operation = models.ForeignKey(
        "TransferOperation",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="business_outgoing_requests",
    )

    class Meta:
        ordering = ("-requested_at",)
        constraints = [models.CheckConstraint(check=Q(amount__gt=0), name="business_outgoing_request_positive_amount")]

    def clean(self):
        if self.requested_by_id and self.requested_by.business_account_id != self.business_account_id:
            raise ValidationError({"requested_by": "Requester must belong to the Business Account."})
        if self.actioned_by_id and self.actioned_by.business_account_id != self.business_account_id:
            raise ValidationError({"actioned_by": "Actioning employee must belong to the Business Account."})
        recipient_count = int(bool(self.recipient_personal_account_id)) + int(bool(self.recipient_business_account_id))
        if self.request_type == self.BUSINESS_TRANSFER and recipient_count != 1:
            raise ValidationError("Business transfer requests require exactly one recipient.")
        if self.request_type == self.BUSINESS_WITHDRAWAL and recipient_count:
            raise ValidationError("Business withdrawal requests cannot have recipients.")

    def __str__(self):
        return f"{self.request_type} {self.status} {self.request_id}"


class TransferOperation(models.Model):
    operation_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    sender_personal_account = models.ForeignKey(
        PersonalAccount,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="outgoing_transfer_operations",
    )
    sender_business_account = models.ForeignKey(
        BusinessAccount,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="outgoing_transfer_operations",
    )
    recipient_personal_account = models.ForeignKey(
        PersonalAccount,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="incoming_transfer_operations",
    )
    recipient_business_account = models.ForeignKey(
        BusinessAccount,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="incoming_transfer_operations",
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    completed_at = models.DateTimeField(auto_now_add=True)
    business_outgoing_request = models.ForeignKey(
        BusinessOutgoingRequest,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="completed_transfer_operations",
    )

    class Meta:
        ordering = ("-completed_at",)
        constraints = [models.CheckConstraint(check=Q(amount__gt=0), name="transfer_operation_positive_amount")]

    def clean(self):
        sender_count = int(bool(self.sender_personal_account_id)) + int(bool(self.sender_business_account_id))
        recipient_count = int(bool(self.recipient_personal_account_id)) + int(bool(self.recipient_business_account_id))
        if sender_count != 1:
            raise ValidationError("Transfer operations require exactly one sender account.")
        if recipient_count != 1:
            raise ValidationError("Transfer operations require exactly one recipient account.")
        if self.sender_personal_account_id and self.sender_personal_account_id == self.recipient_personal_account_id:
            raise ValidationError("Transfers to the same account are not supported.")
        if self.sender_business_account_id and self.sender_business_account_id == self.recipient_business_account_id:
            raise ValidationError("Transfers to the same account are not supported.")

    @property
    def sender_account(self):
        return self.sender_personal_account or self.sender_business_account

    @property
    def recipient_account(self):
        return self.recipient_personal_account or self.recipient_business_account

    def __str__(self):
        return str(self.operation_id)


class CompletedFinancialTransaction(models.Model):
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    TRANSFER_DEBIT = "TRANSFER_DEBIT"
    TRANSFER_CREDIT = "TRANSFER_CREDIT"
    BUSINESS_OPENING_DEPOSIT = "BUSINESS_OPENING_DEPOSIT"
    TRANSACTION_TYPE_CHOICES = (
        (DEPOSIT, "Deposit"),
        (WITHDRAWAL, "Withdrawal"),
        (TRANSFER_DEBIT, "Transfer debit"),
        (TRANSFER_CREDIT, "Transfer credit"),
        (BUSINESS_OPENING_DEPOSIT, "Business opening deposit"),
    )

    transaction_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    personal_account = models.ForeignKey(
        PersonalAccount,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="completed_transactions",
    )
    business_account = models.ForeignKey(
        BusinessAccount,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="completed_transactions",
    )
    transaction_type = models.CharField(max_length=32, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    completed_at = models.DateTimeField(auto_now_add=True)
    transfer_operation = models.ForeignKey(
        TransferOperation,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="completed_transactions",
    )
    business_outgoing_request = models.ForeignKey(
        BusinessOutgoingRequest,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="completed_financial_transactions",
    )
    actor_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="performed_financial_transactions",
    )
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ("-completed_at",)
        constraints = [models.CheckConstraint(check=Q(amount__gt=0), name="completed_financial_transaction_positive_amount")]

    def clean(self):
        account_count = int(bool(self.personal_account_id)) + int(bool(self.business_account_id))
        if account_count != 1:
            raise ValidationError("Completed financial transactions require exactly one account.")
        if self.transaction_type in {self.TRANSFER_DEBIT, self.TRANSFER_CREDIT} and not self.transfer_operation_id:
            raise ValidationError({"transfer_operation": "Transfer transactions require a Transfer Operation."})

    @property
    def account(self):
        return self.personal_account or self.business_account

    def __str__(self):
        return f"{self.transaction_type} {self.amount} {self.transaction_id}"


class AccessAuditEvent(models.Model):
    BUSINESS_ACCOUNT_CREATED = "BUSINESS_ACCOUNT_CREATED"
    INITIAL_AUTHORISER_CREATED = "INITIAL_AUTHORISER_CREATED"
    EMPLOYEE_ACCESS_CREATED = "EMPLOYEE_ACCESS_CREATED"
    TEMPORARY_PASSWORD_ISSUED = "TEMPORARY_PASSWORD_ISSUED"
    PASSWORD_CHANGE_COMPLETED = "PASSWORD_CHANGE_COMPLETED"
    EMPLOYEE_ACTIVATED = "EMPLOYEE_ACTIVATED"
    TEMPORARY_PASSWORD_RESET = "TEMPORARY_PASSWORD_RESET"
    MEMBER_PROMOTED_TO_AUTHORISER = "MEMBER_PROMOTED_TO_AUTHORISER"
    EMPLOYEE_DEACTIVATED = "EMPLOYEE_DEACTIVATED"
    EMPLOYEE_REACTIVATED = "EMPLOYEE_REACTIVATED"
    FINAL_AUTHORISER_DEACTIVATION_REJECTED = "FINAL_AUTHORISER_DEACTIVATION_REJECTED"
    EVENT_CHOICES = (
        (BUSINESS_ACCOUNT_CREATED, "Business Account created"),
        (INITIAL_AUTHORISER_CREATED, "Initial AUTHORISER created"),
        (EMPLOYEE_ACCESS_CREATED, "Employee access created"),
        (TEMPORARY_PASSWORD_ISSUED, "Temporary password issued"),
        (PASSWORD_CHANGE_COMPLETED, "Password change completed"),
        (EMPLOYEE_ACTIVATED, "Employee activated"),
        (TEMPORARY_PASSWORD_RESET, "Temporary password reset"),
        (MEMBER_PROMOTED_TO_AUTHORISER, "Member promoted to Authoriser"),
        (EMPLOYEE_DEACTIVATED, "Employee deactivated"),
        (EMPLOYEE_REACTIVATED, "Employee reactivated"),
        (FINAL_AUTHORISER_DEACTIVATION_REJECTED, "Final Authoriser deactivation rejected"),
    )

    SUCCESS = "SUCCESS"
    REJECTED = "REJECTED"
    OUTCOME_CHOICES = ((SUCCESS, "Success"), (REJECTED, "Rejected"))

    event_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    business_account = models.ForeignKey(BusinessAccount, on_delete=models.CASCADE, related_name="access_audit_events")
    acting_employee = models.ForeignKey(
        BusinessEmployeeAccess,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="access_audit_actions",
    )
    affected_employee = models.ForeignKey(
        BusinessEmployeeAccess,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="access_audit_subjects",
    )
    event_type = models.CharField(max_length=64, choices=EVENT_CHOICES)
    previous_role = models.CharField(max_length=20, blank=True)
    new_role = models.CharField(max_length=20, blank=True)
    previous_status = models.CharField(max_length=32, blank=True)
    new_status = models.CharField(max_length=32, blank=True)
    outcome = models.CharField(max_length=20, choices=OUTCOME_CHOICES, default=SUCCESS)
    safe_metadata = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def clean(self):
        forbidden = ("password", "hash", "secret")
        text = (self.safe_metadata or "").lower()
        if any(word in text for word in forbidden):
            raise ValidationError({"safe_metadata": "Audit metadata must not include password or secret content."})

    def __str__(self):
        return f"{self.event_type} {self.event_id}"
