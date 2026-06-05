from django.contrib import admin
from .models import Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        "ma_nv",
        "ho_ten",
        "gioi_tinh",
        "sdt",
        "bo_phan",
        "chuc_vu",
        "trang_thai",
        "ngay_vao_lam",
    )

    search_fields = (
        "ma_nv",
        "ho_ten",
        "sdt",
        "bo_phan",
        "chuc_vu",
    )

    list_filter = (
        "gioi_tinh",
        "bo_phan",
        "chuc_vu",
        "trang_thai",
    )

    ordering = ("ho_ten",)