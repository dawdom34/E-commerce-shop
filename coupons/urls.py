from django.urls import path
from .views import coupon_apply, change_coupon_status

app_name = 'coupons'


urlpatterns = [
    # Apply coupon to cart
    path('coupon_apply/', coupon_apply, name='coupon_apply'),
    # Change coupon status
    path('coupon/change_status/', change_coupon_status, name='coupon_change_status'),
]
