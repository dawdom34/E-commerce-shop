from django.shortcuts import redirect, render
from django.core.paginator import Paginator
from account.models import Cart, Address
from django.conf import settings
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY


def checkout(request):
    """
    Order summary
    """
    context = {}
    user = request.user

    if request.method == 'GET':
        if user.is_authenticated:
            # Get addresses of auth user
            addresses = Address.objects.filter(user=user)

            # Get cart of authenticated user
            cart = Cart.objects.get(user=user, transaction_completed=False)

            # Pagination setup
            p = Paginator(cart.products.all(), 5)
            page = request.GET.get('page')
            paginated = p.get_page(page)
            page_numbers = 'a' * paginated.paginator.num_pages

            # Total price of products
            total_price = 0
            for product in cart.products.all():
                total_price += (product.product.product.price * product.quantity)

            # Calculate price after coupon apply
            # Check if coupon was applied
            if cart.coupon is not None:
                # Check if coupon is active
                if cart.coupon.is_active:
                    # Coupon percentage discount
                    d = cart.coupon.discount
                    # Calculate the discount price
                    discount = int((float(total_price) * int(d))/100)
                    # Calculate total price after discount
                    price_after_discount = float(total_price) - float(discount)
                    # Information about coupon applied
                    coupon_applied = True
                    # The coupon name
                    coupon = cart.coupon
                else:
                    # Delete inactive coupon
                    cart.delete_coupon()
                    # Set price information to default
                    discount = 0
                    price_after_discount = total_price
                    coupon_applied = False
                    coupon = None
                    d = None
            else:
                # Coupon wasn't applied
                # Set price information to default
                discount = 0
                price_after_discount = total_price
                coupon_applied = False
                coupon = None
                d = None

            # Total number of items in cart
            counter = 0
            for item in cart.products.all():
                counter += item.quantity

            context['total_price'] = total_price
            context['c'] = counter
            context['cart'] = cart
            context['paginated'] = paginated
            context['page_numbers'] = page_numbers
            context['current_number'] = str(paginated.number)
            context['addresses'] = addresses
            context['price_after_discount'] = "%.2f" % price_after_discount
            context['coupon_applied'] = coupon_applied
            context['coupon'] = coupon
            context['d'] = d

    return render(request, 'payment/checkout.html', context)


def payment(request, *args, **kwargs):
    """
    Payment with chosen method
    """
    context = {}
    user = request.user
    payment = kwargs.get('payment_method')
    address_id = kwargs.get('address_id')

    if user.is_authenticated:
        address = Address.objects.get(id=address_id)
        cart = Cart.objects.get(user=user, transaction_completed=False)
        cart.add_address(address_id)
        # Total price of products
        total_price = 0
        for product in cart.products.all():
            total_price += (product.product.product.price * product.quantity)
        if cart.coupon is not None:
            if cart.coupon.is_active:
                d = cart.coupon.discount
                discount = int((float(total_price) * int(d))/100)
                price_after_discount = float(total_price) - float(discount)
            else:
                cart.delete_coupon()
                discount = 0
                price_after_discount = total_price

        else:
            discount = 0
            price_after_discount = total_price

        # Total number of items in cart
        counter = 0
        for item in cart.products.all():
            counter += item.quantity

        price_after_discount = price_after_discount*100
        context['user'] = user
        context['address'] = address
        context['payment_method'] = payment
        context['price_after_discount'] = "%.2f" % price_after_discount
        context['key'] = settings.STRIPE_PUBLISHABLE_KEY
        context['c'] = counter

    return render(request, 'payment/payment.html', context)


def charge(request):
    """
    Finalize payment
    """
    user = request.user

    if user.is_authenticated:
        cart = Cart.objects.get(user=user, transaction_completed=False)
        # Calculate total price of products in cart
        total_price = 0
        for product in cart.products.all():
            total_price += (product.product.product.price * product.quantity)
        total_price = int(total_price*100)
        # Create stripe request
        if request.method == 'POST':
            charge = stripe.Charge.create(
                amount=total_price,
                currency='usd',
                description='Payment Gateway',
                source=request.POST['stripeToken']
            )
            # Mark cart as complete
            cart.mark_as_complete()

    return redirect('account:my_orders')
