from django.db import models
from django.utils import timezone


class PurchaseOrder(models.Model):
    STATUS_CHOICES = [
    ("draft", "Chờ tài xế nhận"),
    ("assigned_driver", "Đã giao tài xế"),
    ("waiting_stock_in", "Chờ nhập kho"),
    ("received", "Đã nhập kho"),
    ("cancelled", "Hủy đặt hàng"),
]

    po_code = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name="Mã đặt mua")
    supplier_code = models.CharField(max_length=50, blank=True, null=True, verbose_name="Mã NCC")
    supplier_name = models.CharField(max_length=255, verbose_name="Nhà cung cấp")
    driver_employee_code = models.CharField(max_length=50, blank=True, null=True, verbose_name="Mã nhân viên tài xế")
    driver_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Tài xế")
    supplier_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nhà cung cấp")
    vehicle_info = models.CharField(max_length=255, blank=True, null=True, verbose_name="Phương tiện")
    warehouse_receiver_code = models.CharField(max_length=50, blank=True, null=True, verbose_name="Mã NV nhận kho")
    warehouse_receiver = models.CharField(max_length=255, blank=True, null=True, verbose_name="Người nhận kho")
    order_datetime = models.DateTimeField(verbose_name="Ngày giờ đặt",default=timezone.now)
    pickup_date = models.DateField(blank=True, null=True, verbose_name="Ngày lấy hàng")
    received_date = models.DateField(blank=True, null=True, verbose_name="Ngày nhập kho")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="draft", verbose_name="Trạng thái")
    note = models.TextField(blank=True, null=True, verbose_name="Ghi chú")
    created_at = models.DateTimeField(auto_now_add=True)
    driver_received_quantity = models.FloatField(default=0, verbose_name="SL tài xế thực nhận")

    def save(self, *args, **kwargs):
        if not self.po_code or self.po_code == "-":
            today = timezone.now().strftime("%Y%m%d")
            prefix = f"PO{today}"

            last_po = PurchaseOrder.objects.filter(
                po_code__startswith=prefix
            ).order_by("-id").first()

            last_number = 0
            if last_po:
                try:
                    last_number = int(last_po.po_code[-4:])
                except Exception:
                    last_number = 0

            self.po_code = f"{prefix}{last_number + 1:04d}"

        super().save(*args, **kwargs)

    class Meta:
        db_table = "purchase_order"
        verbose_name = "Đơn đặt mua"
        verbose_name_plural = "Đơn đặt mua"
        ordering = ["-created_at"]

    def __str__(self):
        return self.po_code or "Đơn đặt mua mới"


class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name="items")
    product_code = models.CharField(max_length=50, verbose_name="Mã hoa")
    product_name = models.CharField(max_length=255, verbose_name="Tên hoa")
    unit = models.CharField(max_length=50, blank=True, null=True)
    stems_per_bundle = models.IntegerField(default=50, verbose_name="Quy cách bó")
    ordered_quantity = models.FloatField(default=0, verbose_name="SL đặt")
    received_quantity = models.FloatField(default=0, verbose_name="SL thực nhận")
    expected_bundle_count = models.IntegerField(default=0, verbose_name="Số bó dự kiến")
    actual_bundle_count = models.IntegerField(default=0, verbose_name="Số bó thực tế")
    note = models.TextField(blank=True, null=True)
    supplier_code = models.CharField(max_length=50,blank=True,null=True,verbose_name="Mã NCC dòng hàng")
    supplier_name = models.CharField(max_length=255,blank=True,null=True,verbose_name="Tên NCC dòng hàng")
    driver_received_quantity = models.FloatField(default=0)
    driver_confirmed = models.BooleanField(default=False)
    driver_confirmed_at = models.DateTimeField(blank=True, null=True)
    over_quantity_status = models.CharField(max_length=30,default="none",choices=[("none", "Không vượt"),("pending", "Chờ duyệt vượt"),("approved", "Đã duyệt vượt"),("rejected", "Đã điều chỉnh SL"),],verbose_name="Trạng thái vượt SL")
    warehouse_checked_quantity = models.FloatField(default=0,verbose_name="SL kho kiểm")
    warehouse_checked_at = models.DateTimeField(blank=True,null=True,verbose_name="Thời gian kho kiểm")
    def save(self, *args, **kwargs):
        if self.stems_per_bundle and self.ordered_quantity:
            self.expected_bundle_count = int(
                (float(self.ordered_quantity) + self.stems_per_bundle - 1)
                // self.stems_per_bundle
            )

        if not self.received_quantity:
            self.received_quantity = self.ordered_quantity

        if self.stems_per_bundle and self.received_quantity:
            self.actual_bundle_count = int(
                (float(self.received_quantity) + self.stems_per_bundle - 1)
                // self.stems_per_bundle
            )

        super().save(*args, **kwargs)

    class Meta:
        db_table = "purchase_order_item"
        verbose_name = "Chi tiết đặt mua"
        verbose_name_plural = "Chi tiết đặt mua"

    def __str__(self):
        po_code = self.purchase_order.po_code if self.purchase_order else "PO"
        return f"{po_code} - {self.product_name}"

