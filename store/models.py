from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


class User(AbstractUser):
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='store_users',
        verbose_name='groups',
        blank=True,
        help_text=(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='store_user_permissions',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
    )


class Cloth(models.Model):
    """Model for the different types of clothing"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Cloth, self).save(*args, **kwargs)


class Category(models.Model):
    """Model for the categories of clothing"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    cloth = models.ForeignKey(
        Cloth, on_delete=models.CASCADE, related_name='categories')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    """Model for the products in the store"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='products', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)
    image = models.ImageField(
        upload_to='product_images', null=True, blank=True)

    def __str__(self):
        return f"{self.name}, {self.category.name}, {self.quantity}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        
        # Save the product instance to ensure it has a primary key
        super(Product, self).save(*args, **kwargs)
        
        # Now that the instance has a primary key, calculate the total quantity
        self.total_quantity = sum(
            variation.quantity for variation in self.variations.all())
        
        # Update the quantity with the total quantity
        self.quantity = self.total_quantity
        
        # Save again to update the quantity field
        super(Product, self).save(*args, **kwargs)



class ProductVariation(models.Model):
    """Model for the variations of a product"""
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='variations')
    size = models.CharField(max_length=50)
    color = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product.name} ({self.size}, {self.color}) - {self.quantity}"


class SaleItem(models.Model):
    """Model for each item sold in a particular sale"""
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='sale_items')
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)
    size = models.CharField(max_length=50)
    color = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.product.name} ({self.size}, {self.color}) - {self.quantity}"


class Sale(models.Model):
    """Model for a collection of SaleItems for a particular day or salesperson"""
    salesperson = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='sales', blank=True, null=True)
    sale_date = models.DateField(auto_now_add=True)
    sale_items = models.ManyToManyField(SaleItem, related_name='sales')

    def get_total_price(self):
        """Calculates the total price of all items in the sale"""
        total = 0
        for item in self.sale_items.all():
            # Use item price if set, otherwise product price
            price = item.price or item.product.price
            total += item.quantity * price
        return total

    def __str__(self):
        # Assuming User has a name field
        return f"Sale on {self.sale_date.strftime('%Y-%m-%d')} by {self.salesperson}"


@receiver(post_save, sender=ProductVariation)
@receiver(post_delete, sender=ProductVariation)
def update_product_quantity(sender, instance, **kwargs):
    product = instance.product
    product.total_quantity = sum(
        variation.quantity for variation in product.variations.all())
    product.quantity = product.total_quantity
    product.save()
