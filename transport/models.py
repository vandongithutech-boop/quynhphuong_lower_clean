from django.db import models


class TransportRoute(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Tên tuyến")
    note = models.TextField(blank=True, null=True, verbose_name="Ghi chú")
    is_active = models.BooleanField(default=True, verbose_name="Đang sử dụng")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Tuyến vận chuyển"
        verbose_name_plural = "Tuyến vận chuyển"
        ordering = ['name']

    def __str__(self):
        return self.name


class TransportCompany(models.Model):
    RECEIVE_TYPE_CHOICES = [
        ('factory', 'Nhận tại xưởng'),
        ('station', 'Nhận tại bến'),
        ('other', 'Khác'),
    ]

    name = models.CharField(max_length=255, unique=True, verbose_name="Tên nhà xe")
    phone = models.CharField(max_length=50, blank=True, null=True, verbose_name="Số điện thoại")
    receive_time = models.CharField(max_length=50, blank=True, null=True, verbose_name="Giờ nhận tại xưởng")
    departure_time = models.CharField(max_length=50, blank=True, null=True, verbose_name="Giờ xe xuất bến")
    receive_type = models.CharField(
        max_length=20,
        choices=RECEIVE_TYPE_CHOICES,
        default='station',
        verbose_name="Hình thức nhận"
    )
    note = models.TextField(blank=True, null=True, verbose_name="Ghi chú")
    is_active = models.BooleanField(default=True, verbose_name="Đang sử dụng")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Nhà xe"
        verbose_name_plural = "Nhà xe"
        ordering = ['name']

    def __str__(self):
        return self.name


class RouteCompany(models.Model):
    route = models.ForeignKey(
        TransportRoute,
        on_delete=models.CASCADE,
        related_name="route_companies",
        verbose_name="Tuyến"
    )
    company = models.ForeignKey(
        TransportCompany,
        on_delete=models.CASCADE,
        related_name="company_routes",
        verbose_name="Nhà xe"
    )
    priority = models.PositiveIntegerField(default=1, verbose_name="Thứ tự ưu tiên")
    note = models.TextField(blank=True, null=True, verbose_name="Ghi chú")

    class Meta:
        verbose_name = "Nhà xe theo tuyến"
        verbose_name_plural = "Nhà xe theo tuyến"
        ordering = ['route__name', 'priority']
        unique_together = ('route', 'company')

    def __str__(self):
        return f"{self.route.name} - {self.company.name}"


class VehicleInspection(models.Model):
    check_date = models.DateField(verbose_name="Ngày kiểm tra")
    check_time = models.TimeField(verbose_name="Giờ kiểm tra")

    tire_ok = models.BooleanField(default=False, verbose_name="Lốp xe")
    tire_note = models.TextField(blank=True, null=True)

    box_ok = models.BooleanField(default=False, verbose_name="Thùng xe")
    box_note = models.TextField(blank=True, null=True)

    oil_ok = models.BooleanField(default=False, verbose_name="Nhớt xe")
    oil_note = models.TextField(blank=True, null=True)

    windshield_ok = models.BooleanField(default=False, verbose_name="Kính chắn gió")
    windshield_note = models.TextField(blank=True, null=True)

    fuel_ok = models.BooleanField(default=False, verbose_name="Nhiên liệu trên 95%")
    fuel_percent = models.PositiveIntegerField(blank=True, null=True, verbose_name="Nhiên liệu thực tế")
    fuel_note = models.TextField(blank=True, null=True)

    light_ok = models.BooleanField(default=False, verbose_name="Đèn chiếu sáng")
    light_note = models.TextField(blank=True, null=True)

    horn_ok = models.BooleanField(default=False, verbose_name="Còi")
    horn_note = models.TextField(blank=True, null=True)

    gps_ok = models.BooleanField(default=False, verbose_name="GPS")
    gps_note = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Kiểm tra xe"
        verbose_name_plural = "Kiểm tra xe"
        ordering = ['-created_at']

    def __str__(self):
        return f"Kiểm tra xe {self.check_date} {self.check_time}"