from django.db import models
from django.utils import timezone
from traceability.models import TraceLot


class InventoryReceipt(models.Model):
    PRODUCT_GROUP_CHOICES = [
        ('HH', 'Hoa Hồng'),
        ('HP', 'Hoa/Lá Phụ'),
        ('VT', 'Vật Tư'),
    ]

    RECEIPT_STATUS_CHOICES = [
        ("DRAFT_LABEL_CREATED", "Đã tạo QR bó - chờ nhập kho"),
        ("COMPLETED", "Đã nhập kho"),
    ]

    receipt_code = models.CharField(max_length=50, unique=True, verbose_name='Mã phiếu nhập')
    product_group = models.CharField(max_length=10, choices=PRODUCT_GROUP_CHOICES, verbose_name='Nhóm hàng')

    supplier_code = models.CharField(max_length=50, blank=True, null=True, verbose_name='Mã nhà cung cấp')
    supplier_name = models.CharField(max_length=255, blank=True, null=True, verbose_name='Tên nhà cung cấp')

    source_po_code = models.CharField(max_length=50, blank=True, null=True, verbose_name="Mã đơn đặt mua liên quan")

    status = models.CharField(
        max_length=30,
        choices=RECEIPT_STATUS_CHOICES,
        default="COMPLETED",
        verbose_name="Trạng thái phiếu nhập"
    )

    receipt_datetime = models.DateTimeField(auto_now_add=True, verbose_name='Ngày nhập')
    note = models.TextField(blank=True, null=True, verbose_name='Ghi chú')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Phiếu nhập kho'
        verbose_name_plural = 'Phiếu nhập kho'
        ordering = ['-receipt_datetime']

    def __str__(self):
        return self.receipt_code


class InventoryReceiptItem(models.Model):
    lot = models.ForeignKey(
        TraceLot,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="receipt_items",
        verbose_name="Mã lô truy xuất"
    )

    receipt = models.ForeignKey(
        InventoryReceipt,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Phiếu nhập'
    )

    product_code = models.CharField(max_length=50, verbose_name='Mã sản phẩm')
    product_name = models.CharField(max_length=255, verbose_name='Tên sản phẩm')
    unit = models.CharField(max_length=100, blank=True, null=True, verbose_name='ĐVT')
    flower_grade = models.CharField(max_length=100, blank=True, null=True, verbose_name='Độ hoa')
    quantity = models.FloatField(default=0, verbose_name='Số lượng')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Chi tiết phiếu nhập kho'
        verbose_name_plural = 'Chi tiết phiếu nhập kho'

    def __str__(self):
        return f'{self.product_name} - {self.quantity}'


class InventoryStock(models.Model):
    lot = models.ForeignKey(
        TraceLot,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="inventory_stocks",
        verbose_name="Mã lô truy xuất"
    )

    WAREHOUSE_CHOICES = [
        ('RAW', 'Kho nguyên liệu'),
        ('FINISHED', 'Kho thành phẩm'),
        ('SALE', 'Kho Sale'),
        ('MATERIAL', 'Kho vật tư'),
        ('DAMAGED', 'Kho hư hao'),
    ]

    PRODUCT_GROUP_CHOICES = [
        ('HH', 'Hoa Hồng'),
        ('HP', 'Hoa/Lá Phụ'),
        ('VT', 'Vật Tư'),
    ]

    warehouse_type = models.CharField(max_length=20, choices=WAREHOUSE_CHOICES, verbose_name='Kho')
    product_group = models.CharField(max_length=10, choices=PRODUCT_GROUP_CHOICES, verbose_name='Nhóm hàng')

    product_code = models.CharField(max_length=50, verbose_name='Mã sản phẩm')
    product_name = models.CharField(max_length=255, verbose_name='Tên sản phẩm')
    unit = models.CharField(max_length=100, blank=True, null=True, verbose_name='ĐVT')
    flower_grade = models.CharField(max_length=100, blank=True, null=True, verbose_name='Độ hoa')

    supplier_code = models.CharField(max_length=50, blank=True, null=True, verbose_name='Mã nhà cung cấp')
    supplier_name = models.CharField(max_length=255, blank=True, null=True, verbose_name='Tên nhà cung cấp')
    received_date = models.DateTimeField(blank=True, null=True, verbose_name='Ngày nhập gốc')

    quantity = models.FloatField(default=0, verbose_name='Số lượng tồn')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tồn kho'
        verbose_name_plural = 'Tồn kho'
        unique_together = (
            'warehouse_type',
            'product_group',
            'product_code',
            'flower_grade',
            'supplier_code',
            'received_date',
        )
        ordering = [
            'warehouse_type',
            'product_group',
            'product_name',
            'received_date',
        ]

    def __str__(self):
        return f'{self.get_warehouse_type_display()} - {self.product_code} - {self.quantity}'


