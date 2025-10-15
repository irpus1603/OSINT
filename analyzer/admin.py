from django.contrib import admin
from analyzer.models import ArticleSentiment, PostSentiment, TrendingTopic

@admin.register(ArticleSentiment)
class ArticleSentimentAdmin(admin.ModelAdmin):
    list_display = ('article', 'sentiment', 'confidence_score', 'analyzed_at')
    list_filter = ('sentiment', 'analyzed_at')
    search_fields = ('article__title', 'text')

@admin.register(PostSentiment)
class PostSentimentAdmin(admin.ModelAdmin):
    list_display = ('post', 'sentiment', 'confidence_score', 'analyzed_at')
    list_filter = ('sentiment', 'analyzed_at')
    search_fields = ('post__content', 'text')

@admin.register(TrendingTopic)
class TrendingTopicAdmin(admin.ModelAdmin):
    list_display = ('keyword', 'frequency', 'date', 'created_at')
    list_filter = ('date', 'created_at')
    search_fields = ('keyword',)