from django.contrib import admin

from .models import ApprovalRequest, BankAccount, CompletedTransaction, TransferOperation


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ("account_id", "owner", "account_type", "balance", "phone_number", "uen")
    list_filter = ("account_type",)
    search_fields = ("owner__email", "owner__username", "phone_number", "uen", "business_display_name")


@admin.register(CompletedTransaction)
class CompletedTransactionAdmin(admin.ModelAdmin):
    list_display = ("transaction_id", "account", "transaction_type", "amount", "status", "completed_at")
    readonly_fields = [field.name for field in CompletedTransaction._meta.fields]
    list_filter = ("transaction_type", "status")
    search_fields = ("transaction_id", "transfer_operation__transfer_operation_id")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(TransferOperation)
class TransferOperationAdmin(admin.ModelAdmin):
    list_display = ("transfer_operation_id", "sender_account", "recipient_account", "amount", "completed_at")
    readonly_fields = [field.name for field in TransferOperation._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ApprovalRequest)
class ApprovalRequestAdmin(admin.ModelAdmin):
    list_display = ("request_id", "business_account", "request_type", "amount", "status", "requested_at")
    readonly_fields = ("request_id", "requested_at", "resolved_at")
    list_filter = ("request_type", "status")
