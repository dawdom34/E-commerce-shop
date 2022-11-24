from django.http import HttpResponse
import json
from account.models import Cart
from coupons.models import Coupon


def coupon_apply(request):
    """
    Apply coupon to cart
    """
    payload = {}
    user = request.user
    if request.method == 'POST' and user.is_authenticated:
        # Get the data from request
        coupon = request.POST.get('coupon')
        cart_id = request.POST.get('cart_id')
        try:
            # Get the cart of auth user
            cart = Cart.objects.get(id=cart_id, transaction_completed=False)
            # If cart have no coupon code
            if cart.coupon is None:
                try:
                    # Check if coupon exist and is active
                    c = Coupon.objects.get(coupon=coupon, is_active=True)
                    try:
                        # Check if coupon is already used by this user
                        completed_carts = Cart.objects.get(user=user, transaction_completed=True, coupon=c)
                        payload['response'] = 'You already used this coupon.'
                    except Cart.DoesNotExist:
                        cart.add_coupon(c)
                        payload['response'] = 'Coupon applied.'
                except Coupon.DoesNotExist:
                    payload['response'] = 'Coupon does not exist.'
            # Cart already have some coupon in use
            else:
                payload['response'] = 'You already have a coupon in use.'
        # Unexpected error
        except:
            payload['response'] = 'Unable to apply this coupon.'

    return HttpResponse(json.dumps(payload))


def change_coupon_status(request):
    """
    Change coupon status (is_active):
    - if True, change to False and vice versa
    """
    payload = {}
    user = request.user
    if request.method == 'POST' and user.is_authenticated and user.is_staff:
        # Get the data from request
        # Id of coupon
        coupon_id = request.POST.get('coupon_id')
        # The status to which the coupon needs to be changed
        status = request.POST.get('status')
        try:
            # Check if coupon exist
            coupon = Coupon.objects.get(id=coupon_id)
            if status == 'Deactivate':
                coupon.deactivate_coupon()
                coupon.save()
                payload['response'] = 'Coupon status changed.'
            elif status == 'Activate':
                coupon.activate_coupon()
                coupon.save()
                payload['response'] = 'Coupon status changed.'
            else:
                payload['response'] = 'Unable to change the status.'      
        except Coupon.DoesNotExist:
            payload['response'] = 'Coupon does not exist.'

    return HttpResponse(json.dumps(payload))
