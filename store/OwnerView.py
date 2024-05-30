from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from .models import Cloth, Category, Product, ProductVariation, Sale, SaleItem
from .forms import ClothForm, CategoryForm, ProductForm, ProductVariationForm
from django.db.models import Sum, DateField
from django.db.models.functions import ExtractDay, ExtractWeek, ExtractMonth, ExtractYear
from django.utils import timezone
from django.views.generic import TemplateView
from django.db import models
from django.db.models import Count


# Home
def owner_home(request):
    return render(request, 'owner/home.html')

# Cloth views
def cloth_list(request):
    cloths = Cloth.objects.annotate(
        product_count=Count('categories__products')
    ).prefetch_related('categories', 'categories__products')
    return render(request, 'owner/cloth_list.html', {'cloths': cloths})


def cloth_create(request):
    if request.method == 'POST':
        form = ClothForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cloth created successfully.')
            return redirect('cloth_list')
    else:
        form = ClothForm()
    return render(request, 'owner/cloth_form.html', {'form': form})


def cloth_update(request, slug):
    cloth = get_object_or_404(Cloth, slug=slug)
    if request.method == 'POST':
        form = ClothForm(request.POST, instance=cloth)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cloth updated successfully.')
            return redirect('cloth_list')
    else:
        form = ClothForm(instance=cloth)
    return render(request, 'owner/cloth_form.html', {'form': form})


def cloth_delete(request, slug):
    cloth = get_object_or_404(Cloth, slug=slug)
    if request.method == 'POST':
        cloth.delete()
        messages.success(request, 'Cloth deleted successfully.')
        return redirect('cloth_list')
    return render(request, 'owner/cloth_confirm_delete.html', {'cloth': cloth})

# Category views


def category_list(request):
    categories = Category.objects.all()
    return render(request, 'owner/category_list.html', {'categories': categories})


def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully.')
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'owner/category_form.html', {'form': form})


def category_update(request, slug):
    category = get_object_or_404(Category, slug=slug)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully.')
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'owner/category_form.html', {'form': form})


def category_delete(request, slug):
    category = get_object_or_404(Category, slug=slug)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully.')
        return redirect('category_list')
    return render(request, 'owner/category_confirm_delete.html', {'category': category})

# Product views


def product_list(request):
    products = Product.objects.all()
    return render(request, 'owner/product_list.html', {'products': products})


def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, 'Product created successfully.')
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'owner/product_form.html', {'form': form})


def product_update(request, slug):
    product = get_object_or_404(Product, slug=slug)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully.')
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'owner/product_form.html', {'form': form})


def product_delete(request, slug):
    product = get_object_or_404(Product, slug=slug)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully.')
        return redirect('product_list')
    return render(request, 'owner/product_confirm_delete.html', {'product': product})

# ProductVariation views


def product_variation_list(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    variations = ProductVariation.objects.filter(product=product)
    return render(request, 'owner/product_variation_list.html', {'variations': variations, 'product': product})


def product_variation_create(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    if request.method == 'POST':
        form = ProductVariationForm(request.POST)
        if form.is_valid():
            variation = form.save(commit=False)
            variation.product = product
            variation.save()
            messages.success(request, 'Variation created successfully.')
            return redirect('product_variation_list', product_slug=product.slug)
    else:
        form = ProductVariationForm()
    return render(request, 'owner/product_variation_form.html', {'form': form, 'product': product})


def product_variation_update(request, product_slug, id):
    product = get_object_or_404(Product, slug=product_slug)
    variation = get_object_or_404(ProductVariation, id=id, product=product)
    if request.method == 'POST':
        form = ProductVariationForm(request.POST, instance=variation)
        if form.is_valid():
            form.save()
            messages.success(request, 'Variation updated successfully.')
            return redirect('product_variation_list', product_slug=product.slug)
    else:
        form = ProductVariationForm(instance=variation)
    return render(request, 'owner/product_variation_form.html', {'form': form, 'product': product})


def product_variation_delete(request, product_slug, id):
    product = get_object_or_404(Product, slug=product_slug)
    variation = get_object_or_404(ProductVariation, id=id, product=product)
    if request.method == 'POST':
        variation.delete()
        messages.success(request, 'Variation deleted successfully.')
        return redirect('product_variation_list', product_slug=product.slug)
    return render(request, 'owner/product_variation_confirm_delete.html', {'variation': variation, 'product': product})


from django.db.models import Sum, F
from django.db.models.functions import ExtractDay, ExtractWeek, ExtractMonth

class SalesReportView(TemplateView):
    template_name = 'owner/sales_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Sales by day
        sales_by_day = Sale.objects.annotate(day=ExtractDay('sale_date')).values(
            'sale_date', 'day').annotate(total_sales=Sum('sale_items__quantity'))

        # Sales by week
        sales_by_week = Sale.objects.annotate(week=ExtractWeek('sale_date')).values(
            'week').annotate(total_sales=Sum('sale_items__quantity'))

        # Sales by month
        sales_by_month = Sale.objects.annotate(month=ExtractMonth('sale_date')).values(
            'month').annotate(total_sales=Sum('sale_items__quantity'))

        # Sales by category
        sales_by_category = SaleItem.objects.values(
            'product__category__name').annotate(total_sales=Sum('quantity'))

        # Sales by product
        sales_by_product = SaleItem.objects.values(
            'product__name').annotate(total_sales=Sum('quantity'))

        context.update({
            'sales_by_day': sales_by_day,
            'sales_by_week': sales_by_week,
            'sales_by_month': sales_by_month,
            'sales_by_category': sales_by_category,
            'sales_by_product': sales_by_product,
        })

        return context
