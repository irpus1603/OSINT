from django.contrib import admin
from dashboard.models import DashboardConfig, Alert, Report

@admin.register(DashboardConfig)
class DashboardConfigAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_range', 'created_at', 'updated_at')
    list_filter = ('date_range', 'created_at', 'updated_at')
    search_fields = ('user__username',)

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'alert_type', 'is_active', 'email_notifications', 'created_at')
    list_filter = ('alert_type', 'is_active', 'email_notifications', 'created_at')
    search_fields = ('name', 'user__username')
    filter_horizontal = ('keywords',)

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'generated_at', 'period_start', 'period_end')
    list_filter = ('generated_at',)
    search_fields = ('title', 'user__username')