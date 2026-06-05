from django import forms
from .models import Employee


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            "ma_nv",
            "ho_ten",
            "gioi_tinh",
            "sdt",
            "bo_phan",
            "chuc_vu",
            "dia_chi",
            "ngay_vao_lam",
            "trang_thai",
            "ghi_chu",
        ]

        widgets = {
            "ma_nv": forms.TextInput(attrs={"class": "form-control"}),
            "ho_ten": forms.TextInput(attrs={"class": "form-control"}),
            "gioi_tinh": forms.TextInput(attrs={"class": "form-control"}),
            "sdt": forms.TextInput(attrs={"class": "form-control"}),
            "bo_phan": forms.TextInput(attrs={"class": "form-control"}),
            "chuc_vu": forms.TextInput(attrs={"class": "form-control"}),
            "dia_chi": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "ngay_vao_lam": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "trang_thai": forms.TextInput(attrs={"class": "form-control"}),
            "ghi_chu": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }