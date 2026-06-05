from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),

    path("pending/", views.pending_accounts_view, name="pending_accounts"),
    path("approve/<int:account_id>/", views.approve_account_view, name="approve_account"),
    path("reject/<int:account_id>/", views.reject_account_view, name="reject_account"),

    path("update-group/<int:account_id>/", views.update_account_group_view, name="update_account_group"),
    path("delete/<int:account_id>/", views.delete_account_view, name="delete_account"),
    path("permissions/update/", views.update_role_permissions_view, name="update_role_permissions"),
    path("permissions/module/create/", views.create_system_module_view, name="create_system_module"),
]