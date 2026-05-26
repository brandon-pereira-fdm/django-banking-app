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
        constraints = [
            models.CheckConstraint(check=Q(balance__gte=0), name="personal_account_non_negative_balance"),
        ]

    def clean(self):
        if self.owner_id and self.owner.access_context != "PERSONAL":
            raise ValidationError({"owner": "Only Personal users may own a Personal Account."})
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
        constraints = [
            models.CheckConstraint(check=Q(balance__gte=0), name="business_account_non_negative_balance"),
        ]

    @property
    def display_name(self):
        return self.business_display_name

    @property
    def receiving_identifier(self):
        return self.uen

    def __str__(self):
        return self.business_display_name


class BusinessMembership(models.Model):
    MEMBER = "MEMBER"
    AUTHORISER = "AUTHORISER"
    ROLE_CHOICES = (
        (MEMBER, "Member"),
        (AUTHORISER, "Authoriser"),
    )

    membership_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    business_account = models.ForeignKey(BusinessAccount, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="business_memberships")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    removed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ("business_account__business_display_name", "user__email")
        constraints = [
            models.UniqueConstraint(
                fields=["business_account", "user"],
                condition=Q(is_active=True),
                name="one_active_business_membership_per_user_account",
            ),
        ]

    def clean(self):
        if self.user_id and self.user.access_context != "BUSINESS":
            raise ValidationError({"user": "Only Business users may hold Business memberships."})
        if self.role not in {self.MEMBER, self.AUTHORISER}:
            raise ValidationError({"role": "Unsupported Business membership role."})

    def __str__(self):
        return f"{self.user.email} {self.role} at {self.business_account}"


class BusinessInvitation(models.Model):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    CANCELLED = "CANCELLED"
    STATUS_CHOICES = (
        (PENDING, "Pending"),
        (ACCEPTED, "Accepted"),
        (CANCELLED, "Cancelled"),
    )

    invitation_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    business_account = models.ForeignKey(BusinessAccount, on_delete=models.CASCADE, related_name="invitations")
    invited_email = models.EmailField()
    intended_role = models.CharField(max_length=20, choices=BusinessMembership.ROLE_CHOICES)
    inviting_membership = models.ForeignKey(
        BusinessMembership,
        on_delete=models.PROTECT,
        related_name="issued_invitations",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    issued_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(blank=True, null=True)
    accepted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="accepted_business_invitations",
    )

    class Meta:
        ordering = ("-issued_at",)
        constraints = [
            models.UniqueConstraint(
                fields=["business_account", "invited_email"],
                condition=Q(status="PENDING"),
                name="one_pending_invitation_per_email_business",
            ),
        ]

    def clean(self):
        if self.inviting_membership_id and self.inviting_membership.role != BusinessMembership.AUTHORISER:
            raise ValidationError({"inviting_membership": "Only AUTHORISERS may issue invitations."})
        if self.accepted_by_id and self.accepted_by.access_context != "BUSINESS":
            raise ValidationError({"accepted_by": "Only Business users may accept Business invitations."})

    def __str__(self):
        return f"{self.invited_email} invited to {self.business_account}"


class BusinessAccessAuditEvent(models.Model):
    BUSINESS_ACCOUNT_CREATED = "BUSINESS_ACCOUNT_CREATED"
    INITIAL_AUTHORISER_ASSIGNED = "INITIAL_AUTHORISER_ASSIGNED"
    INVITATION_ISSUED = "INVITATION_ISSUED"
    INVITATION_ACCEPTED = "INVITATION_ACCEPTED"
    MEMBER_PROMOTED_TO_AUTHORISER = "MEMBER_PROMOTED_TO_AUTHORISER"
    MEMBER_REMOVED = "MEMBER_REMOVED"
    AUTHORISER_REMOVED = "AUTHORISER_REMOVED"
    LAST_AUTHORISER_REMOVAL_REJECTED = "LAST_AUTHORISER_REMOVAL_REJECTED"
    EVENT_CHOICES = (
        (BUSINESS_ACCOUNT_CREATED, "Business account created"),
        (INITIAL_AUTHORISER_ASSIGNED, "Initial authoriser assigned"),
        (INVITATION_ISSUED, "Invitation issued"),
        (INVITATION_ACCEPTED, "Invitation accepted"),
        (MEMBER_PROMOTED_TO_AUTHORISER, "Member promoted to authoriser"),
        (MEMBER_REMOVED, "Member removed"),
        (AUTHORISER_REMOVED, "Authoriser removed"),
        (LAST_AUTHORISER_REMOVAL_REJECTED, "Last authoriser removal rejected"),
    )

    SUCCESS = "SUCCESS"
    REJECTED = "REJECTED"
    OUTCOME_CHOICES = (
        (SUCCESS, "Success"),
        (REJECTED, "Rejected"),
    )

    event_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    business_account = models.ForeignKey(BusinessAccount, on_delete=models.CASCADE, related_name="access_audit_events")
    acting_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="business_access_audit_actions",
    )
    affected_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="business_access_audit_subjects",
    )
    invited_email = models.EmailField(blank=True)
    role = models.CharField(max_length=20, blank=True)
    event_type = models.CharField(max_length=64, choices=EVENT_CHOICES)
    outcome = models.CharField(max_length=20, choices=OUTCOME_CHOICES, default=SUCCESS)
    details = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.event_type} {self.event_id}"


