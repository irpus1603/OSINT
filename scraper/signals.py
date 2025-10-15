from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Article, Post

@receiver(post_save, sender=Article)
def article_post_save(sender, instance, created, **kwargs):
    """Signal handler for Article post-save"""
    if created:
        # Could add additional processing here when a new article is created
        pass

@receiver(post_save, sender=Post)
def post_post_save(sender, instance, created, **kwargs):
    """Signal handler for Post post-save"""
    if created:
        # Could add additional processing here when a new post is created
        pass