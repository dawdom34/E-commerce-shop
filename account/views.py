import json
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from product.models import Product

from .forms import RegistrationForm, AccountAuthenticationForm, AddressForm, AccountEditForm

from .models import Account, Address, Cart, OrderStatus, CartItem


def get_redirect_if_exist(request):
    """
    Returns the destination before the required login
    """
    redirect = None
    if request.GET:
        if request.GET.get('next'):
            redirect = str(request.GET.get('next'))
    return redirect


def register_view(request):
    """
    User registraction
    """
    # Check if user is already authenticated
    user = request.user
    if user.is_authenticated:
        return HttpResponse(f'You are already authenticated as {user}.')
    context = {}
    errors = False

    if request.POST:
        # Define form
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            # Getting email and password from form
            email = form.cleaned_data.get('email').lower()
            raw_password = form.cleaned_data.get('password1')
            # Authenticate the user and login
            account = authenticate(email=email, password=raw_password)
            login(request, account)
            return redirect('shop:home')
        else:
            context['registration_form'] = form
            errors = True
    else:
        form = RegistrationForm()
        context['registration_form'] = form

    if errors:
        return render(request, 'account/register.html', status=401, context=context)
    else:
        return render(request, 'account/register.html', context)


def logout_view(request, *args, **kwargs):
    """
    Logout user
    """
    logout(request)
    return redirect('login')


def login_view(request):
    """
    Login user
    """
    context = {}
    user = request.user
    errors = False
    # If user is already authenticated redirect him to homepage
    if user.is_authenticated:
        return redirect('shop:home')

    destination = get_redirect_if_exist(request)
    if request.POST:
        # Define form
        form = AccountAuthenticationForm(request.POST)
        if form.is_valid():
            # Get email and password from form
            email = request.POST['email']
            password = request.POST['password']
            # Authenticate and login user
            user = authenticate(email=email, password=password)
            login(request, user)
            if destination:
                return redirect(destination)
            return redirect('shop:home')
        else:
            errors = True
    else:
        form = AccountAuthenticationForm()

    context['login_form'] = form
    if errors:
        return render(request, 'account/login.html', status=401, context=context)
    else:
        return render(request, 'account/login.html', context)


@login_required(login_url='login')
def profile_view(request, *args, **kwargs):
    """
    User profile view
    """
    context = {}
    # Get user id from url
    user_id = kwargs.get('user_id')

    # Check if user with that id exist
    try:
        account = Account.objects.get(pk=user_id)
    except Account.DoesNotExist:
        return HttpResponse("That user doesn't exist.")

    # Check if user is trying to see his own profile
    if user_id != request.user.id:
        return HttpResponse('You cannot see other user profile')

    # Addresses of authenticated user
    addresses = Address.objects.filter(user=account)

    # Cart of auth user
    cart = Cart.objects.get(user=account, transaction_completed=False)

    # Five latest orders of auth user
    my_orders = Cart.objects.filter(user=account, transaction_completed=True).order_by('-timestamp')[:5]

    # Combine orders with latest status
    orders_with_status = []
    for order in my_orders:
        status = OrderStatus.objects.filter(order=order).order_by('-timestamp')
        orders_with_status.append((order, status[0].status))

    # Total number of items in cart
    counter = sum([item.quantity for item in cart.products.all()])

    if account:
        context['id'] = account.id
        context['name'] = account.name
        context['surname'] = account.surname
        context['email'] = account.email
        context['number'] = account.phone_number
        context['addresses'] = addresses
        context['c'] = counter
        context['order_with_status'] = orders_with_status

    return render(request, 'account/profile.html', context)


@login_required(login_url='login')
def address_add(request, *args, **kwargs):
    """
    Add user address
    """
    context = {}
    # Get user id from url
    id = kwargs.get('user_id')

    if request.method == 'GET':
        if id:
            # Check if user with that id exist
            try:
                account = Account.objects.get(pk=id)
            except Account.DoesNotExist:
                return HttpResponse('That user does not exist')
            # Check if user is trying to see his own addresses
            if id != request.user.id:
                return HttpResponse('You cannot see other user addresses')
            # Check if user have some addresses
            addresses = Address.objects.filter(user=account)

            # Total number of items in cart
            cart = Cart.objects.get(user=account, transaction_completed=False)
            counter = 0
            for item in cart.products.all():
                counter += item.quantity

            context['addresses'] = addresses
            context['c'] = counter
            context['form'] = AddressForm(account)
            return render(request, 'account/address.html', context)
    elif request.method == 'POST':
        if id:
            # Check if user with that id exist
            try:
                account = Account.objects.get(pk=id)
            except Account.DoesNotExist:
                return HttpResponse('That user does not exist')
            # Check if user is trying to see his own addresses
            if id != request.user.id:
                return HttpResponse('You cannot see other user addresses')

            # Get user with given id
            account = Account.objects.get(pk=id)
            # Get addresses of user
            addresses = Address.objects.filter(user=account)
            # Get cart of user
            cart = Cart.objects.get(user=account, transaction_completed=False)

            counter = 0
            # Total number of items in cart
            for item in cart.products.all():
                counter += item.quantity

            # Pass current user to the forms
            # Source: https://doraprojects.net/questions/5119994/get-current-user-in-django-form
            form = AddressForm(account, request.POST)
            if form.is_valid():
                new_address = form.save(commit=False)
                new_address.user = account
                new_address.save()
                return redirect('account:view', user_id=id)
            else:
                context['addresses'] = addresses
                context['c'] = counter
                context['form'] = form
                return render(request, 'account/address.html', status=401, context=context)


