from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse
import json

from product.forms import ProductCreationForm
from product.models import Product, ProductAttribute, Color, Size

from account.models import OrderStatus, Cart

from coupons.forms import CouponForm
from coupons.models import Coupon

from feedback.models import FeedbackModel


@login_required(login_url='login')
def add_product(request):
    user = request.user
    context = {}
    if user.is_staff:
        if request.method == 'GET':
            productform = ProductCreationForm()
            context['form'] = productform
        elif request.method == 'POST':
            productform = ProductCreationForm(request.POST, request.FILES)
            if productform.is_valid():
                category = productform.cleaned_data['category']
                name = productform.cleaned_data['name']
                description = productform.cleaned_data['description']
                main_image = productform.cleaned_data['main_image']
                image1 = productform.cleaned_data['image1']
                image2 = productform.cleaned_data['image2']
                image3 = productform.cleaned_data['image3']
                image4 = productform.cleaned_data['image4']
                price = productform.cleaned_data['price']
                gender = productform.cleaned_data['gender']
                composition = productform.cleaned_data['composition']
                sizes = productform.cleaned_data['sizes']
                colors = productform.cleaned_data['colors']

                # Create product attribute object
                attr = ProductAttribute.objects.create(
                    category=category,
                    name=name,
                    description=description,
                    main_image=main_image,
                    image1=image1,
                    image2=image2,
                    image3=image3,
                    image4=image4,
                    price=price,
                    gender=gender,
                    composition=composition)
                attr.save()
                # Create product object with given attributes
                prod = Product.objects.create(product=attr)
                # Add colors and sizes
                for x in colors:
                    prod.colors.add(Color.objects.get(color=x))
                    prod.save()
                    # Add selected sizes to manyToMany relation
                for x in sizes:
                    prod.sizes.add(Size.objects.get(size=x))
                    prod.save()
                return redirect('management:product_add')
            context['form'] = productform

        return render(request, 'management/add_product.html', context)


@login_required(login_url='login')
def orders_view_collecting_an_items(request):
    """
    View all orders with status 'Collecting an items'
    """
    user = request.user
    context = {}
    if user.is_staff:
        # Get all orders witch contains 'Collecting an items' status
        status = OrderStatus.objects.filter(status='Collecting an items').order_by('timestamp')
        orders = []
        for order in status.all():
            # Find orders with only one status
            check = OrderStatus.objects.filter(order=order.order)
            if len(check.all()) == 1:
                orders.append(order)
        # Pagination setup
        p_orders = Paginator(orders, 10)
        page = request.GET.get('page')
        paginated_orders = p_orders.get_page(page)
        context['paginated_orders'] = paginated_orders
    return render(request, 'management/orders_status_collecting.html', context)


@login_required(login_url='login')
def orders_view_waiting_for_shipment(request):
    """
    View all orders with status 'Waiting for shipment'
    """
    user = request.user
    context = {}
    if user.is_staff:
        # Get all orders witch contains 'Waiting for shipment' status
        status = OrderStatus.objects.filter(status='Waiting for shipment').order_by('timestamp')
        orders = []
        for order in status.all():
            # Find orders with two status
            check = OrderStatus.objects.filter(order=order.order)
            if len(check.all()) == 2:
                orders.append(order)
        # Pagination setup
        p_orders = Paginator(orders, 10)
        page = request.GET.get('page')
        paginated_ready = p_orders.get_page(page)
        context['paginated_ready'] = paginated_ready
    return render(request, 'management/orders_status_ready.html', context)


@login_required(login_url='login')
def orders_view_shipped(request):
    """
    View all orders with status 'Shipped'
    """
    user = request.user
    context = {}
    if user.is_staff:
        # Get all orders witch contains 'Shipped' status
        status = OrderStatus.objects.filter(status='Shipped').order_by('timestamp')
        orders = []
        for order in status.all():
            # Find orders with three status
            check = OrderStatus.objects.filter(order=order.order)
            if len(check.all()) == 3:
                orders.append(order)
        # Pagination setup
        p_orders = Paginator(orders, 10)
        page = request.GET.get('page')
        paginated_shipped = p_orders.get_page(page)
        context['paginated_shipped'] = paginated_shipped
    return render(request, 'management/orders_status_shipped.html', context)


