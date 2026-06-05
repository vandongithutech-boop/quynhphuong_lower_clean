from django.db import models
from django.contrib.auth.models import User
from employees.models import Employee


class UserEmployee(models.Model):
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Chờ duyệt"),
        (STATUS_APPROVED, "Đã duyệt"),
        (STATUS_REJECTED, "Từ chối"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="employee_profile",
        verbose_name="Tài khoản"
    )

    employee = models.OneToOneField(
        Employee,
        on_delete=models.CASCADE,
        related_name="user_account",
        verbose_name="Nhân viên"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name="Trạng thái duyệt"
    )

    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="approved_accounts",
        verbose_name="Người duyệt"
    )

    approved_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Ngày duyệt"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.employee.ho_ten}"

    class Meta: 
        db_table = "accounts_user_employee"
        verbose_name = "Tài khoản nhân viên"
        verbose_name_plural = "Tài khoản nhân viên"

from django.contrib.auth.models import Group


class RoleModulePermission(models.Model):
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name="module_permissions"
    )

    module_name = models.CharField(max_length=100)

    can_access = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "accounts_role_module_permission"
        unique_together = ("group", "module_name")
        verbose_name = "Phân quyền module"
        verbose_name_plural = "Phân quyền module"

    def __str__(self):
        return f"{self.group.name} - {self.module_name}"
    
    
class SystemModule(models.Model):
    module_key = models.CharField(max_length=100, unique=True)
    module_label = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "accounts_system_module"
        ordering = ["sort_order", "module_label"]
        verbose_name = "Module hệ thống"
        verbose_name_plural = "Module hệ thống"

    def __str__(self):
        return self.module_label