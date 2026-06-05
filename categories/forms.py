from django import forms
from .models import FlowerType, Customer


class FlowerTypeForm(forms.ModelForm):
    class Meta:
        model = FlowerType
        fields = [
            "code",
            "name",
            "color",
            "origin",
            "stem_length",
            "unit",
            "processing_loss_rate",
            "category_type",
        ]

        widgets = {
            "code": forms.TextInput(attrs={"class": "form-control"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "color": forms.TextInput(attrs={"class": "form-control"}),
            "origin": forms.TextInput(attrs={"class": "form-control"}),
            "stem_length": forms.TextInput(attrs={"class": "form-control"}),
            "unit": forms.TextInput(attrs={"class": "form-control"}),
            "processing_loss_rate": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01"
            }),
            "category_type": forms.TextInput(attrs={"class": "form-control"}),
        }


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            'ma_kh',
            'ten_khach_hang',
            'dia_chi',
            'sdt',
            'van_chuyen',
            'vung',
            'nguoi_nhan_thay',
            'ma_dau',
            'country',
            'phan_loai_kh',
            'ma_so_thue',
        ]

        widgets = {
            'ma_kh': forms.TextInput(attrs={'class': 'form-control'}),
            'ten_khach_hang': forms.TextInput(attrs={'class': 'form-control'}),
            'dia_chi': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'sdt': forms.TextInput(attrs={'class': 'form-control'}),
            'van_chuyen': forms.TextInput(attrs={'class': 'form-control'}),
            'vung': forms.TextInput(attrs={'class': 'form-control'}),
            'nguoi_nhan_thay': forms.TextInput(attrs={'class': 'form-control'}),
            'ma_dau': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'phan_loai_kh': forms.TextInput(attrs={'class': 'form-control'}),
            'ma_so_thue': forms.TextInput(attrs={'class': 'form-control'}),
        }