@login_required(login_url='login')
def account_edit_view(request, *args, **kwargs):
    """
    User account edit
    """
    context = {}
    # Get user id from url
    id = kwargs.get('user_id')

    # Check if user exist
    try:
        user = Account.objects.get(pk=id)
    except Account.DoesNotExist:
        return HttpResponse('User does not exist')

    # Check if user is trying to edit his own profile
    if user.pk != request.user.pk:
        return HttpResponse('You cannot edit someone else profile')

    # Get cart of auth user
    cart = Cart.objects.get(user=user, transaction_completed=False)
    counter = 0
    # Total number of items in cart
    for item in cart.products.all():
        counter += item.quantity

    errors = False

    if request.method == 'POST':
        form = AccountEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('account:view', user_id=user.pk)
        else:
            # Set initial values
            form = AccountEditForm(request.POST, instance=user,
                initial={
                    'id': user.pk,
                    'name': user.name,
                    'surname': user.surname,
                    'email': user.email,
                    'phone_number': user.phone_number
                })
            context['form'] = form
            context['c'] = counter
            errors = True
    else:
        # Set initial values
        form = AccountEditForm(initial={
            'id': user.pk,
            'name': user.name,
            'surname': user.surname,
            'email': user.email,
            'phone_number': user.phone_number
        })
        context['form'] = form
        context['c'] = counter

    if not errors:
        return render(request, 'account/profile_edit.html', context)
    else:
        return render(request, 'account/profile_edit.html', status=401, context=context)


def remove_address_view(request):
    """
    Removing an address from user addresses
    """
    payload = {}
    # Get auth user
    user = request.user
    if request.method == 'POST' and user.is_authenticated:
        # Get id of an address from request
        address_id = int(request.POST.get('address_id'))
        try:
            # Get address and delete
            address = Address.objects.get(pk=address_id)
            address.delete()
            payload['response'] = 'Address deleted.'
        except Address.DoesNotExist:
            payload['response'] = 'Unable to delete this address.'
    else:
        payload['response'] = 'You must be authenticated to delete this address'

    return HttpResponse(json.dumps(payload))


@login_required(login_url='login')
def cart_view(request, *args, **kwargs):
    """
    View all products in the cart
    """
    context = {}
    # Get user id from url
    id = kwargs.get('user_id')

    # Check if user exist
    try:
        user = Account.objects.get(pk=id)
    except Account.DoesNotExist:
        return HttpResponse('Something went wrong')

    # Check if user is trying to view his own cart
    if user.pk != request.user.pk:
        return HttpResponse('You cannot see other users carts')

    # Get cart of authenticated user
    try:
        cart = Cart.objects.get(user=user, transaction_completed=False)
    except Cart.DoesNotExist:
        # Should never happened
        cart = Cart.objects.create(user=user, transaction_completed=False)

    # Pagination setup
    p = Paginator(cart.products.all(), 5)
    page = request.GET.get('page')
    paginated = p.get_page(page)
    page_numbers = 'a' * paginated.paginator.num_pages

    # Total price of products in cart
    total_price = sum([product.product.product.price * product.quantity for product in cart.products.all()])

    # Calculate price after coupon apply
    # Check if coupon was applied to cart
    if cart.coupon != None:
        # Check if coupon is active
        if cart.coupon.is_active:
            # Coupon percentage discount
            d = cart.coupon.discount
            # Calculate the discount price
            discount = int((float(total_price) * int(d))/100)
            # Total price after discount
            price_after_discount = float(total_price) - float(discount)
            # Information about applied coupon
            coupon_applied = True
            # The coupon name
            coupon = cart.coupon
        else:
            # If coupon is not active but was applied in the past
            # Delete coupon from cart
            cart.delete_coupon()
            # Set coupon information to default values
            discount = 0
            price_after_discount = total_price
            coupon_applied = False
            coupon = None
            d = None
    else:
        # Coupon wasn't applied
        discount = 0
        price_after_discount = total_price
        coupon_applied = False
        coupon = None
        d = None

    # Total number of items in cart
    counter = sum([item.quantity for item in cart.products.all()])

    context['total_price'] = total_price
    context['cart'] = cart
    context['paginated'] = paginated
    context['page_numbers'] = page_numbers
    context['current_number'] = str(paginated.number)
    context['c'] = counter
    context['discount'] = discount
    context['price_after_discount'] = "%.2f" % price_after_discount
    context['coupon_applied'] = coupon_applied
    context['coupon'] = coupon
    context['d'] = d

    return render(request, 'account/cart.html', context)


