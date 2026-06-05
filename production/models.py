from django.db import models
from django.utils import timezone
from traceability.models import TraceLot

from orders.models import Order, OrderItem


class ProductionOrder(models.Model):
    STATUS_CHOICES = [
        ("waiting", "Chờ sản xuất"),
        ("processing", "Đang sản xuất"),
        ("packing", "Đang đóng gói"),
        ("completed", "Hoàn thành"),
        ("cancelled", "Đã huỷ"),
    ]

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="production_order",
        verbose_name="Đơn hàng"
    )

    production_code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Mã sản xuất"
    )

    customer_name = models.CharField(max_length=255, verbose_name="Khách hàng")
    order_code = models.CharField(max_length=50, verbose_name="Mã đơn hàng")

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="waiting",
        verbose_name="Trạng thái sản xuất"
    )

    note = models.TextField(blank=True, null=True, verbose_name="Ghi chú sản xuất")

    received_at = models.DateTimeField(default=timezone.now, verbose_name="Thời gian nhận đơn")
    started_at = models.DateTimeField(blank=True, null=True, verbose_name="Bắt đầu sản xuất")
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name="Hoàn thành")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Lệnh sản xuất"
        verbose_name_plural = "Lệnh sản xuất"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.production_code} - {self.customer_name}"


class ProductionItem(models.Model):
    lot = models.ForeignKey(
        TraceLot,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="production_items",
        verbose_name="Mã lô truy xuất"
    )
    production_order = models.ForeignKey(
        ProductionOrder,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Lệnh sản xuất"
    )

    order_item = models.ForeignKey(
        OrderItem,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="production_items",
        verbose_name="Sản phẩm đơn hàng"
    )

    product_code = models.CharField(max_length=100, blank=True, null=True, verbose_name="Mã sản phẩm")
    product_name = models.CharField(max_length=255, verbose_name="Tên sản phẩm")
    flower_type = models.CharField(max_length=100, blank=True, null=True, verbose_name="Phân loại")
    group_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Tone/Nhóm")
    unit = models.CharField(max_length=50, blank=True, null=True, verbose_name="DVT")

    standard_quantity = models.FloatField(default=0, verbose_name="SL tiêu chuẩn")
    sale_quantity = models.FloatField(default=0, verbose_name="SL sale")

    required_quantity = models.FloatField(default=0, verbose_name="Tổng số lượng cần")
    finished_available = models.FloatField(default=0, verbose_name="Tồn thành phẩm lúc nhận")
    missing_quantity = models.FloatField(default=0, verbose_name="Số lượng thiếu")
    raw_available = models.FloatField(default=0, verbose_name="Tồn nguyên liệu")
    need_processing_quantity = models.FloatField(default=0, verbose_name="Cần sơ chế thêm")

    warning_note = models.TextField(blank=True, null=True, verbose_name="Cảnh báo sản xuất")

    is_sale_item = models.BooleanField(default=False, verbose_name="Hàng sale")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Chi tiết lệnh sản xuất"
        verbose_name_plural = "Chi tiết lệnh sản xuất"

    def __str__(self):
        return self.product_name


class PackingBox(models.Model):
    STATUS_CHOICES = [
        ("draft", "Nháp"),
        ("full", "FULL"),
        ("lack", "THIẾU"),
        ("over", "THỪA"),
    ]

    production_order = models.ForeignKey(
        ProductionOrder,
        on_delete=models.CASCADE,
        related_name="boxes",
        verbose_name="Lệnh sản xuất"
    )

    box_code = models.CharField(max_length=50, verbose_name="Mã thùng")
    box_number = models.IntegerField(default=1, verbose_name="Số thứ tự thùng")

    box_type = models.ForeignKey(
        "production.BoxCapacity",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="packing_boxes",
        verbose_name="Loại thùng"
    )

    capacity_index = models.FloatField(default=0, verbose_name="Sức chứa thùng")
    total_index = models.FloatField(default=0, verbose_name="Tổng chỉ số đã đóng")

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
        verbose_name="Trạng thái thùng"
    )

    total_bunches = models.FloatField(default=0, verbose_name="Tổng bó")
    total_stems = models.FloatField(default=0, verbose_name="Tổng cành")

    nw = models.FloatField(default=0, verbose_name="NW")
    gw = models.FloatField(default=0, verbose_name="GW")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Thùng đóng gói"
        verbose_name_plural = "Thùng đóng gói"

    def __str__(self):
        return self.box_code

    def recalculate(self):
        total_index = 0
        total_bunches = 0
        total_stems = 0
        total_nw = 0
        total_gw = 0

        for item in self.items.all():
            total_index += item.total_index or 0
            total_bunches += item.bunches or 0
            total_stems += item.stems or 0
            total_nw += item.nw or 0
            total_gw += item.gw or 0

        self.total_index = total_index
        self.total_bunches = total_bunches
        self.total_stems = total_stems
        self.nw = total_nw

        if self.box_type:
            self.capacity_index = self.box_type.capacity_index
            self.gw = total_nw + self.box_type.box_weight

            if total_index == self.capacity_index:
                self.status = "full"
            elif total_index < self.capacity_index:
                self.status = "lack"
            else:
                self.status = "over"
        else:
            self.status = "draft"
            self.gw = total_gw

        self.save(update_fields=[
            "total_index",
            "total_bunches",
            "total_stems",
            "nw",
            "gw",
            "capacity_index",
            "status",
        ])

