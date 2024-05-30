from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, Product, ProductVariation, Sale, SaleItem
from django.contrib import messages


def product_catalog(request):
    categories = Category.objects.all()
    products = Product.objects.prefetch_related('category', 'variations').all()
    context = {
        'categories': categories,
        'products': products,
    }
    return render(request, 'store/product_catalog.html', context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    variations = product.variations.all()
    context = {
        'product': product,
        'variations': variations
    }
    return render(request, 'store/product_detail.html', context)


def product_list_by_category(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    products = Product.objects.filter(category=category)
    return render(request, 'store/product_list_by_category.html', {'products': products, 'category': category})


def add_to_sale(request):
    """Handles adding a product to the temporary sale (cart) in session"""
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 1))  # Default quantity to 1
    price = request.POST.get('price')  # Optional price override
    size = request.POST.get('size')
    color = request.POST.get('color')

    if not product_id or quantity <= 0:
        messages.error(request, "Invalid product or quantity.")
        return redirect('product_catalog')

    try:
        product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        messages.error(request, "Product not found.")
        return redirect('product_catalog')

    # Get sale items from session (or create an empty list)
    sale_items = request.session.get('sale_items', [])

    # Check if item already exists in the cart
    existing_item = next((item for item in sale_items if item['product_id'] ==
                         product_id and item['size'] == size and item['color'] == color), None)
    if existing_item:
        existing_item['quantity'] += quantity
    else:
        sale_items.append({
            'product_id': product_id,
            'quantity': quantity,
            # Use price override if provided, and convert Decimal to float
            'price': float(Decimal(price or product.price).quantize(Decimal('0.00'))),
            'size': size,
            'color': color,
        })

    request.session['sale_items'] = sale_items
    messages.success(request, f"Added {quantity} {
                     product.name} ({size}, {color}) to sale.")

    # Redirect back to the product catalog or previous page (consider using referrer)
    return redirect('product_catalog')


def review_sale(request):
    """Displays the list of products currently in the sale (cart)"""
    sale_items = request.session.get('sale_items', [])
    products = []
    total_price = 0

    for item in sale_items:
        product = get_object_or_404(Product, pk=item['product_id'])
        products.append({
            'product': product,
            'quantity': item['quantity'],
            'price': item['price'],
            'size': item['size'],
            'color': item['color'],
            'total_item_price': item['quantity'] * item['price'],
        })
        total_price += item['quantity'] * item['price']

    context = {
        'sale_items': products,
        'total_price': total_price,
    }
    return render(request, 'store/review_sale.html', context)


def submit_sale(request):
    """Handles submitting the final sale"""
    sale_items = request.session.get('sale_items', [])

    if not sale_items:
        messages.error(request, "Your sale cart is empty.")
        return redirect('review_sale')

    # Create Sale object (consider adding salesperson information if needed)
    sale = Sale.objects.create()

    for item in sale_items:
        product = get_object_or_404(Product, pk=item['product_id'])

        # Check if the product has variations
        product_variations = ProductVariation.objects.filter(
            product=product, size=item['size'], color=item['color'])

        if product_variations.exists():
            # Product has variations, update the corresponding ProductVariation
            product_variation = product_variations.first()
            if item['quantity'] > product_variation.quantity:
                messages.error(request, f"Not enough stock for {product.name} ({item['size']}, {
                               item['color']}) - only {product_variation.quantity} available.")
                return redirect('review_sale')
            product_variation.quantity -= item['quantity']
            product_variation.save()
        else:
            # Product doesn't have variations, update the Product directly
            if item['quantity'] > product.quantity:
                messages.error(request, f"Not enough stock for {
                               product.name} - only {product.quantity} available.")
                return redirect('review_sale')
            product.quantity -= item['quantity']
            product.save()

        # Create SaleItem object and add it to the Sale
        sale_item = SaleItem.objects.create(
            product=product,
            quantity=item['quantity'],
            price=item['price'],
            size=item['size'],
            color=item['color'],
        )
        sale.sale_items.add(sale_item)

    # Clear sale items from session
    del request.session['sale_items']

    messages.success(request, "Sale submitted successfully!")
    # Redirect to a success page or salesperson dashboard
    return redirect('product_catalog')  # Replace with appropriate URL
