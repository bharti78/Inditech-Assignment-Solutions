from django.contrib import admin
from .models import Customer, AdminLog

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'email', 'phone', 'created_by', 'created_at')
    list_filter = ('created_at', 'gender')
    search_fields = ('first_name', 'last_name', 'email', 'phone')
    readonly_fields = ('created_at', 'updated_at', 'pdf_file')

@admin.register(AdminLog)
class AdminLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'timestamp')
    list_filter = ('action', 'timestamp')
    search_fields = ('user__username', 'details')
    readonly_fields = ('user', 'action', 'details', 'timestamp')

