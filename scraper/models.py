from django.db import models
from django.contrib.auth.models import User

class Source(models.Model):
    name = models.CharField(max_length=100)
    url = models.URLField()
    source_type = models.CharField(max_length=20, choices=[
        ('news', 'News Media'),
        ('social', 'Social Media'),
    ])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Keyword(models.Model):
    term = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.term

class Article(models.Model):
    title = models.CharField(max_length=500)
    url = models.URLField(unique=True)
    content = models.TextField()
    excerpt = models.TextField(blank=True)
    published_at = models.DateTimeField()
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    keywords = models.ManyToManyField(Keyword, blank=True)
    scraped_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Post(models.Model):
    content = models.TextField()
    url = models.URLField(unique=True)
    author = models.CharField(max_length=100, blank=True)
    author_username = models.CharField(max_length=100, blank=True)
    published_at = models.DateTimeField()
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    keywords = models.ManyToManyField(Keyword, blank=True)
    likes_count = models.IntegerField(default=0)
    retweets_count = models.IntegerField(default=0)
    replies_count = models.IntegerField(default=0)
    scraped_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content[:100] + '...' if len(self.content) > 100 else self.content