from django.urls import path
from . import views
from . import OwnerView
from .OwnerView import SalesReportView
from django.views.generic import TemplateView


# Sales URL patterns
urlpatterns = [
    # Other URL patterns...
    path('products/', views.product_catalog, name='product_catalog'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('categories/<int:category_id>/', views.product_list_by_category,
         name='product_list_by_category'),
    path('add-to-sale/', views.add_to_sale, name='add_to_sale'),
    path('review-sale/', views.review_sale, name='review_sale'),
    path('submit-sale/', views.submit_sale, name='submit_sale'),



    # Owner URL patterns

    # Home
    path('owner/', OwnerView.owner_home, name='owner_home'),

    # Cloth views
    path('ocloths/', OwnerView.cloth_list, name='cloth_list'),
    path('ocloths/create/', OwnerView.cloth_create, name='cloth_create'),
    path('ocloths/<slug:slug>/update/',
         OwnerView.cloth_update, name='cloth_update'),
    path('ocloths/<slug:slug>/delete/',
         OwnerView.cloth_delete, name='cloth_delete'),

    # Category views
    path('ocategories/', OwnerView.category_list, name='category_list'),
    path('ocategories/create/', OwnerView.category_create, name='category_create'),
    path('ocategories/<slug:slug>/update/',
         OwnerView.category_update, name='category_update'),
    path('ocategories/<slug:slug>/delete/',
         OwnerView.category_delete, name='category_delete'),

    # Product views
    path('oproducts/', OwnerView.product_list, name='product_list'),
    path('oproducts/create/', OwnerView.product_create, name='product_create'),
    path('oproducts/<slug:slug>/update/',
         OwnerView.product_update, name='product_update'),
    path('oproducts/<slug:slug>/delete/',
         OwnerView.product_delete, name='product_delete'),

    # ProductVariation views
    path('oproducts/<slug:product_slug>/variations/',
         OwnerView.product_variation_list, name='product_variation_list'),
    path('oproducts/<slug:product_slug>/variations/create/',
         OwnerView.product_variation_create, name='product_variation_create'),
    path('oproducts/<slug:product_slug>/variations/<int:id>/update/',
         OwnerView.product_variation_update, name='product_variation_update'),
    path('oproducts/<slug:product_slug>/variations/<int:id>/delete/',
         OwnerView.product_variation_delete, name='product_variation_delete'),


    path('sales-report/', SalesReportView.as_view(), name='sales_report'),
]
