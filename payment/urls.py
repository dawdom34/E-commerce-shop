from django.urls import path
from .views import checkout, payment, charge

app_name = 'payment'

urlpatterns = [
    path('checkout/', checkout, name='checkout'),
    path('charge/', charge, name='charge'),
    path('payment/<int:address_id>/<str:payment_method>', payment, name='payment'),
]
