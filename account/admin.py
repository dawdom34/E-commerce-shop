from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account, Address, Cart, CartItem, OrderStatus


class AccountAdmin(UserAdmin):
    list_display = ('email', 'name', 'surname', 'date_joined', 'is_admin', 'is_staff')
    search_fields = ('email', 'name', 'surname')
    readonly_fields = ('id', 'date_joined', 'last_login')
    ordering = ()

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'surname', 'phone_number', 'password1', 'password2'),
            #              🖞 without username
        }),
    )


admin.site.register(Account, AccountAdmin)


class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'country', 'city', 'address1')
    search_fields = ('country', 'city', 'address1', 'user__name', 'user__surname')
    readonly_fields = ('id',)
    ordering = ()

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(Address, AddressAdmin)


class CardAdmin(admin.ModelAdmin):
    list_display = ('user', 'transaction_completed', 'timestamp')
    search_fields = ('user',)
    readonly_fields = ('id', 'timestamp', 'transaction_completed')
    ordering = ()

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(Cart, CardAdmin)


class CartItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'color', 'size')
    search_fields = ('product',)
    readonly_fields = ('id',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(CartItem, CartItemAdmin)


class OrderStatusAdmin(admin.ModelAdmin):
    list_display = ('order', 'status', 'timestamp')
    search_fields = ('order', 'status', 'timestamp')
    readonly_fields = ('id',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(OrderStatus, OrderStatusAdmin)
