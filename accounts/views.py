from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie


from .forms import EmployeeSelfRegisterForm, ApproveAccountForm
from .models import UserEmployee, SystemModule
from .permissions import MODULE_LABELS, DEFAULT_MODULE_PERMISSIONS, get_system_modules
from .models import RoleModulePermission

def is_admin_user(user):
    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    return user.groups.filter(name="ADMIN").exists()


@ensure_csrf_cookie
def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:dashboard")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)

            next_url = request.GET.get("next")

            if next_url:
                return redirect(next_url)

            return redirect("dashboard:dashboard")

        messages.error(
            request,
            "Tên đăng nhập hoặc mật khẩu không đúng hoặc tài khoản chưa được duyệt."
        )

    return render(request, "accounts/login.html")


@ensure_csrf_cookie
def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:dashboard")

    if request.method == "POST":
        form = EmployeeSelfRegisterForm(request.POST)

        if form.is_valid():
            employee = form.cleaned_data["employee"]
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password1"]

            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=employee.ho_ten,
                is_active=False,
            )

            UserEmployee.objects.create(
                user=user,
                employee=employee,
                status=UserEmployee.STATUS_PENDING
            )

            messages.success(
                request,
                "Đăng ký thành công. Vui lòng chờ admin duyệt tài khoản."
            )

            return redirect("accounts:login")

    else:
        form = EmployeeSelfRegisterForm()

    return render(request, "accounts/register.html", {
        "form": form
    })

@login_required
def logout_view(request):
    logout(request)
    return redirect("accounts:login")

@login_required
def pending_accounts_view(request):
    if not is_admin_user(request.user):
        messages.error(request, "Bạn không có quyền truy cập trang này.")
        return redirect("dashboard:dashboard")

    pending_accounts = (
        UserEmployee.objects
        .select_related("user", "employee")
        .filter(status=UserEmployee.STATUS_PENDING)
        .order_by("-created_at")
    )

    approved_accounts = (
        UserEmployee.objects
        .select_related("user", "employee", "approved_by")
        .filter(status=UserEmployee.STATUS_APPROVED)
        .order_by("-approved_at", "-created_at")
    )

    groups = Group.objects.all().order_by("name")

    role_names = [
        "ADMIN",
        "SALE",
        "KHO",
        "PACKING",
        "LOGISTICS",
        "HR",
        "KE_TOAN",
    ]

    module_rows = []

    system_modules = get_system_modules()

    for module_key, module_label in system_modules.items():
        role_items = []

        for role_name in role_names:
            group = Group.objects.filter(name=role_name).first()

            checked = False

            if RoleModulePermission.objects.exists():
                checked = RoleModulePermission.objects.filter(
                    group__name=role_name,
                    module_name=module_key,
                    can_access=True
                ).exists()
            else:
                checked = role_name in DEFAULT_MODULE_PERMISSIONS.get(module_key, [])

            role_items.append({
                "role": role_name,
                "checked": checked,
                "value": f"{role_name}|{module_key}",
            })

        module_rows.append({
            "key": module_key,
            "label": module_label,
            "roles": role_items,
        })

    return render(request, "accounts/pending_accounts.html", {
        "pending_accounts": pending_accounts,
        "approved_accounts": approved_accounts,
        "groups": groups,
        "module_rows": module_rows,
        "role_names": role_names,
    })


@login_required
def approve_account_view(request, account_id):
    if not is_admin_user(request.user):
        messages.error(request, "Bạn không có quyền duyệt tài khoản.")
        return redirect("dashboard:dashboard")

    account = get_object_or_404(
        UserEmployee,
        id=account_id,
        status=UserEmployee.STATUS_PENDING
    )

    if request.method == "POST":
        group_id = request.POST.get("group")
        group = get_object_or_404(Group, id=group_id)

        user = account.user
        user.is_active = True
        user.groups.clear()
        user.groups.add(group)
        user.save()

        account.status = UserEmployee.STATUS_APPROVED
        account.approved_by = request.user
        account.approved_at = timezone.now()
        account.save()

        messages.success(request, f"Đã duyệt tài khoản {user.username} thành công.")

    return redirect("accounts:pending_accounts")

