from django.contrib import admin

from .models import (
    BusinessAccessAuditEvent,
    BusinessAccount,
    BusinessApprovalRequest,
    BusinessInvitation,
    BusinessMembership,
    CompletedFinancialTransaction,
    PersonalAccount,
    TransferOperation,
)


admin.site.register(PersonalAccount)
admin.site.register(BusinessAccount)
admin.site.register(BusinessMembership)
admin.site.register(BusinessInvitation)
admin.site.register(BusinessAccessAuditEvent)
admin.site.register(BusinessApprovalRequest)
admin.site.register(TransferOperation)


@admin.register(CompletedFinancialTransaction)
class CompletedFinancialTransactionAdmin(admin.ModelAdmin):
    list_display = ("transaction_id", "transaction_type", "amount", "completed_at")
    readonly_fields = [field.name for field in CompletedFinancialTransaction._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