class PackingBoxItem(models.Model):
    lot = models.ForeignKey(
        TraceLot,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="packing_box_items",
        verbose_name="Mã lô truy xuất"
    )
    box = models.ForeignKey(
        PackingBox,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Thùng"
    )

    production_item = models.ForeignKey(
        ProductionItem,
        on_delete=models.CASCADE,
        related_name="box_items",
        verbose_name="Sản phẩm sản xuất"
    )

    product_code = models.CharField(max_length=100, blank=True, null=True)
    product_name = models.CharField(max_length=255)

    bunches = models.FloatField(default=0, verbose_name="Số bó")
    stems = models.FloatField(default=0, verbose_name="Số cành")
    stems_per_bunch = models.FloatField(default=0, verbose_name="Cành/bó")

    packing_index = models.FloatField(default=0, verbose_name="Chỉ số đóng thùng")
    total_index = models.FloatField(default=0, verbose_name="Tổng chỉ số")

    nw = models.FloatField(default=0, verbose_name="NW")
    gw = models.FloatField(default=0, verbose_name="GW")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Chi tiết thùng"
        verbose_name_plural = "Chi tiết thùng"

    def save(self, *args, **kwargs):
        self.stems = (self.bunches or 0) * (self.stems_per_bunch or 0)
        self.total_index = (self.bunches or 0) * (self.packing_index or 0)

        super().save(*args, **kwargs)

        if self.box:
            self.box.recalculate()

    def delete(self, *args, **kwargs):
        box = self.box
        super().delete(*args, **kwargs)

        if box:
            box.recalculate()

    def __str__(self):
        return self.product_name
    
class PackingStemRule(models.Model):
    RULE_CHOICES = [
        ("100", "100c"),
        ("50", "50c"),
        ("40", "40c"),
        ("30", "30c"),
        ("20", "20c"),
        ("LE", "Lẻ"),
    ]

    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=50)
    stems_quantity = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Quy cách bó"
        verbose_name_plural = "Quy cách bó"

    def __str__(self):
        return self.name


class PackingBoxType(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)

    max_bunches = models.IntegerField(default=0)
    max_stems = models.IntegerField(default=0)

    box_weight = models.FloatField(default=1.4)

    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Loại thùng"
        verbose_name_plural = "Loại thùng"

    def __str__(self):
        return self.code


class ProductPackingRule(models.Model):
    flower = models.ForeignKey(
        "categories.FlowerType",
        on_delete=models.CASCADE,
        related_name="packing_rules"
    )

    stem_rule = models.ForeignKey(
        PackingStemRule,
        on_delete=models.CASCADE,
        related_name="product_rules"
    )

    box_type = models.ForeignKey(
        PackingBoxType,
        on_delete=models.CASCADE,
        related_name="product_rules"
    )

    bunches_per_box = models.IntegerField(default=0)
    nw_per_bunch = models.FloatField(default=0)

    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Quy chuẩn đóng gói"
        verbose_name_plural = "Quy chuẩn đóng gói"

    def __str__(self):
        return f"{self.flower.name} - {self.stem_rule.name}"
    
class PackingIndex(models.Model):
    flower = models.ForeignKey(
        "categories.FlowerType",
        on_delete=models.CASCADE,
        related_name="packing_indexes",
        verbose_name="Loại hoa"
    )

    packing_index = models.FloatField(default=0, verbose_name="Chỉ số đóng thùng")
    base_stems = models.FloatField(default=50, verbose_name="Số cành quy đổi")

    note = models.TextField(blank=True, null=True, verbose_name="Ghi chú")
    is_active = models.BooleanField(default=True, verbose_name="Đang sử dụng")

    class Meta:
        verbose_name = "Chỉ số đóng thùng"
        verbose_name_plural = "Chỉ số đóng thùng"

    def __str__(self):
        return f"{self.flower.name} - {self.packing_index}"


class BoxCapacity(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name="Mã thùng")
    name = models.CharField(max_length=100, verbose_name="Tên thùng")

    capacity_index = models.FloatField(default=0, verbose_name="Chỉ số sức chứa")
    box_weight = models.FloatField(default=1.4, verbose_name="Trọng lượng thùng")

    note = models.TextField(blank=True, null=True, verbose_name="Ghi chú")
    is_active = models.BooleanField(default=True, verbose_name="Đang sử dụng")

    class Meta:
        verbose_name = "Sức chứa thùng"
        verbose_name_plural = "Sức chứa thùng"

    def __str__(self):
        return f"{self.code} - {self.capacity_index}"