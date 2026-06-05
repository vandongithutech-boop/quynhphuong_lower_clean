from functools import wraps

from django.shortcuts import redirect
from django.contrib import messages
from django.db.utils import OperationalError, ProgrammingError

from .models import RoleModulePermission, SystemModule


ROLE_ADMIN = "ADMIN"
ROLE_SALE = "SALE"
ROLE_KHO = "KHO"
ROLE_PACKING = "PACKING"
ROLE_LOGISTICS = "LOGISTICS"
ROLE_HR = "HR"
ROLE_KE_TOAN = "KE_TOAN"


MODULE_LABELS = {
    "dashboard": "Dashboard",
    "accounts": "Tài khoản",
    "employees": "Nhân sự",
    "customers": "Khách hàng",
    "orders": "Đơn hàng",
    "production": "Sản xuất",
    "categories": "Loại hoa",
    "processing": "Sơ chế",
    "inventory": "Kho tổng",
    "transport": "Vận chuyển",
    "finance": "Doanh thu",
    "reports": "Báo cáo",
}


DEFAULT_MODULE_PERMISSIONS = {
    "dashboard": [ROLE_ADMIN, ROLE_KE_TOAN],
    "accounts": [ROLE_ADMIN],

    "employees": [ROLE_ADMIN, ROLE_HR],
    "customers": [ROLE_ADMIN, ROLE_HR, ROLE_KE_TOAN],

    "orders": [ROLE_ADMIN, ROLE_KHO, ROLE_KE_TOAN],
    "production": [ROLE_ADMIN, ROLE_KHO, ROLE_PACKING, ROLE_LOGISTICS, ROLE_KE_TOAN],

    "categories": [ROLE_ADMIN, ROLE_SALE, ROLE_KHO, ROLE_HR, ROLE_KE_TOAN],
    "processing": [ROLE_ADMIN, ROLE_KHO, ROLE_HR, ROLE_KE_TOAN],
    "inventory": [ROLE_ADMIN, ROLE_SALE, ROLE_KHO, ROLE_PACKING, ROLE_KE_TOAN],
    "transport": [ROLE_ADMIN, ROLE_KHO, ROLE_PACKING, ROLE_LOGISTICS, ROLE_KE_TOAN],

    "finance": [ROLE_ADMIN],
    "reports": [ROLE_ADMIN],
}


def user_has_role(user, roles):
    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    return user.groups.filter(name__in=roles).exists()


def can_access_module(user, module_name):
    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    user_groups = user.groups.values_list("name", flat=True)

    try:
        has_dynamic_permission = RoleModulePermission.objects.exists()

        if has_dynamic_permission:
            return RoleModulePermission.objects.filter(
                group__name__in=user_groups,
                module_name=module_name,
                can_access=True
            ).exists()

    except (OperationalError, ProgrammingError):
        pass

    allowed_roles = DEFAULT_MODULE_PERMISSIONS.get(module_name, [])
    return user_has_role(user, allowed_roles)


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("accounts:login")

            if user_has_role(request.user, roles):
                return view_func(request, *args, **kwargs)

            messages.error(request, "Bạn không có quyền truy cập chức năng này.")
            return redirect("dashboard:dashboard")

        return wrapper

    return decorator


def module_required(module_name):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("accounts:login")

            if can_access_module(request.user, module_name):
                return view_func(request, *args, **kwargs)

            messages.error(request, "Bạn không có quyền truy cập khu vực này.")
            return redirect("dashboard:dashboard")

        return wrapper

    return decorator

def get_system_modules():
    try:
        modules = SystemModule.objects.filter(is_active=True).order_by("sort_order", "module_label")

        if modules.exists():
            return {
                item.module_key: item.module_label
                for item in modules
            }

    except Exception:
        pass

    return MODULE_LABELS