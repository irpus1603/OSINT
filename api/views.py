from rest_framework import viewsets, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import ArticleSerializer, PostSerializer, SourceSerializer, KeywordSerializer
from scraper.models import Article, Post, Source, Keyword
from scraper.services import ScraperService

class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['title', 'content']
    filterset_fields = ['source', 'published_at']

class PostViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['content']
    filterset_fields = ['source', 'published_at']

class SourceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Source.objects.all()
    serializer_class = SourceSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['source_type', 'is_active']

class KeywordViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Keyword.objects.all()
    serializer_class = KeywordSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['term']

    @action(detail=False, methods=['get'])
    def stats(self, request):
        stats = ScraperService.get_scraping_stats()
        return Response(stats)
