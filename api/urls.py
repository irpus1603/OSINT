from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'api'

router = DefaultRouter()
router.register(r'articles', views.ArticleViewSet)
router.register(r'posts', views.PostViewSet)
router.register(r'sources', views.SourceViewSet)
router.register(r'keywords', views.KeywordViewSet)

urlpatterns = [
    path('', include(router.urls)),
]