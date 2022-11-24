from django.urls import path
from .views import (add_product, 
    orders_view_collecting_an_items, 
    orders_view_waiting_for_shipment,
     orders_view_shipped, 
     orders_view_delivered, 
     add_coupon, 
     coupons_management, 
     feedback,
     questions,
     issues,
     order_details,
     set_new_status,
)
app_name = 'management'

urlpatterns = [
    # Create new product
    path('add_product', add_product, name='product_add'),
    # Orders with status 'Collecting an items'
    path('orders/collecting_an_items/', orders_view_collecting_an_items, name='collecting'),
    # Orders with status 'Ready for shipment'
    path('orders/waiting_for_shipment/', orders_view_waiting_for_shipment, name='ready'),
    # Orders with status 'Shipped'
    path('orders/shipped/', orders_view_shipped, name='shipped'),
    # Orders with status 'Delivered'
    path('orders/delivered/', orders_view_delivered, name='delivered'),
    # Add coupon code
    path('coupons/add/', add_coupon, name='add_coupon'),
    # Coupons management
    path('coupons/management/', coupons_management, name='coupons_management'),
    # Feedback from clients
    path('feedback/', feedback, name='feedback'),
    # Questions from clients
    path('questions/', questions, name='questions'),
    # Issues from clients
    path('issues/', issues, name='issues'),
    # Order details
    path('details/<int:order_id>/<int:status>/', order_details, name='details'),
    # Set new order status
    path('set_new_status/', set_new_status, name='set_new_status')
]