@login_required
def reject_account_view(request, account_id):
    if not is_admin_user(request.user):
        messages.error(request, "Bạn không có quyền từ chối tài khoản.")
        return redirect("dashboard:dashboard")

    account = get_object_or_404(
        UserEmployee,
        id=account_id,
        status=UserEmployee.STATUS_PENDING
    )

    account.status = UserEmployee.STATUS_REJECTED
    account.save()

    user = account.user
    user.is_active = False
    user.save()

    messages.success(
        request,
        f"Đã từ chối tài khoản {user.username}."
    )

    return redirect("accounts:pending_accounts")

@login_required
def update_account_group_view(request, account_id):
    if not is_admin_user(request.user):
        messages.error(request, "Bạn không có quyền sửa tài khoản.")
        return redirect("dashboard:dashboard")

    account = get_object_or_404(
        UserEmployee,
        id=account_id,
        status=UserEmployee.STATUS_APPROVED
    )

    if request.method == "POST":
        group_id = request.POST.get("group")
        group = get_object_or_404(Group, id=group_id)

        account.user.groups.clear()
        account.user.groups.add(group)

        messages.success(
            request,
            f"Đã cập nhật quyền cho tài khoản {account.user.username}."
        )

    return redirect("accounts:pending_accounts")


@login_required
def delete_account_view(request, account_id):
    if not is_admin_user(request.user):
        messages.error(request, "Bạn không có quyền xóa tài khoản.")
        return redirect("dashboard:dashboard")

    account = get_object_or_404(UserEmployee, id=account_id)

    if request.method == "POST":
        username = account.user.username
        account.user.delete()

        messages.success(request, f"Đã xóa tài khoản {username}.")

    return redirect("accounts:pending_accounts")


@login_required
def update_role_permissions_view(request):
    if not is_admin_user(request.user):
        messages.error(request, "Bạn không có quyền cài đặt phân quyền.")
        return redirect("dashboard:dashboard")

    if request.method == "POST":
        selected_permissions = request.POST.getlist("permissions")

        system_modules = get_system_modules()
        module_keys = list(system_modules.keys())

        role_names = [
            "ADMIN",
            "SALE",
            "KHO",
            "PACKING",
            "LOGISTICS",
            "HR",
            "KE_TOAN",
        ]

        RoleModulePermission.objects.filter(
            module_name__in=module_keys,
            group__name__in=role_names,
        ).delete()

        for item in selected_permissions:
            role_name, module_name = item.split("|")

            group = Group.objects.filter(name=role_name).first()

            if group:
                RoleModulePermission.objects.update_or_create(
                    group=group,
                    module_name=module_name,
                    defaults={"can_access": True}
                )

        messages.success(request, "Đã cập nhật phân quyền hệ thống.")

    return redirect("accounts:pending_accounts")

@login_required
def create_system_module_view(request):
    if not is_admin_user(request.user):
        messages.error(request, "Bạn không có quyền thêm module.")
        return redirect("dashboard:dashboard")

    if request.method == "POST":
        module_key = request.POST.get("module_key", "").strip()
        module_label = request.POST.get("module_label", "").strip()
        sort_order = request.POST.get("sort_order") or 0

        if not module_key or not module_label:
            messages.error(request, "Vui lòng nhập đủ mã module và tên hiển thị.")
            return redirect("accounts:pending_accounts")

        SystemModule.objects.get_or_create(
            module_key=module_key,
            defaults={
                "module_label": module_label,
                "sort_order": sort_order,
                "is_active": True,
            }
        )

        messages.success(request, "Đã thêm module phân quyền mới.")

    return redirect("accounts:pending_accounts")