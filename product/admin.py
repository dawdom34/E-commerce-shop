from django.contrib import admin
from .models import Size, Product, ProductAttribute, Color, Review


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'score', 'timestamp')
    search_fields = ('user', 'product', 'score')
    readonly_fields = ('id',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(Review, ReviewAdmin)


class ColorAdmin(admin.ModelAdmin):
    list_display = ('color',)
    search_fields = ('color',)
    readonly_fields = ('id',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(Color, ColorAdmin)


class SizeAdmin(admin.ModelAdmin):
    list_display = ('size',)
    search_fields = ('size',)
    readonly_fields = ('id',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(Size, SizeAdmin)


class ProductAttrAdmin(admin.ModelAdmin):
    list_display = ('category', 'name', 'description', 'price', 'gender')
    search_fields = ('category', 'price', 'gender', 'name')
    readonly_fields = ('id',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(ProductAttribute, ProductAttrAdmin)


class ProductAdmin(admin.ModelAdmin):
    list_display = ('product',)
    search_fields = ('product',)
    readonly_fields = ('id',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(Product, ProductAdmin)
