from rest_framework import serializers
from scraper.models import Article, Post, Source, Keyword

class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = '__all__'

class KeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keyword
        fields = '__all__'

class ArticleSerializer(serializers.ModelSerializer):
    source = SourceSerializer(read_only=True)
    keywords = KeywordSerializer(many=True, read_only=True)
    
    class Meta:
        model = Article
        fields = '__all__'

class PostSerializer(serializers.ModelSerializer):
    source = SourceSerializer(read_only=True)
    keywords = KeywordSerializer(many=True, read_only=True)
    
    class Meta:
        model = Post
        fields = '__all__'