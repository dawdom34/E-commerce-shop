import json
from django.shortcuts import render
from .models import Product
from django.http import HttpResponse
from django.core.paginator import Paginator

from .forms import FilterForm
from .models import Review

from account.models import Cart


def home_view(request):
    context = {}
    user = request.user
    if user.is_authenticated:
        cart = Cart.objects.get(user=user, transaction_completed=False)
        # Total number of items in cart
        counter = 0
        for item in cart.products.all():
            counter += item.quantity
        context['c'] = counter
    return render(request, 'shop_app/home.html', context)


def filtered_products(request, *args, **kwargs):
    """
    Show filter applied products
    """
    context = {}
    user = request.user
    PRODUCTS_PER_PAGE = 4
    errors = False

    if request.method == 'GET':
        # Filters initial values
        category = kwargs.get('category')
        size = 'Size'
        gender = 'Gender'
        price = 'Price'

        # Define form with initial values
        form = FilterForm(initial={
            'category': category,
            'size': size,
            'gender': gender,
            'price': price,
        })

        # Products filtered by category
        category_filtered = Product.objects.filter(product__category=category)

        products_list = category_filtered

        # Total number of items in cart
        counter = 0
        if user.is_authenticated:
            cart = Cart.objects.get(user=user, transaction_completed=False)
            for item in cart.products.all():
                counter += item.quantity

        # Pagination setup
        if products_list:
            p = Paginator(products_list, PRODUCTS_PER_PAGE)
            page = request.GET.get('page')
            paginated = p.get_page(page)
            page_numbers = 'a' * paginated.paginator.num_pages
            context['paginated'] = paginated
            context['page_numbers'] = page_numbers
            context['current_number'] = str(paginated.number)

        context['category'] = category
        context['form'] = form
        context['c'] = counter
    elif request.method == 'POST':

        form = FilterForm(request.POST)
        if form.is_valid():
            # Get data from form
            category = form.cleaned_data.get('category')
            size = form.cleaned_data['size']
            gender = form.cleaned_data['gender']
            price = form.cleaned_data['price']

            # Filter products by category
            category_filtered = Product.objects.filter(product__category=category)

            # If user imput some size, filter products by given size
            if size != 'Size' and size != 'All sizes':
                category_filtered = category_filtered.filter(sizes__size=size)

            # If user imput some gender, filter products by given gener
            if gender != 'Gender' and gender != 'All genders':
                category_filtered = category_filtered.filter(product__gender=gender)

            # Price filtering
            if price != 'Price' and price != 'All prices':
                if price == '50 or less':
                    category_filtered = category_filtered.filter(product__price__lte=50)
                elif price == '50 to 100':
                    category_filtered = category_filtered.filter(product__price__gte=50).filter(product__price__lte=100)
                elif price == '100 to 150':
                    category_filtered = category_filtered.filter(product__price__gte=100).filter(product__price__lte=150)
                else:
                    category_filtered = category_filtered.filter(product__price__gte=150)

            products_list = category_filtered

            # Total number of items in cart
            if user.is_authenticated:
                cart = Cart.objects.get(user=user, transaction_completed=False)
                counter = sum([item.quantity for item in cart.products.all()])
            else:
                counter = 0

            # Pagination setup

            p = Paginator(products_list, PRODUCTS_PER_PAGE)
            page = request.GET.get('page')
            paginated = p.get_page(page)
            page_numbers = 'a' * paginated.paginator.num_pages
            context['paginated'] = paginated
            context['page_numbers'] = page_numbers
            context['current_number'] = str(paginated.number)

            context['category'] = category
            context['size'] = size
            context['gender'] = gender
            context['price'] = price
            context['form'] = form
            context['c'] = counter
        else:
            errors = True

    if errors is False:
        return render(request, 'product/filtered.html', context)
    else:
        return render(request, 'product/filtered.html', status=401 ,context=context)


def product_details(request, *args, **kwargs):
    context = {}
    user = request.user
    # Get product id from url
    product_id = kwargs.get('product_id')
    # Get product from db
    product = Product.objects.get(id=product_id)

    # Get all reviews of current product
    reviews = Review.objects.filter(product=product).order_by('-timestamp')

    # Store all reviews combined with checked and unchecked stars
    rev = []
    stars = 'No data'
    if reviews:
        # Store all reviews score to calculate average
        avg_review = []
        for x in reviews.all():
            # Checked stars
            checked = 'a' * int(x.score)
            # unchecked stars
            unchecked = 'a'*(5-len(checked))
            # Add information about checked and unchecked star, to display it in review card
            rev.append((x, checked, unchecked))
            # Append score of review to calculate average score
            avg_review.append(x.score)

        average_score = int(sum(avg_review) / len(avg_review))
        # Information about checked and unchecked star, to display it in review card
        stars = ('a'*average_score, 'a'*(5-average_score))

    # Total number of items in cart
    if user.is_authenticated:
        cart = Cart.objects.get(user=user, transaction_completed=False)
        counter = 0
        for item in cart.products.all():
            counter += item.quantity
        # Get product review of authenticated user
        try:
            user_review = Review.objects.get(user=user, product=product)
            user_stars = 'a' * int(user_review.score)
            unchecked = 'a' * (5 - len(user_stars))
            user_review = (user_review, user_stars, unchecked)
        except Review.DoesNotExist:
            user_review = None
    else:
        counter = 0
        user_review = None

    context['product'] = product
    context['c'] = counter
    context['rev'] = rev
    context['stars'] = stars
    context['user_review'] = user_review

    return render(request, 'product/product_details.html', context)


def add_product_review(requets):
    """
    Add review of product
    """
    payload = {}
    user = requets.user
    if requets.method == 'POST' and user.is_authenticated:
        # Review
        review = requets.POST.get('review')
        # Stars score
        stars = requets.POST.get('stars')
        # Id of the product
        product_id = requets.POST.get('product_id')
        # Check if product exist
        try:
            product = Product.objects.get(id=product_id)
            # check if review already exist
            try:
                user_review = Review.objects.get(user=user, product=product, score=stars, review=review)
                payload['response'] = 'You have already rated this product.'
            except Review.DoesNotExist:
                Review.objects.create(user=user, product=product, score=stars, review=review)
                payload['response'] = 'Review added.'
        except Product.DoesNotExist:
            payload['response'] = 'Unable to add this review.'
    else:
        payload['response'] = 'You must be authenticated to add review.'

    return HttpResponse(json.dumps(payload))


def delete_product_review(request):
    """
    Delete review of product
    """
    payload = {}
    user = request.user
    if request.method == 'POST' and user.is_authenticated:
        # Get review if 
        review_id = request.POST.get('review_id')
        try:
            # Get review and delete
            review = Review.objects.get(id=review_id)
            review.delete()
            payload['response'] = 'Review deleted.'
        except Review.DoesNotExist:
            payload['response'] = 'Unable to delete this review.'
    else:
        payload['response'] = 'You must be authenticated to delete this review.'

    return HttpResponse(json.dumps(payload))
