from django.db import models
from django.utils import timezone
from traceability.models import TraceLot

class Order(models.Model):
    STATUS_CHOICES = [
        ("new", "Mới tạo"),
        ("processing", "Đang xử lý"),
        ("completed", "Hoàn thành"),
        ("cancelled", "Đã huỷ"),
    ]

    order_code = models.CharField(max_length=50, unique=True, verbose_name="Mã đơn hàng")

    customer_code = models.CharField(max_length=100, blank=True, null=True, verbose_name="Mã khách hàng")
    customer_name = models.CharField(max_length=255, verbose_name="Khách hàng")
    customer_address = models.CharField(max_length=255, blank=True, null=True, verbose_name="Địa chỉ")
    customer_area = models.CharField(max_length=255, blank=True, null=True, verbose_name="Khu vực")
    customer_phone = models.CharField(max_length=50, blank=True, null=True, verbose_name="SĐT")

    created_by = models.CharField(max_length=255, blank=True, null=True, verbose_name="Người tạo đơn")
    employee_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nhân viên")
    transport_vehicle = models.CharField(max_length=255, blank=True, null=True, verbose_name="Xe vận chuyển")

    order_time = models.DateTimeField(default=timezone.now, verbose_name="Thời gian")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    note = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-order_time", "-created_at"]

    def __str__(self):
        return self.order_code


class OrderItem(models.Model):
    lot = models.ForeignKey(
        TraceLot,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_items",
        verbose_name="Mã lô truy xuất"
    )
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")

    product_code = models.CharField(max_length=100, blank=True, null=True, verbose_name="Mã sản phẩm")
    product_name = models.CharField(max_length=255, verbose_name="Tên Hoa/Lá phụ")

    flower_type = models.CharField(max_length=100, blank=True, null=True, verbose_name="Phân loại")
    group_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Tone/Nhóm")

    supplier_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nhà cung cấp")

    standard_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    sale_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    unit = models.CharField(max_length=50, blank=True, null=True, verbose_name="DVT")
    specification = models.CharField(max_length=255, blank=True, null=True, verbose_name="Quy cách")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product_name