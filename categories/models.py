from django.db import models


class FlowerType(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name="Mã hoa")
    name = models.CharField(max_length=255, verbose_name="Tên hoa")
    color = models.CharField(max_length=100,blank=True,null=True,verbose_name="Tone/Nhóm")
    origin = models.CharField(max_length=100,blank=True,null=True,verbose_name="Xuất xứ")
    stem_length = models.CharField(max_length=50,blank=True,null=True,verbose_name="CĐ")
    unit = models.CharField(max_length=50,blank=True,null=True,verbose_name="DVT")
    processing_loss_rate = models.DecimalField(max_digits=50,decimal_places=2,default=0,verbose_name="Tỉ lệ hao hụt sơ chế")
    category_type = models.CharField(max_length=100,blank=True,null=True,verbose_name="Phân Loại")
    description = models.TextField(blank=True, null=True, verbose_name="Mô tả")
    is_active = models.BooleanField(default=True, verbose_name="Đang sử dụng")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")
    export_name = models.CharField(max_length=255,blank=True,null=True,verbose_name="Tên xuất khẩu")
    stems_per_bunch = models.FloatField(default=0,verbose_name="Số cành/bó")
    bunches_per_box = models.FloatField(default=0,verbose_name="Số bó/thùng")
    nw_per_bunch = models.FloatField(default=0,verbose_name="NW/bó")
    box_weight = models.FloatField(default=1.4,verbose_name="Trọng lượng thùng")
    packing_type = models.CharField(max_length=100,blank=True,null=True,verbose_name="Quy cách đóng gói")
    box_type = models.CharField(max_length=100,blank=True,null=True,verbose_name="Loại thùng")
    class Meta:
        verbose_name = "Loại hoa"
        verbose_name_plural = "Danh sách loại hoa"
        ordering = ["name"]

    def __str__(self):
        return f"{self.code} - {self.name}"
    
class Customer(models.Model):
    ma_kh = models.CharField(max_length=50, unique=True, verbose_name="Mã KH")
    ten_khach_hang = models.CharField(max_length=255, verbose_name="Tên khách hàng")
    dia_chi = models.TextField(blank=True, null=True, verbose_name="Địa chỉ")
    sdt = models.CharField(max_length=30, blank=True, null=True, verbose_name="SĐT")
    van_chuyen = models.CharField(max_length=255, blank=True, null=True, verbose_name="Vận chuyển")
    vung = models.CharField(max_length=100, blank=True, null=True, verbose_name="Vùng")
    nguoi_nhan_thay = models.CharField(max_length=255, blank=True, null=True, verbose_name="Người nhận thay")
    ma_dau = models.CharField(max_length=50, blank=True, null=True, verbose_name="Mã đầu")
    country = models.CharField(max_length=10, blank=True, null=True, verbose_name="Country V/N")
    phan_loai_kh = models.CharField(max_length=10, blank=True, null=True, verbose_name="Phân loại KH")
    ma_so_thue = models.CharField(max_length=50, blank=True, null=True, verbose_name="Mã số thuế")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.ten_khach_hang

    class Meta:
        verbose_name = "Khách hàng"
        verbose_name_plural = "Khách hàng"