class PurchaseWarehouseCheckDraft(models.Model):
    purchase_order_item = models.OneToOneField(
        PurchaseOrderItem,
        on_delete=models.CASCADE,
        related_name="warehouse_check_draft"
    )

    checked_quantity = models.FloatField(default=0, verbose_name="SL kho kiểm tạm")
    stems_per_bundle = models.IntegerField(default=50, verbose_name="Quy cách bó tạm")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "purchase_warehouse_check_draft"
        verbose_name = "Dữ liệu kho kiểm tạm"
        verbose_name_plural = "Dữ liệu kho kiểm tạm"

    def __str__(self):
        return f"{self.purchase_order_item.product_name} - {self.checked_quantity}"

class PurchasePickup(models.Model):
    STATUS_CHOICES = [
        ("draft", "Nháp"),
        ("assigned_driver", "Đã giao tài xế"),
        ("picked_up", "Đã lấy hàng"),
        ("waiting_stock_in", "Chờ nhập kho"),
        ("received", "Đã nhập kho"),
        ("cancelled", "Đã hủy"),
    ]

    pickup_code = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Mã chuyến lấy hàng"
    )

    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name="pickups",
        verbose_name="Đơn đặt mua"
    )

    driver_employee_code = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Mã NV tài xế"
    )

    driver_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Tài xế"
    )

    vehicle_info = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Phương tiện"
    )

    pickup_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="Ngày lấy hàng"
    )

    received_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="Ngày kho nhận"
    )

    warehouse_receiver_code = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Mã NV nhận kho"
    )

    warehouse_receiver = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Người nhận kho"
    )

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default="draft",
        verbose_name="Trạng thái"
    )

    note = models.TextField(
        blank=True,
        null=True,
        verbose_name="Ghi chú"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.pickup_code or self.pickup_code == "-":
            today = timezone.now().strftime("%Y%m%d")
            prefix = f"PU{today}"

            last_pickup = (
                PurchasePickup.objects
                .filter(pickup_code__startswith=prefix)
                .order_by("-id")
                .first()
            )

            last_number = 0

            if last_pickup:
                try:
                    last_number = int(last_pickup.pickup_code[-4:])
                except Exception:
                    last_number = 0

            self.pickup_code = f"{prefix}{last_number + 1:04d}"

        super().save(*args, **kwargs)

    class Meta:
        db_table = "purchase_pickup"
        verbose_name = "Chuyến lấy hàng"
        verbose_name_plural = "Chuyến lấy hàng"
        ordering = ["-created_at"]

    def __str__(self):
        return self.pickup_code or "Chuyến lấy hàng mới"


class PurchasePickupItem(models.Model):
    pickup = models.ForeignKey(
        PurchasePickup,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Chuyến lấy hàng"
    )

    purchase_order_item = models.ForeignKey(
        PurchaseOrderItem,
        on_delete=models.CASCADE,
        related_name="pickup_items",
        verbose_name="Sản phẩm đặt mua"
    )

    product_code = models.CharField(
        max_length=50,
        verbose_name="Mã hoa"
    )

    product_name = models.CharField(
        max_length=255,
        verbose_name="Tên hoa"
    )

    unit = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    stems_per_bundle = models.IntegerField(
        default=50,
        verbose_name="Quy cách bó"
    )

    planned_quantity = models.FloatField(
        default=0,
        verbose_name="SL dự kiến lấy"
    )

    received_quantity = models.FloatField(
        default=0,
        verbose_name="SL kho thực nhận"
    )

    planned_bundle_count = models.IntegerField(
        default=0,
        verbose_name="Số bó dự kiến"
    )

    actual_bundle_count = models.IntegerField(
        default=0,
        verbose_name="Số bó thực nhận"
    )

    note = models.TextField(
        blank=True,
        null=True,
        verbose_name="Ghi chú"
    )

    def save(self, *args, **kwargs):
        if self.stems_per_bundle and self.planned_quantity:
            self.planned_bundle_count = int(
                (float(self.planned_quantity) + self.stems_per_bundle - 1)
                // self.stems_per_bundle
            )

        if not self.received_quantity:
            self.received_quantity = self.planned_quantity

        if self.stems_per_bundle and self.received_quantity:
            self.actual_bundle_count = int(
                (float(self.received_quantity) + self.stems_per_bundle - 1)
                // self.stems_per_bundle
            )

        super().save(*args, **kwargs)

    class Meta:
        db_table = "purchase_pickup_item"
        verbose_name = "Chi tiết chuyến lấy hàng"
        verbose_name_plural = "Chi tiết chuyến lấy hàng"

    def __str__(self):
        return f"{self.pickup.pickup_code} - {self.product_name}"
    
class PurchaseOrderAlert(models.Model):
    STATUS_CHOICES = [
        ("pending", "Chờ xử lý"),
        ("approved", "Đã duyệt nhận"),
        ("rejected", "Không nhận"),
    ]

    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name="alerts",
        verbose_name="Đơn đặt mua"
    )

    item = models.ForeignKey(
        PurchaseOrderItem,
        on_delete=models.CASCADE,
        related_name="alerts",
        verbose_name="Dòng sản phẩm"
    )

    product_name = models.CharField(max_length=255, verbose_name="Tên hoa")
    ordered_quantity = models.FloatField(default=0, verbose_name="SL đặt")
    driver_received_quantity = models.FloatField(default=0, verbose_name="SL tài xế báo nhận")

    approved_quantity = models.FloatField(
        blank=True,
        null=True,
        verbose_name="SL kinh doanh duyệt"
    )

    message = models.TextField(blank=True, null=True, verbose_name="Nội dung cảnh báo")

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name="Trạng thái"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(blank=True, null=True)

    driver_name = models.CharField(
    max_length=255,
    blank=True,
    null=True,
    verbose_name="Tài xế"
    )

    supplier_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Nhà cung cấp"
    )
    class Meta:
        db_table = "purchase_order_alert"
        verbose_name = "Cảnh báo đặt mua"
        verbose_name_plural = "Cảnh báo đặt mua"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.purchase_order.po_code} - {self.product_name}"
    
class PurchaseWarehouseCheckDraft(models.Model):
    purchase_order_item = models.OneToOneField(
        PurchaseOrderItem,
        on_delete=models.CASCADE,
        related_name="warehouse_check_draft"
    )

    checked_quantity = models.FloatField(default=0, verbose_name="SL kho kiểm tạm")
    stems_per_bundle = models.IntegerField(default=50, verbose_name="Quy cách bó tạm")

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "purchase_warehouse_check_draft"
        verbose_name = "Dữ liệu kho kiểm tạm"
        verbose_name_plural = "Dữ liệu kho kiểm tạm"

    def __str__(self):
        return f"{self.purchase_order_item.product_name} - {self.checked_quantity}"