from django.urls import path

from . import views


urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("personal/", views.personal_dashboard, name="personal_dashboard"),
    path("personal/account/", views.personal_account_detail, name="personal_account_detail"),
    path("personal/deposit/", views.personal_deposit, name="personal_deposit"),
    path("personal/withdraw/", views.personal_withdraw, name="personal_withdraw"),
    path("personal/transfer/", views.personal_transfer, name="personal_transfer"),
    path("personal/transactions/", views.personal_transaction_history, name="personal_transactions"),
    path("business/", views.business_dashboard, name="business_dashboard"),
    path("business/deposit/", views.business_deposit, name="business_deposit"),
    path("business/withdraw/", views.business_withdraw_request, name="business_withdraw_request"),
    path("business/transfer/", views.business_transfer_request, name="business_transfer_request"),
    path("business/approvals/", views.approvals_list, name="approvals_list"),
    path("business/approvals/<uuid:request_id>/", views.approvals_detail, name="approvals_detail"),
    path("business/approvals/<uuid:request_id>/<str:action>/", views.approval_action, name="approval_action"),
    path("business/team-access/", views.team_access, name="team_access"),
    path("business/team-access/add/", views.add_employee_access, name="add_employee_access"),
    path("business/team-access/<uuid:access_id>/reset-password/", views.reset_employee_password, name="reset_employee_password"),
    path("business/team-access/<uuid:access_id>/promote/", views.promote_employee, name="promote_employee"),
    path("business/team-access/<uuid:access_id>/deactivate/", views.deactivate_employee, name="deactivate_employee"),
    path("business/team-access/<uuid:access_id>/reactivate/", views.reactivate_employee, name="reactivate_employee"),
    path("business/transactions/", views.business_transaction_history, name="business_transactions"),
    path("business/approval-history/", views.approval_history, name="approval_history"),
    path("business/access-audit/", views.access_audit, name="access_audit"),
]
