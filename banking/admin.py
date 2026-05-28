from django.contrib import admin

from .models import (
    AccessAuditEvent,
    BusinessAccount,
    BusinessEmployeeAccess,
    BusinessOutgoingRequest,
    CompletedFinancialTransaction,
    PersonalAccount,
    TransferOperation,
)


admin.site.register(PersonalAccount)
admin.site.register(BusinessAccount)
admin.site.register(BusinessEmployeeAccess)
admin.site.register(BusinessOutgoingRequest)
admin.site.register(TransferOperation)
admin.site.register(AccessAuditEvent)


@admin.register(CompletedFinancialTransaction)
class CompletedFinancialTransactionAdmin(admin.ModelAdmin):
    list_display = ("transaction_id", "transaction_type", "amount", "completed_at")
    readonly_fields = [field.name for field in CompletedFinancialTransaction._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
