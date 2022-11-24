from django.urls import path

from .views import (profile_view, 
    address_add, 
    account_edit_view, 
    remove_address_view, 
    cart_view, 
    cart_product_remove, 
    cart_product_add, 
    my_orders, 
    order_details)
  
app_name = 'account'


urlpatterns = [
    # View user profile
    path('<int:user_id>/', profile_view, name='view'),
    # View user addresses/add new address
    path('<int:user_id>/address/', address_add, name='address'),
    # Edit profile
    path('<int:user_id>/edit_profile/', account_edit_view, name='edit_profile'),
    # View user cart
    path('<int:user_id>/cart/', cart_view, name='cart'),
    # Remove address
    path('remove_address/', remove_address_view, name='remove_address'),
    # Remove product from cart
    path('cart_remove_product/', cart_product_remove, name='cart_remove_product'),
    # Add product to cart
    path('cart_add_product/', cart_product_add, name='cart_add_product'),
    # View user orders
    path('my_orders/', my_orders, name='my_orders'),
    # View details of order
    path('order/<int:order_id>', order_details, name='order_details'),
]
