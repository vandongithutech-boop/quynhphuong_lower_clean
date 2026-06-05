from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .models import Employee
from .forms import EmployeeForm


def employee_list(request):
    keyword = request.GET.get('q', '')

    employees = Employee.objects.all().order_by('-created_at')

    if keyword:
        employees = employees.filter(ho_ten__icontains=keyword)

    context = {
        'employees': employees,
        'keyword': keyword,
    }
    return render(request, 'employees/employee_list.html', context)


def employee_create(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã thêm nhân viên thành công.')
            return redirect('employee_list')
    else:
        form = EmployeeForm()

    return render(request, 'employees/employee_form.html', {
        'form': form,
        'title': 'Thêm nhân viên'
    })


def employee_update(request, pk):
    employee = get_object_or_404(Employee, pk=pk)

    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật nhân viên thành công.')
            return redirect('employee_list')
    else:
        form = EmployeeForm(instance=employee)

    return render(request, 'employees/employee_form.html', {
        'form': form,
        'title': 'Sửa nhân viên'
    })


def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)

    if request.method == 'POST':
        employee.delete()
        messages.success(request, 'Đã xóa nhân viên thành công.')
        return redirect('employee_list')

    return render(request, 'employees/employee_confirm_delete.html', {
        'employee': employee
    })