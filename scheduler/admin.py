from django.contrib import admin
from scheduler.models import CrawlTask, CrawlLog

@admin.register(CrawlTask)
class CrawlTaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'source', 'frequency', 'is_active', 'status', 'last_run', 'next_run')
    list_filter = ('frequency', 'is_active', 'status', 'source')
    search_fields = ('name',)
    filter_horizontal = ('keywords',)

@admin.register(CrawlLog)
class CrawlLogAdmin(admin.ModelAdmin):
    list_display = ('task', 'started_at', 'finished_at', 'status', 'items_scraped')
    list_filter = ('status', 'started_at', 'task')
    search_fields = ('task__name', 'error_message')