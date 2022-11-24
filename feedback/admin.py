from django.contrib import admin
from .models import FeedbackModel


class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'subject', 'timestamp', 'is_active')
    search_fields = ('user', 'subject')
    readonly_fields = ('id', 'timestamp', 'subject', 'message', 'user', 'is_active')
    ordering = ()

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(FeedbackModel, FeedbackAdmin)
