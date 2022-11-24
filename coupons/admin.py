from django.contrib import admin
from .models import Coupon


class CouponAdmin(admin.ModelAdmin):
    list_display = ('coupon', 'discount', 'is_active', 'counter')
    search_fields = ('coupon', 'discount')
    readonly_fields = ('id', 'counter', 'discount')
    ordering = ()

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(Coupon, CouponAdmin)