class InventoryTransaction(models.Model):
    lot = models.ForeignKey(
        TraceLot,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="inventory_transactions",
        verbose_name="Mã lô truy xuất"
    )

    TRANSACTION_CHOICES = [
        ('IN', 'Nhập kho'),
        ('OUT', 'Xuất kho'),
        ('CHECK', 'Kiểm kê'),
        ('TRANSFER', 'Điều chuyển'),
        ('ADJUST', 'Điều chỉnh'),
    ]

    WAREHOUSE_CHOICES = [
        ('RAW', 'Kho nguyên liệu'),
        ('FINISHED', 'Kho thành phẩm'),
        ('SALE', 'Kho Sale'),
        ('MATERIAL', 'Kho vật tư'),
        ('DAMAGED', 'Kho hư hao'),
    ]

    transaction_code = models.CharField(max_length=50, verbose_name='Mã giao dịch')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_CHOICES, verbose_name='Loại giao dịch')
    warehouse_type = models.CharField(max_length=20, choices=WAREHOUSE_CHOICES, verbose_name='Kho')

    product_group = models.CharField(max_length=10, blank=True, null=True, verbose_name='Nhóm hàng')
    product_code = models.CharField(max_length=50, verbose_name='Mã sản phẩm')
    product_name = models.CharField(max_length=255, verbose_name='Tên sản phẩm')
    unit = models.CharField(max_length=100, blank=True, null=True, verbose_name='ĐVT')
    flower_grade = models.CharField(max_length=100, blank=True, null=True, verbose_name='Độ hoa')

    supplier_code = models.CharField(max_length=50, blank=True, null=True, verbose_name='Mã nhà cung cấp')
    supplier_name = models.CharField(max_length=255, blank=True, null=True, verbose_name='Tên nhà cung cấp')
    received_date = models.DateTimeField(blank=True, null=True, verbose_name='Ngày nhập gốc')

    quantity = models.FloatField(default=0, verbose_name='Số lượng')
    reference_code = models.CharField(max_length=50, blank=True, null=True, verbose_name='Mã tham chiếu')

    note = models.TextField(blank=True, null=True, verbose_name='Ghi chú')

    business_date = models.DateField(
        default=timezone.localdate,
        verbose_name="Ngày nghiệp vụ / ngày báo cáo kho"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Lịch sử kho'
        verbose_name_plural = 'Lịch sử kho'
        ordering = ['-business_date', '-created_at']

    def __str__(self):
        return f'{self.transaction_code} - {self.product_code}'


class InventoryStockOut(models.Model):
    STOCK_OUT_TYPE_CHOICES = [
        ("HH", "Hoa Hồng"),
        ("HP", "Hoa/Lá Phụ"),
        ("DIRECT_SALE", "Sale trực tiếp"),
        ("DAMAGED", "Xuất hoa Hủy"),
    ]

    stock_out_code = models.CharField(max_length=50, unique=True, verbose_name="Mã phiếu xuất")
    stock_out_type = models.CharField(max_length=30, choices=STOCK_OUT_TYPE_CHOICES, verbose_name="Loại xuất kho")

    employee_code = models.CharField(max_length=50, blank=True, null=True, verbose_name="Mã nhân viên")
    employee_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nhân viên thực hiện")
    employee_department = models.CharField(max_length=255, blank=True, null=True, verbose_name="Bộ phận")
    employee_position = models.CharField(max_length=255, blank=True, null=True, verbose_name="Chức vụ")

    stock_out_datetime = models.DateTimeField(auto_now_add=True, verbose_name="Ngày giờ xuất kho")
    note = models.TextField(blank=True, null=True, verbose_name="Ghi chú")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Phiếu xuất kho"
        verbose_name_plural = "Phiếu xuất kho"
        ordering = ["-stock_out_datetime"]

    def __str__(self):
        return self.stock_out_code


class InventoryStockOutItem(models.Model):
    stock_out = models.ForeignKey(
        InventoryStockOut,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Phiếu xuất kho"
    )

    lot = models.ForeignKey(
        TraceLot,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_out_items",
        verbose_name="Mã lô truy xuất"
    )

    source_stock_id = models.IntegerField(blank=True, null=True, verbose_name="ID tồn kho nguồn")

    source_warehouse = models.CharField(max_length=30, verbose_name="Kho nguồn")
    destination_warehouse = models.CharField(max_length=30, verbose_name="Kho đích")

    product_group = models.CharField(max_length=10, blank=True, null=True, verbose_name="Nhóm hàng")
    product_code = models.CharField(max_length=50, verbose_name="Mã sản phẩm")
    product_name = models.CharField(max_length=255, verbose_name="Tên sản phẩm")
    unit = models.CharField(max_length=100, blank=True, null=True, verbose_name="ĐVT")

    original_grade = models.CharField(max_length=100, blank=True, null=True, verbose_name="Độ hoa gốc")
    output_grade = models.CharField(max_length=100, blank=True, null=True, verbose_name="Độ hoa lúc xuất")

    supplier_code = models.CharField(max_length=50, blank=True, null=True, verbose_name="Mã nhà cung cấp")
    supplier_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Tên nhà cung cấp")
    received_date = models.DateTimeField(blank=True, null=True, verbose_name="Ngày nhập gốc")

    reason = models.CharField(max_length=255, blank=True, null=True, verbose_name="Lý do Sale/Hủy")
    quantity = models.FloatField(default=0, verbose_name="Số lượng xuất")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Chi tiết phiếu xuất kho"
        verbose_name_plural = "Chi tiết phiếu xuất kho"

    def __str__(self):
        return f"{self.product_name} - {self.quantity}"