@login_required(login_url='login')
def orders_view_delivered(request):
    """
    View all orders with status 'Delivered'
    """
    user = request.user
    context = {}
    if user.is_staff:
        # Get all orders witch contains 'Shipped' status
        status = OrderStatus.objects.filter(status='Delivered').order_by('timestamp')
        orders = []
        for order in status.all():
            # Find orders with three status
            check = OrderStatus.objects.filter(order=order.order)
            if len(check.all()) == 4:
                orders.append(order)
        # Pagination setup
        p_orders = Paginator(orders, 10)
        page = request.GET.get('page')
        paginated_delivered = p_orders.get_page(page)
        context['paginated_delivered'] = paginated_delivered
    return render(request, 'management/orders_status_delivered.html', context)


@login_required(login_url='login')
def add_coupon(request):
    """
    Add new coupon
    """
    user = request.user
    context = {}
    if user.is_staff:
        if request.method == 'GET':
            form = CouponForm()
            context['form'] = form
        elif request.method == 'POST':
            form = CouponForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('management:add_coupon')
            context['form'] = form
    return render(request, 'management/coupon_add.html', context)


@login_required(login_url='login')
def coupons_management(request):
    """
    View all coupons and manage them
    """
    user = request.user
    context = {}
    if user.is_staff:
        # Get all coupons
        coupons = Coupon.objects.all()
        # Pagination setup
        coup = Paginator(coupons, 10)
        page = request.GET.get('page')
        paginated_coupons = coup.get_page(page)
        context['paginated_coupons'] = paginated_coupons
    return render(request, 'management/coupons_management.html', context)


@login_required(login_url='login')
def feedback(request):
    """
    View feedback of clients
    """
    user = request.user
    context = {}
    if user.is_staff:
        feedback = FeedbackModel.objects.filter(subject='Feedback').filter(is_active=True).order_by('-timestamp')
        p_feedback = Paginator(feedback, 15)
        page = request.GET.get('page')
        paginated_feedback = p_feedback.get_page(page)
        context['paginated_feedback'] = paginated_feedback
    return render(request, 'management/feedback.html', context)


@login_required(login_url='login')
def questions(request):
    """
    View questions of clients
    """
    user = request.user
    context = {}
    if user.is_staff:
        questions = FeedbackModel.objects.filter(subject='Question').filter(is_active=True).order_by('-timestamp')
        p_questions = Paginator(questions, 15)
        page = request.GET.get('page')
        paginated_questions = p_questions.get_page(page)
        context['paginated_questions'] = paginated_questions
    return render(request, 'management/questions.html', context)


@login_required(login_url='login')
def issues(request):
    """
    View issues of clients
    """
    user = request.user
    context = {}
    if user.is_staff:
        issues = FeedbackModel.objects.filter(subject='Issue').filter(is_active=True).order_by('-timestamp')
        p_issues = Paginator(issues, 15)
        page = request.GET.get('page')
        paginated_issues = p_issues.get_page(page)
        context['paginated_issues'] = paginated_issues
    return render(request, 'management/issues.html', context)


@login_required(login_url='login')
def order_details(request, *args, **kwargs):
    """
    Details of order
    """
    context = {}
    user = request.user
    order_id = kwargs.get('order_id')
    status = kwargs.get('status')

    if user.is_staff:
        # Get the order
        order = Cart.objects.get(id=order_id)

        # Pagination setup
        p = Paginator(order.products.all(), 5)
        page = request.GET.get('page')
        paginated = p.get_page(page)

        context['paginated'] = paginated
        context['order'] = order
        context['current_number'] = str(paginated.number)
        context['status'] = status

    return render(request, 'management/order_details.html', context)


@login_required(login_url='login')
def set_new_status(request):
    """
    Create new status object
    """
    payload = {}
    user = request.user

    if request.method == 'POST' and user.is_staff:
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('new_status')
        try:
            order = Cart.objects.get(id=order_id)
            new_status = OrderStatus.objects.create(order=order, status=new_status)
            new_status.save()
            payload['response'] = 'Success'
        except Cart.DoesNotExist:
            payload['response'] = 'Unable to update status'
    else:
        payload['response'] = 'You must be authenticated to change the status'

    return HttpResponse(json.dumps(payload))
