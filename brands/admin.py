from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Brand

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'active_status', 'created_date', 'actions')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
class BrandAdmin(admin.ModelAdmin):
    ordering = ('-created_at','',)
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 20

    def active_status(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="color: green; font-weight: bold;">Active</span>'
            )
        return format_html(
            '<span style="color: red; font-weight: bold;">Inactive</span>'
        )
    active_status.short_description = 'Status'

    def created_date(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M')
    created_date.short_description = 'Created Date'
    created_date.admin_order_field = 'created_at'

    def actions(self, obj):
        return format_html(
            '<a class="button" href="{}">View</a>&nbsp;'
            '<a class="button" href="{}">Edit</a>',
            obj.get_absolute_url(),
            f'/admin/brands/brand/{obj.id}/change/'
        )
    actions.short_description = 'Actions'

    def get_queryset(self, request):
        return super().get_queryset(request).order_by('-created_at') 