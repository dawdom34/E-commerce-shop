"""shop_app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from account.views import register_view, login_view, logout_view
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),

    # Auth
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    # Account
    path('account/', include('account.urls', namespace='account')),

    # Coupons
    path('coupons/', include('coupons.urls', namespace='coupons')),

    # Feedback
    path('feedback/', include('feedback.urls', namespace='feedback')),

    # Management
    path('management/', include('management.urls', namespace='management')),

    # Shop
    path('', include('product.urls', namespace='shop')),

    # Password change
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='password_reset/password_change.html'), name='password_change'),
    path('password_change_done/', auth_views.PasswordChangeView.as_view(template_name='password_reset/password_change_done.html'), name='password_change_done'),

    # Password reset
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset/password_reset_form.html'), name='password_reset'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='password_reset/password_reset_complete.html'), name='password_reset_complete'),
    path('password_reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='password_reset/password_reset_done.html'), name='password_reset_done'),

    # Payment
    path('payment/', include('payment.urls', namespace='payment'))
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
