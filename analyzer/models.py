from django.db import models
from scraper.models import Article, Post

class Sentiment(models.Model):
    SENTIMENT_CHOICES = [
        ('positive', 'Positive'),
        ('negative', 'Negative'),
        ('neutral', 'Neutral'),
    ]
    
    text = models.TextField()
    sentiment = models.CharField(max_length=10, choices=SENTIMENT_CHOICES)
    confidence_score = models.FloatField()
    analyzed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        abstract = True

class ArticleSentiment(Sentiment):
    article = models.OneToOneField(Article, on_delete=models.CASCADE, related_name='sentiment')
    
    def __str__(self):
        return f"{self.article.title[:50]}... - {self.sentiment}"

class PostSentiment(Sentiment):
    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name='sentiment')
    
    def __str__(self):
        return f"{self.post.content[:50]}... - {self.sentiment}"

class TrendingTopic(models.Model):
    keyword = models.CharField(max_length=100)
    frequency = models.IntegerField()
    sentiment_distribution = models.JSONField()  # Store positive/negative/neutral counts
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['keyword', 'date']
    
    def __str__(self):
        return f"{self.keyword} - {self.date}"