def cart_product_add(request):
    """
    Adding product to cart
    """
    payload = {}
    user = request.user
    if request.method == 'POST' and user.is_authenticated:
        # Get product information from request
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity')
        color = request.POST.get('color')
        size = request.POST.get('size')
        try:
            # Get product with given id
            product = Product.objects.get(pk=product_id)
            # Get cart of auth user
            cart = Cart.objects.get(user=user, transaction_completed=False)
            # Add product to cart
            cart.add_product(product, quantity, color, size, user)
            payload['response'] = 'Product added.'
        except Product.DoesNotExist:
            payload['response'] = 'Unable to add this product.'
    else:
        payload['response'] = 'You must be authenticated to add this product'

    return HttpResponse(json.dumps(payload))


def cart_product_remove(request):
    """
    Removing product from cart
    """
    payload = {}
    user = request.user
    if request.method == 'POST' and user.is_authenticated:
        # Get id of product to remove
        product_id = request.POST.get('product_id')
        try:
            # Get cart of auth user
            cart = Cart.objects.get(user=user, transaction_completed=False)
            # Check if product exist
            product = CartItem.objects.get(id=product_id)
            # Initiate deleting process
            cart.delete_product(product_id)
            payload['response'] = 'Product deleted.'
        except CartItem.DoesNotExist:
            payload['response'] = 'Unable to delete this product.'
    else:
        payload['response'] = 'You must be authenticated to delete this product'

    return HttpResponse(json.dumps(payload))


@login_required(login_url='login')
def my_orders(request):
    """
    View all orders
    """
    context = {}
    user = request.user

    if user.is_authenticated:
        # Get all paid orders ordered by newest
        my_orders = Cart.objects.filter(user=user, transaction_completed=True).order_by('-timestamp')
        # Combine orders with latest status
        orders_with_status = []
        for order in my_orders:
            status = OrderStatus.objects.filter(order=order).order_by('-timestamp')
            orders_with_status.append((order, status[0].status))
        # Total number of items in cart
        cart = Cart.objects.get(user=user, transaction_completed=False)
        counter = sum([item.quantity for item in cart.products.all()])

        context['c'] = counter
        context['my_orders'] = my_orders
        context['orders_with_status'] = orders_with_status

    return render(request, 'account/my_orders.html', context)


@login_required(login_url='login')
def order_details(request, *args, **kwargs):
    """
    View order details
    """
    # Order id
    order_id = kwargs.get('order_id')
    user = request.user
    context = {}

    if user.is_authenticated:
        cart = Cart.objects.get(user=user, transaction_completed=False)
        # Total number of items in cart
        counter = sum([item.quantity for item in cart.products.all()])
        # Get order with given id
        order = Cart.objects.get(id=order_id)
        # Calculate total price of products in order
        total_price = sum([product.product.product.price * product.quantity for product in order.products.all()])

        # Calculate price after coupon apply
        # Check if coupon was applied
        if order.coupon:
            # Coupon percentage discount
            d = order.coupon.discount
            # Calculate the discount price
            discount = int((float(total_price) * int(d))/100)
            # Calculate total price aftert discount
            price_after_discount = float(total_price) - float(discount)
            # Information about coupon applied
            coupon_applied = True
            # The coupon name
            coupon = order.coupon
        else:
            # Coupon wasn't applied
            # Set coupon information co default values
            discount = 0
            price_after_discount = total_price
            coupon_applied = False
            coupon = None
            d = None
        # Get all status information about the order
        status = OrderStatus.objects.filter(order=order).order_by('-timestamp')

        context['order'] = order
        context['c'] = counter
        context['total_price'] = total_price
        context['price_after_discount'] = "%.2f" % price_after_discount
        context['coupon_applied'] = coupon_applied
        context['coupon'] = coupon
        context['discount'] = discount
        context['d'] = d
        context['status'] = status

    return render(request, 'account/order_details.html', context)
