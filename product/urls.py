from django.urls import path
from .views import home_view, filtered_products, product_details, add_product_review, delete_product_review


app_name = 'product'

urlpatterns = [
    # Home screen
    path('', home_view, name='home'),
    # Category filtered
    path('filtered/<str:category>/', filtered_products, name='filtered'),
    # Product details
    path('details/<int:product_id>/', product_details, name='details'),
    # Add review of product
    path('add_product_review/', add_product_review, name='add_product_review'),
    # Delete review of product
    path('delete_product_review/', delete_product_review, name='delete_product_review'),
]
