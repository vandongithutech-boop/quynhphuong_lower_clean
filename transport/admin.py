from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import TransportRoute, TransportCompany, RouteCompany, VehicleInspection


class RouteCompanyInline(admin.TabularInline):
    model = RouteCompany
    extra = 1


@admin.register(TransportRoute)
class TransportRouteAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    search_fields = ('name',)
    list_filter = ('is_active',)
    inlines = [RouteCompanyInline]


@admin.register(TransportCompany)
class TransportCompanyAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'phone',
        'receive_time',
        'departure_time',
        'receive_type',
        'is_active',
    )
    search_fields = ('name', 'phone')
    list_filter = ('receive_type', 'is_active')


@admin.register(RouteCompany)
class RouteCompanyAdmin(admin.ModelAdmin):
    list_display = ('route', 'company', 'priority')
    search_fields = ('route__name', 'company__name')
    list_filter = ('route', 'company')


@admin.register(VehicleInspection)
class VehicleInspectionAdmin(admin.ModelAdmin):
    list_display = (
        'check_date',
        'check_time',
        'tire_ok',
        'box_ok',
        'oil_ok',
        'fuel_ok',
        'light_ok',
        'horn_ok',
        'gps_ok',
        'created_at',
    )

    list_filter = (
        'check_date',
        'tire_ok',
        'box_ok',
        'oil_ok',
        'fuel_ok',
        'light_ok',
        'horn_ok',
        'gps_ok',
    )

    search_fields = (
        'tire_note',
        'box_note',
        'oil_note',
        'fuel_note',
        'gps_note',
    )