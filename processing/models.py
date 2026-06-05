from django.db import models
from django.utils import timezone
from traceability.models import TraceLot

class ProcessingTicket(models.Model):
    ticket_code = models.CharField(max_length=50, unique=True, verbose_name="Mã phiếu sơ chế")

    employee_code = models.CharField(max_length=50, verbose_name="Mã NV")
    employee_name = models.CharField(max_length=255, verbose_name="Họ tên")
    employee_position = models.CharField(max_length=100, blank=True, null=True, verbose_name="Chức vụ")

    start_time = models.DateTimeField(default=timezone.now, verbose_name="Giờ bắt đầu")
    end_time = models.DateTimeField(blank=True, null=True, verbose_name="Giờ hoàn thành")
    total_hours = models.FloatField(default=0, verbose_name="Số giờ sơ chế")
    business_date = models.DateField(default=timezone.localdate,verbose_name="Ngày nghiệp vụ / ngày báo cáo sơ chế")

    shift1_start = models.DateTimeField(blank=True, null=True, verbose_name="Ca 1 - Bắt đầu")
    shift1_end = models.DateTimeField(blank=True, null=True, verbose_name="Ca 1 - Kết thúc")
    shift1_hours = models.FloatField(default=0, verbose_name="Số giờ ca 1")

    shift2_start = models.DateTimeField(blank=True, null=True, verbose_name="Ca 2 - Bắt đầu")
    shift2_end = models.DateTimeField(blank=True, null=True, verbose_name="Ca 2 - Kết thúc")
    shift2_hours = models.FloatField(default=0, verbose_name="Số giờ ca 2")

    total_work_hours = models.FloatField(default=0, verbose_name="Tổng giờ làm việc")
    overtime_hours = models.FloatField(default=0, verbose_name="Số giờ tăng ca")

    work_note = models.TextField(blank=True, null=True, verbose_name="Ghi chú thời gian làm việc")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Phiếu sơ chế"
        verbose_name_plural = "Phiếu sơ chế"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.ticket_code} - {self.employee_name}"


class ProcessingTicketItem(models.Model):
    lot = models.ForeignKey(
        TraceLot,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="processing_items",
        verbose_name="Mã lô truy xuất"
    )
    ticket = models.ForeignKey(
        ProcessingTicket,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Phiếu sơ chế"
    )

    raw_stock_id = models.IntegerField(blank=True, null=True, verbose_name="ID tồn kho nguyên liệu")

    product_group = models.CharField(max_length=10, blank=True, null=True, verbose_name="Nhóm hàng")
    product_code = models.CharField(max_length=50, verbose_name="Mã sản phẩm")
    product_name = models.CharField(max_length=255, verbose_name="Tên sản phẩm")
    unit = models.CharField(max_length=100, blank=True, null=True, verbose_name="ĐVT")
    flower_grade = models.CharField(max_length=100, blank=True, null=True, verbose_name="Độ hoa")

    supplier_code = models.CharField(max_length=50, blank=True, null=True, verbose_name="Mã NCC")
    supplier_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Tên NCC")
    received_date = models.DateTimeField(blank=True, null=True, verbose_name="Ngày nhập gốc")
    soaking_days = models.IntegerField(default=0, verbose_name="Thời gian ngâm")

    stock_quantity = models.FloatField(default=0, verbose_name="Tồn kho lúc sơ chế")
    received_quantity = models.FloatField(default=0, verbose_name="Số lượng đã nhận")

    bunch_type = models.CharField(max_length=20, blank=True, null=True, verbose_name="Loại cành/bó")
    stems_per_bunch = models.IntegerField(default=0, verbose_name="Số cành/bó")

    processed_stems = models.FloatField(default=0, verbose_name="Số cành sơ chế")
    damaged_stems = models.FloatField(default=0, verbose_name="Số cành xả/hủy")
    odd_stems = models.FloatField(default=0, verbose_name="Số cành lẻ")
    extra_stems = models.FloatField(default=0, verbose_name="Số cành thừa")
    compensate_stems = models.FloatField(default=0, verbose_name="Bù cành lẻ khác")
    final_stems = models.FloatField(default=0, verbose_name="Tổng cành thành phẩm")
    final_bunches = models.FloatField(default=0, verbose_name="Số bó thành phẩm")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Chi tiết phiếu sơ chế"
        verbose_name_plural = "Chi tiết phiếu sơ chế"

    def __str__(self):
        return self.product_name
    

