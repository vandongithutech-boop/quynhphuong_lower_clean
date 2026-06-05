from django.db import models
from production.models import PackingBox


class ExportShipment(models.Model):
    shipment_code = models.CharField("Mã xuất hàng", max_length=50, unique=True)

    export_date = models.DateField("Ngày xuất")
    export_time = models.TimeField("Giờ xuất", blank=True, null=True)

    customer_code = models.CharField("Mã khách hàng", max_length=50, blank=True, null=True)
    customer_name = models.CharField("Tên khách hàng", max_length=255, blank=True, null=True)

    vehicle_info = models.CharField("Xe vận chuyển", max_length=255, blank=True, null=True)
    container_code = models.CharField("Mã container", max_length=100, blank=True, null=True)
    driver_name = models.CharField("Tài xế", max_length=255, blank=True, null=True)

    note = models.TextField("Ghi chú", blank=True, null=True)

    boxes = models.ManyToManyField(
        PackingBox,
        related_name="export_shipments",
        verbose_name="Danh sách thùng"
    )

    created_at = models.DateTimeField("Ngày tạo", auto_now_add=True)

    class Meta:
        verbose_name = "Phiếu xuất hàng"
        verbose_name_plural = "Phiếu xuất hàng"
        ordering = ["-created_at"]

    def __str__(self):
        return self.shipment_code