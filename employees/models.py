from django.db import models


class Employee(models.Model):
    ma_nv = models.CharField(max_length=50, unique=True, verbose_name="Mã NV")
    ho_ten = models.CharField(max_length=255, verbose_name="Họ và tên")
    gioi_tinh = models.CharField(max_length=20, blank=True, null=True, verbose_name="Giới tính")
    sdt = models.CharField(max_length=30, blank=True, null=True, verbose_name="SĐT")
    bo_phan = models.CharField(max_length=100, blank=True, null=True, verbose_name="Bộ phận")
    chuc_vu = models.CharField(max_length=100, blank=True, null=True, verbose_name="Chức vụ")
    dia_chi = models.TextField(blank=True, null=True, verbose_name="Địa chỉ")
    ngay_vao_lam = models.DateField(blank=True, null=True, verbose_name="Ngày vào làm")
    trang_thai = models.CharField(max_length=50, default="Đang làm", verbose_name="Trạng thái")
    ghi_chu = models.TextField(blank=True, null=True, verbose_name="Ghi chú")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    def __str__(self):
        return f"{self.ma_nv} - {self.ho_ten}"

    class Meta:
        db_table = "employees_employee"
        verbose_name = "Nhân sự"
        verbose_name_plural = "Danh sách nhân sự"
        ordering = ["ho_ten"]