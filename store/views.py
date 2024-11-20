from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Cart, Category, Order, OrderItem, Payment

def home(request):
    categories = Category.objects.all()
    featured_products = Product.objects.filter(stock_quantity__gt=0)[:6]
    
    context = {
        'categories': categories,
        'featured_products': featured_products
    }
    return render(request, 'store/home.html', context)

# def product_list(request, category_id=None):
    if category_id:
        products = Product.objects.filter(category_id=category_id)
    else:
        products = Product.objects.all()
    
    categories = Category.objects.all()
    
    context = {
        'products': products,
        'categories': categories
    }
    return render(request, 'store/product_list.html', context)

def product_list(request, category_id=None):
    if category_id:
        # Filter products by category
        products = Product.objects.filter(category_id=category_id, stock_quantity__gt=0)
    else:
        # Show all products with stock available
        products = Product.objects.filter(stock_quantity__gt=0)
    
    categories = Category.objects.all()
    
    context = {
        'products': products,
        'categories': categories,
    }
    return render(request, 'store/product_list.html', context)


# def product_detail(request, product_id):
    product = Product.objects.get(id=product_id)
    return render(request, 'store/product_detail.html', {'product': product})

def product_detail(request, product_id):
    # Get product details, raise 404 if not found
    product = get_object_or_404(Product, id=product_id, stock_quantity__gt=0)
    return render(request, 'store/product_detail.html', {'product': product})


# @login_required
# def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Check if product is in stock
    if product.stock_quantity <= 0:
        messages.error(request, "Product is out of stock!")
        return redirect('home')
    
    # Create or update cart item
    cart_item, created = Cart.objects.get_or_create(
        user=request.user, 
        product=product
    )
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    messages.success(request, f"{product.name} added to cart!")
    return redirect('home')

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Check if the requested quantity is more than the available stock
    quantity = int(request.POST.get('quantity', 1))
    if quantity > product.stock_quantity:
        messages.error(request, "Not enough stock available.")
        return redirect('product_detail', product_id=product.id)
    
    # Create or update the cart item
    cart_item, created = Cart.objects.get_or_create(
        user=request.user, 
        product=product
    )
    
    if not created:
        # If item already in cart, update quantity
        cart_item.quantity += quantity
        cart_item.save()
    else:
        # If new item, set initial quantity
        cart_item.quantity = quantity
        cart_item.save()
    
    messages.success(request, f"{product.name} added to cart!")
    return redirect('view_cart')  # Redirect to view cart page

@login_required
def view_cart(request):
    # Get all cart items for the current user
    cart_items = Cart.objects.filter(user=request.user)
    total = sum(item.product.price * item.quantity for item in cart_items)
    
    context = {
        'cart_items': cart_items,
        'total': total
    }
    return render(request, 'store/cart.html', context)

@login_required
def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(Cart, id=cart_item_id, user=request.user)
    cart_item.delete()
    messages.success(request, "Item removed from cart.")
    return redirect('view_cart')

@login_required
# def checkout(request):
#     cart_items = Cart.objects.filter(user=request.user)
#     total = sum(item.product.price * item.quantity for item in cart_items)
    
#     if request.method == 'POST':
#         # Create order
#         order = Order.objects.create(
#             user=request.user,
#             total_price=total,
#             is_completed=True
#         )
        
#         # Clear cart and update stock
#         for cart_item in cart_items:
#             product = cart_item.product
#             product.stock_quantity -= cart_item.quantity
#             product.save()
        
#         cart_items.delete()
        
#         messages.success(request, "Order placed successfully!")
#         return redirect('home')
    
#     context = {
#         'cart_items': cart_items,
#         'total': total
#     }
#     return render(request, 'store/checkout.html', context)

def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)
    total = sum(item.product.price * item.quantity for item in cart_items)
    
    if request.method == 'POST':
        # Create order with "Pending" payment status
        order = Order.objects.create(
            user=request.user,
            total_amount=total,
            payment_status='Pending',
            shipping_status='Pending'
        )
        
        # Create order items and reduce stock
        for cart_item in cart_items:
            product = cart_item.product
            product.stock_quantity -= cart_item.quantity
            product.save()
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=cart_item.quantity,
                price=product.price
            )
        
        # Clear cart
        cart_items.delete()
        
        # Redirect to payment page
        return redirect('payment', order_id=order.id)
    
    context = {
        'cart_items': cart_items,
        'total': total
    }
    return render(request, 'store/checkout.html', context)

@login_required
def payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        
        # Simulate payment processing
        Payment.objects.create(
            order=order,
            payment_method=payment_method,
            amount=order.total_amount
        )
        
        # Update order status
        order.payment_status = 'Completed'
        order.save()
        
        messages.success(request, "Payment successful! Order placed.")
        return redirect('home')
    
    return render(request, 'store/payment.html', {'order': order})