class TransferOperation(models.Model):
    transfer_operation_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
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

    class Meta:
        ordering = ("-completed_at",)
        constraints = [
            models.CheckConstraint(check=Q(amount__gt=0), name="transfer_operation_positive_amount"),
        ]

    def clean(self):
        sender_count = int(bool(self.sender_personal_account_id)) + int(bool(self.sender_business_account_id))
        recipient_count = int(bool(self.recipient_personal_account_id)) + int(bool(self.recipient_business_account_id))
        if sender_count != 1:
            raise ValidationError("Transfer operations require exactly one sender account.")
        if recipient_count != 1:
            raise ValidationError("Transfer operations require exactly one recipient account.")
        if self.sender_personal_account_id and self.recipient_personal_account_id == self.sender_personal_account_id:
            raise ValidationError("Self-transfers are not supported.")
        if self.sender_business_account_id and self.recipient_business_account_id == self.sender_business_account_id:
            raise ValidationError("Self-transfers are not supported.")

    @property
    def sender_account(self):
        return self.sender_personal_account or self.sender_business_account

    @property
    def recipient_account(self):
        return self.recipient_personal_account or self.recipient_business_account

    def __str__(self):
        return str(self.transfer_operation_id)


class BusinessApprovalRequest(models.Model):
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
    business_account = models.ForeignKey(BusinessAccount, on_delete=models.PROTECT, related_name="approval_requests")
    requesting_membership = models.ForeignKey(
        BusinessMembership,
        on_delete=models.PROTECT,
        related_name="submitted_approval_requests",
    )
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="submitted_business_requests")
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
    requested_at = models.DateTimeField(auto_now_add=True)
    actioning_membership = models.ForeignKey(
        BusinessMembership,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="actioned_approval_requests",
    )
    actioned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="actioned_business_requests",
    )
    resolved_at = models.DateTimeField(blank=True, null=True)
    resolution_note = models.CharField(max_length=255, blank=True)
    completed_transaction = models.ForeignKey(
        "CompletedFinancialTransaction",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="completed_withdrawal_requests",
    )
    transfer_operation = models.ForeignKey(
        TransferOperation,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="business_approval_requests",
    )

    class Meta:
        ordering = ("-requested_at",)
        constraints = [
            models.CheckConstraint(check=Q(amount__gt=0), name="business_approval_request_positive_amount"),
        ]

    def clean(self):
        if self.requesting_membership_id:
            if not self.requesting_membership.is_active:
                raise ValidationError({"requesting_membership": "Requester membership must be active."})
            if self.requesting_membership.business_account_id != self.business_account_id:
                raise ValidationError({"requesting_membership": "Requester must belong to the Business Account."})
        recipient_count = int(bool(self.recipient_personal_account_id)) + int(bool(self.recipient_business_account_id))
        if self.request_type == self.BUSINESS_TRANSFER and recipient_count != 1:
            raise ValidationError("Business transfer requests require exactly one recipient.")
        if self.request_type == self.BUSINESS_WITHDRAWAL and recipient_count:
            raise ValidationError("Business withdrawal requests cannot have recipients.")

    def __str__(self):
        return f"{self.request_type} {self.status} {self.request_id}"


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
    transfer_operation = models.ForeignKey(
        TransferOperation,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="completed_transactions",
    )
    business_approval_request = models.ForeignKey(
        BusinessApprovalRequest,
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
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-completed_at",)
        constraints = [
            models.CheckConstraint(check=Q(amount__gt=0), name="completed_financial_transaction_positive_amount"),
        ]

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
