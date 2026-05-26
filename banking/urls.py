from django.urls import path

from . import views


urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("accounts/personal/setup/", views.personal_setup, name="personal_setup"),
    path("accounts/personal/", views.personal_detail, name="personal_detail"),
    path("accounts/business/setup/", views.business_setup, name="business_setup"),
    path("accounts/business/", views.business_detail, name="business_detail"),
    path("deposit/", views.deposit_view, name="deposit"),
    path("withdraw/", views.withdraw_view, name="withdraw"),
    path("transfer/", views.transfer_view, name="transfer"),
    path("approvals/", views.approvals_list, name="approvals"),
    path("approvals/<uuid:request_id>/", views.approval_detail, name="approval_detail"),
    path("transactions/", views.transactions_view, name="transactions"),
]
