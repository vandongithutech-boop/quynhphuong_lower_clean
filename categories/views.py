from django.shortcuts import render, redirect, get_object_or_404
from .models import FlowerType, Customer
from .forms import FlowerTypeForm, CustomerForm
from django.db.models import Q


def flower_list(request):
    filter_type = request.GET.get("type")
    keyword = request.GET.get("q", "").strip()

    flowers = FlowerType.objects.all()

    if filter_type == "HH":
        flowers = flowers.filter(category_type__iexact="HH")
    elif filter_type == "HP":
        flowers = flowers.filter(category_type__iexact="HP")

    if keyword:
        flowers = flowers.filter(name__icontains=keyword)

    total_flowers = flowers.count()

    suggestion_flowers = FlowerType.objects.all()

    if filter_type == "HH":
        suggestion_flowers = suggestion_flowers.filter(category_type__iexact="HH")
    elif filter_type == "HP":
        suggestion_flowers = suggestion_flowers.filter(category_type__iexact="HP")

    return render(request, "categories/flower_list.html", {
        "flowers": flowers,
        "suggestion_flowers": suggestion_flowers,
        "filter_type": filter_type,
        "keyword": keyword,
        "total_flowers": total_flowers,
    })

def flower_create(request):
    if request.method == 'POST':
        form = FlowerTypeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('categories:flower_list')
    else:
        form = FlowerTypeForm()

    return render(request, 'categories/flower_form.html', {
        'form': form
    })


def flower_update(request, pk):
    flower = FlowerType.objects.get(pk=pk)

    if request.method == 'POST':
        form = FlowerTypeForm(request.POST, instance=flower)
        if form.is_valid():
            form.save()
            return redirect('categories:flower_list')
    else:
        form = FlowerTypeForm(instance=flower)

    return render(request, 'categories/flower_form.html', {
        'form': form
    })


def flower_delete(request, pk):
    flower = FlowerType.objects.get(pk=pk)

    if request.method == 'POST':
        flower.delete()
        return redirect('categories:flower_list')

    return render(request, 'categories/flower_confirm_delete.html', {
        'flower': flower
    })



def customer_list(request):
    filter_type = request.GET.get("type")
    keyword = request.GET.get("q", "").strip()

    customers = Customer.objects.all().order_by("-id")

    if filter_type == "KH":
        customers = customers.filter(ma_kh__istartswith="KH")
    elif filter_type == "NCC":
        customers = customers.filter(ma_kh__istartswith="NCC")

    if keyword:
        customers = customers.filter(ten_khach_hang__icontains=keyword)

    total_customers = customers.count()

    suggestion_customers = Customer.objects.all()

    if filter_type == "KH":
        suggestion_customers = suggestion_customers.filter(ma_kh__istartswith="KH")
    elif filter_type == "NCC":
        suggestion_customers = suggestion_customers.filter(ma_kh__istartswith="NCC")

    return render(request, "categories/customer_list.html", {
        "customers": customers,
        "suggestion_customers": suggestion_customers,
        "filter_type": filter_type,
        "keyword": keyword,
        "total_customers": total_customers,
    })


def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('categories:customer_list')
    else:
        form = CustomerForm()

    return render(request, 'categories/customer_form.html', {
        'form': form,
        'title': 'Thêm khách hàng'
    })


def customer_update(request, pk):
    customer = get_object_or_404(Customer, pk=pk)

    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('categories:customer_list')
    else:
        form = CustomerForm(instance=customer)

    return render(request, 'categories/customer_form.html', {
        'form': form,
        'title': 'Sửa khách hàng'
    })


def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)

    if request.method == 'POST':
        customer.delete()
        return redirect('categories:customer_list')

    return render(request, 'categories/customer_confirm_delete.html', {
        'customer': customer
    })