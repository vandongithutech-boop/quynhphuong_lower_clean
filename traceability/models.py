from django.db import models


class TraceLot(models.Model):
    DELIVERY_TYPE_CHOICES = [
        ("supplier_delivery", "Nhà cung cấp giao"),
        ("company_pickup", "Nhân viên công ty đi lấy"),
        ("retail_delivery", "Khách lẻ giao"),
        ("other", "Khác"),
    ]

    lot_code = models.CharField("Mã lô", max_length=50, unique=True)

    product_code = models.CharField("Mã sản phẩm", max_length=50)
    product_name = models.CharField("Tên sản phẩm", max_length=255)
    unit = models.CharField("Đơn vị tính", max_length=50, blank=True, null=True)

    supplier_code = models.CharField("Mã nhà cung cấp", max_length=50, blank=True, null=True)
    supplier_name = models.CharField("Tên nhà cung cấp", max_length=255, blank=True, null=True)

    received_date = models.DateField("Ngày nhập")
    received_time = models.TimeField("Giờ nhập", blank=True, null=True)
    received_quantity = models.IntegerField("Số lượng nhập", default=0)

    delivery_type = models.CharField(
        "Hình thức giao nhận",
        max_length=50,
        choices=DELIVERY_TYPE_CHOICES,
        blank=True,
        null=True
    )

    delivered_by = models.CharField("Người giao hàng", max_length=255, blank=True, null=True)
    picked_by = models.CharField("Người đi lấy hàng", max_length=255, blank=True, null=True)
    vehicle_info = models.CharField("Thông tin xe", max_length=255, blank=True, null=True)

    quality_status = models.CharField("Tình trạng hoa lúc nhận", max_length=255, blank=True, null=True)
    note = models.TextField("Ghi chú", blank=True, null=True)

    qr_code = models.ImageField("QR Code", upload_to="trace_qr/", blank=True, null=True)

    created_at = models.DateTimeField("Ngày tạo", auto_now_add=True)
    updated_at = models.DateTimeField("Ngày cập nhật", auto_now=True)

    class Meta:
        verbose_name = "Lô truy xuất"
        verbose_name_plural = "Lô truy xuất"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.lot_code} - {self.product_name}"


class TraceLog(models.Model):
    ACTION_CHOICES = [
        ("import_raw", "Nhập kho nguyên liệu"),
        ("move_to_processing", "Xuất đi sơ chế"),
        ("processing_done", "Nhập kho thành phẩm"),
        ("processing_waste", "Xả/hủy khi sơ chế"),
        ("export_order", "Xuất cho đơn hàng"),
        ("packing", "Đóng gói"),
        ("move_to_sale", "Chuyển kho sale"),
        ("destroy", "Hủy hoa"),
        ("adjust", "Điều chỉnh"),
        ("other", "Khác"),
    ]

    lot = models.ForeignKey(
        TraceLot,
        on_delete=models.CASCADE,
        related_name="logs",
        verbose_name="Mã lô"
    )

    action = models.CharField("Hành động", max_length=100, choices=ACTION_CHOICES)

    from_area = models.CharField("Từ khu vực", max_length=100, blank=True, null=True)
    to_area = models.CharField("Đến khu vực", max_length=100, blank=True, null=True)

    quantity = models.IntegerField("Số lượng", default=0)
    employee_name = models.CharField("Nhân viên thực hiện", max_length=255, blank=True, null=True)

    related_code = models.CharField("Mã liên quan", max_length=100, blank=True, null=True)
    note = models.TextField("Ghi chú", blank=True, null=True)

    created_at = models.DateTimeField("Thời gian", auto_now_add=True)

    class Meta:
        verbose_name = "Nhật ký truy xuất"
        verbose_name_plural = "Nhật ký truy xuất"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.lot.lot_code} - {self.get_action_display()} - {self.quantity}"


class DisposalRecord(models.Model):
    lot = models.ForeignKey(
        TraceLot,
        on_delete=models.CASCADE,
        related_name="disposals",
        verbose_name="Mã lô"
    )

    quantity = models.IntegerField("Số lượng hủy", default=0)
    reason = models.CharField("Lý do hủy", max_length=255)
    employee_name = models.CharField("Người hủy", max_length=255, blank=True, null=True)
    note = models.TextField("Ghi chú", blank=True, null=True)

    created_at = models.DateTimeField("Thời gian hủy", auto_now_add=True)

    class Meta:
        verbose_name = "Phiếu hủy hoa"
        verbose_name_plural = "Phiếu hủy hoa"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.lot.lot_code} - Hủy {self.quantity}"
    
class TraceBundle(models.Model):
    STATUS_CHOICES = [
        ("raw", "Nguyên liệu"),
        ("processing", "Đang sơ chế"),
        ("processed", "Đã sơ chế"),
        ("finished", "Thành phẩm"),
        ("packed", "Đã đóng gói"),
        ("exported", "Đã xuất hàng"),
        ("damaged", "Hủy/hao hụt"),
    ]

    bundle_code = models.CharField(
        max_length=80,
        unique=True,
        verbose_name="Mã bó QR"
    )

    lot = models.ForeignKey(
        TraceLot,
        on_delete=models.CASCADE,
        related_name="bundles",
        verbose_name="Mã lô"
    )

    product_code = models.CharField(max_length=100, blank=True, null=True)
    product_name = models.CharField(max_length=255)

    supplier_code = models.CharField(max_length=100, blank=True, null=True)
    supplier_name = models.CharField(max_length=255, blank=True, null=True)

    initial_stems = models.FloatField(default=0, verbose_name="Số cành ban đầu")
    remaining_stems = models.FloatField(default=0, verbose_name="Số cành còn lại")

    bundle_number = models.PositiveIntegerField(
        default=1,
        verbose_name="Số thứ tự bó"
    )

    expected_stems = models.FloatField(
        default=0,
        verbose_name="Số cành dự kiến/bó"
    )

    actual_stems = models.FloatField(
        default=0,
        verbose_name="Số cành thực nhận/bó"
    )

    SOURCE_CHOICES = [
        ("purchase", "Đơn đặt mua"),
        ("walk_in", "Khách lẻ mang tới"),
        ("adjustment", "Nhập điều chỉnh"),
    ]

    source_type = models.CharField(
        max_length=30,
        choices=SOURCE_CHOICES,
        default="purchase",
        verbose_name="Nguồn nhập"
    )

    seller_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Người bán/khách lẻ"
    )

    seller_phone = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="SĐT người bán"
    )

    note = models.TextField(
        blank=True,
        null=True,
        verbose_name="Ghi chú bó"
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="raw",
        verbose_name="Trạng thái bó"
    )

    qr_image = models.ImageField(
        upload_to="trace_bundle_qr/",
        blank=True,
        null=True,
        verbose_name="QR bó"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Bó QR truy xuất"
        verbose_name_plural = "Bó QR truy xuất"
        ordering = ["lot", "product_code", "bundle_number"]
        unique_together = ("lot", "product_code", "bundle_number")

    def __str__(self):
        return self.bundle_code