class LooseStemStock(models.Model):
    STATUS_CHOICES = [
        ("available", "Còn cành lẻ"),
        ("used", "Đã dùng hết"),
        ("expired", "Quá ngày/Hủy"),
    ]

    lot = models.ForeignKey(
        TraceLot,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="loose_stem_stocks",
        verbose_name="Mã lô truy xuất"
    )

    processing_item = models.ForeignKey(
        ProcessingTicketItem,
        on_delete=models.CASCADE,
        related_name="loose_stems",
        verbose_name="Chi tiết sơ chế"
    )

    product_code = models.CharField(max_length=50, verbose_name="Mã sản phẩm")
    product_name = models.CharField(max_length=255, verbose_name="Tên sản phẩm")
    product_group = models.CharField(max_length=10, blank=True, null=True, verbose_name="Nhóm hàng")

    supplier_code = models.CharField(max_length=50, blank=True, null=True, verbose_name="Mã NCC")
    supplier_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Tên NCC")

    employee_code = models.CharField(max_length=50, blank=True, null=True, verbose_name="Mã NV sơ chế")
    employee_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nhân viên sơ chế")

    stems_per_bunch = models.IntegerField(default=0, verbose_name="Số cành/bó")
    original_quantity = models.FloatField(default=0, verbose_name="Số cành lẻ ban đầu")
    remaining_quantity = models.FloatField(default=0, verbose_name="Số cành lẻ còn lại")
    is_carried_next_day = models.BooleanField(
        default=False,
        verbose_name="Cành lẻ chuyển qua ngày sau"
    )

    carry_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="Ngày chuyển cành lẻ"
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="available")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Khay cành lẻ"
        verbose_name_plural = "Khay cành lẻ"
        ordering = ["product_code", "created_at"]

    def __str__(self):
        return f"{self.product_code} - {self.remaining_quantity} cành lẻ ({self.supplier_name})"


class LooseStemMerge(models.Model):
    merge_code = models.CharField(max_length=50, unique=True, verbose_name="Mã ghép bó")

    product_code = models.CharField(max_length=50, verbose_name="Mã sản phẩm")
    product_name = models.CharField(max_length=255, verbose_name="Tên sản phẩm")
    stems_per_bunch = models.IntegerField(default=0, verbose_name="Số cành/bó")

    total_stems = models.FloatField(default=0, verbose_name="Tổng cành ghép")
    total_bunches = models.FloatField(default=0, verbose_name="Tổng bó tạo được")

    main_lot = models.ForeignKey(
        TraceLot,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="main_loose_merges",
        verbose_name="Lô chính"
    )

    created_by = models.CharField(max_length=255, blank=True, null=True, verbose_name="Người ghép")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Phiếu ghép cành lẻ"
        verbose_name_plural = "Phiếu ghép cành lẻ"
        ordering = ["-created_at"]

    def __str__(self):
        return self.merge_code


class LooseStemMergeItem(models.Model):
    merge = models.ForeignKey(
        LooseStemMerge,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Phiếu ghép"
    )

    loose_stock = models.ForeignKey(
        LooseStemStock,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="merge_items",
        verbose_name="Nguồn cành lẻ"
    )

    lot = models.ForeignKey(
        TraceLot,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="loose_merge_items",
        verbose_name="Mã lô truy xuất nguồn"
    )

    supplier_code = models.CharField(max_length=50, blank=True, null=True)
    supplier_name = models.CharField(max_length=255, blank=True, null=True)
    quantity_used = models.FloatField(default=0, verbose_name="Số cành đã dùng")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Chi tiết ghép cành lẻ"
        verbose_name_plural = "Chi tiết ghép cành lẻ"

    def __str__(self):
        return f"{self.merge.merge_code} - {self.quantity_used}"
