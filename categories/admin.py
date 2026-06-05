from django.contrib import admin
from .models import FlowerType, Customer


@admin.register(FlowerType)
class FlowerTypeAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'color', 'is_active', 'created_at',"category_type","processing_loss_rate","unit","stem_length","origin","stems_per_bunch","bunches_per_box","nw_per_bunch","box_weight","packing_type","box_type",)
    search_fields = ('code', 'name', 'color')
    list_filter = ('is_active', 'color')

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("ma_kh", "ten_khach_hang", "sdt", "vung", "country", "phan_loai_kh")
    search_fields = ("ma_kh", "ten_khach_hang", "sdt")
    list_filter = ("vung", "country", "phan_loai_kh")