from django.urls import path

from . import views


urlpatterns = [
    path("", views.account_type_selection, name="account_type_selection"),
    path("register/personal/", views.register_personal, name="register_personal"),
    path("register/business/", views.register_business, name="register_business"),
    path("register/business/invitation/<uuid:invitation_id>/", views.register_business_invited, name="register_business_invited"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
]
