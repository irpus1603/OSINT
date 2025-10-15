from django.db import models
from django.contrib.auth.models import User
from scraper.models import Keyword, Source
from analyzer.models import TrendingTopic

class DashboardConfig(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    sources = models.ManyToManyField(Source, blank=True)
    keywords = models.ManyToManyField(Keyword, blank=True)
    date_range = models.CharField(max_length=20, default='7d', choices=[
        ('1d', 'Last 24 Hours'),
        ('7d', 'Last 7 Days'),
        ('30d', 'Last 30 Days'),
        ('90d', 'Last 90 Days'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Dashboard config for {self.user.username}"

class Alert(models.Model):
    ALERT_TYPE_CHOICES = [
        ('sentiment', 'Sentiment Threshold'),
        ('volume', 'Volume Threshold'),
        ('keyword', 'Keyword Mention'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPE_CHOICES)
    threshold = models.FloatField(null=True, blank=True)  # For sentiment/volume alerts
    keywords = models.ManyToManyField(Keyword, blank=True)  # For keyword alerts
    is_active = models.BooleanField(default=True)
    email_notifications = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"

class Report(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    generated_at = models.DateTimeField(auto_now_add=True)
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    
    def __str__(self):
        return f"{self.title} - {self.generated_at.date()}"