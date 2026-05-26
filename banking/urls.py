from django.urls import path

from . import views


urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("personal/", views.personal_dashboard, name="personal_dashboard"),
    path("personal/account/", views.personal_account_detail, name="personal_account_detail"),
    path("personal/deposit/", views.personal_deposit, name="personal_deposit"),
    path("personal/withdraw/", views.personal_withdraw, name="personal_withdraw"),
    path("personal/transfer/", views.personal_transfer, name="personal_transfer"),
    path("personal/transactions/", views.personal_transactions, name="personal_transactions"),
    path("business/", views.business_home, name="business_home"),
    path("business/<uuid:account_id>/", views.business_dashboard, name="business_dashboard"),
    path("business/<uuid:account_id>/deposit/", views.business_deposit, name="business_deposit"),
    path("business/<uuid:account_id>/withdraw/", views.business_withdraw_request, name="business_withdraw_request"),
    path("business/<uuid:account_id>/transfer/", views.business_transfer_request, name="business_transfer_request"),
    path("business/<uuid:account_id>/approvals/", views.approvals_list, name="approvals_list"),
    path("business/<uuid:account_id>/approvals/<uuid:request_id>/", views.approvals_detail, name="approvals_detail"),
    path("business/<uuid:account_id>/approvals/<uuid:request_id>/<str:action>/", views.approval_action, name="approval_action"),
    path("business/<uuid:account_id>/invitations/", views.invitations, name="business_invitations"),
    path("business/invitations/<uuid:invitation_id>/accept/", views.accept_invitation_view, name="accept_invitation"),
    path("business/<uuid:account_id>/members/", views.members, name="business_members"),
    path("business/<uuid:account_id>/members/<uuid:membership_id>/<str:action>/", views.member_action, name="member_action"),
    path("business/<uuid:account_id>/transactions/", views.business_transactions, name="business_transactions"),
    path("business/<uuid:account_id>/approval-history/", views.approval_history, name="approval_history"),
    path("business/<uuid:account_id>/access-audit/", views.access_audit, name="access_audit"),
]
