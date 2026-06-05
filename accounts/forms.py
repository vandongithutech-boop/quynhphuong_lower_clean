from django import forms
from django.contrib.auth.models import User, Group
from employees.models import Employee
from .models import UserEmployee


class EmployeeSelfRegisterForm(forms.Form):
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.filter(trang_thai="Đang làm"),
        label="Nhân viên",
        empty_label="-- Chọn nhân viên --",
        widget=forms.Select(attrs={"class": "form-select"})
    )

    username = forms.CharField(
        label="Tên đăng nhập",
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Nhập tên đăng nhập"
        })
    )

    password1 = forms.CharField(
        label="Mật khẩu",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Nhập mật khẩu"
        })
    )

    password2 = forms.CharField(
        label="Nhập lại mật khẩu",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Nhập lại mật khẩu"
        })
    )

    def clean_employee(self):
        employee = self.cleaned_data["employee"]

        if UserEmployee.objects.filter(employee=employee).exists():
            raise forms.ValidationError("Nhân viên này đã đăng ký tài khoản.")

        return employee

    def clean_username(self):
        username = self.cleaned_data["username"]

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Tên đăng nhập đã tồn tại.")

        return username

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Hai mật khẩu không khớp.")

        return cleaned_data


class ApproveAccountForm(forms.Form):
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        label="Nhóm quyền",
        empty_label="-- Chọn nhóm quyền --",
        widget=forms.Select(attrs={"class": "form-select form-select-sm"})
    )