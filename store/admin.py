from django.contrib import admin
from .models import User, Cloth, Category, Product, ProductVariation, Sale, SaleItem

# Register the models with the admin site
admin.site.register(User)


class ClothAdmin(admin.ModelAdmin):
    # Display only the "name" field in the admin list view
    list_display = ('name',)


admin.site.register(Cloth, ClothAdmin)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_cloth_name')  # Use a custom method

    def get_cloth_name(self, obj):
        """Returns the name of the related Cloth object"""
        try:
            # Access the related Cloth object's name (preferred)
            return obj.cloth.name
        except Cloth.DoesNotExist:
            return 'Cloth not assigned'  # Handle missing Cloth object gracefully

    # Set a descriptive label for the column
    get_cloth_name.short_description = 'Cloth'


admin.site.register(Category, CategoryAdmin)

admin.site.register(Product)
admin.site.register(ProductVariation)

admin.site.register(Sale)
admin.site.register(SaleItem)
