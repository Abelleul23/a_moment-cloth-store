from django import forms
from .models import Cloth, Category, Product, ProductVariation

class ClothForm(forms.ModelForm):
    class Meta:
        model = Cloth
        fields = ['name', 'description']

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'cloth']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'category', 'price', 'quantity', 'image']

class ProductVariationForm(forms.ModelForm):
    class Meta:
        model = ProductVariation
        fields = ['product', 'size', 'color', 'quantity']