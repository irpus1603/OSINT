from django.contrib import admin
from scraper.models import Source, Keyword, Article, Post

@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'source_type', 'is_active', 'created_at')
    list_filter = ('source_type', 'is_active', 'created_at')
    search_fields = ('name', 'url')

@admin.register(Keyword)
class KeywordAdmin(admin.ModelAdmin):
    list_display = ('term', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('term',)

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'source', 'published_at', 'scraped_at')
    list_filter = ('source', 'published_at', 'scraped_at')
    search_fields = ('title', 'content')
    filter_horizontal = ('keywords',)
    date_hierarchy = 'published_at'

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('content', 'author', 'source', 'published_at', 'likes_count', 'retweets_count')
    list_filter = ('source', 'published_at', 'scraped_at')
    search_fields = ('content', 'author')
    filter_horizontal = ('keywords',)
    date_hierarchy = 'published_at'