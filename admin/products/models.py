from django.db import models

class Product(models.Model):
  title = models.CharField(max_length=200)
  image = models.CharField(max_length=200)
  likes = models.PositiveBigIntegerField(default=0)

  def __str__(self):
    return self.title

class User(models.Model):
  pass


class PublishedEvent(models.Model):
  channel = models.CharField(max_length=100) # product-events
  payload = models.JSONField()
  extra = models.JSONField(default=dict, blank=True) #event type headers
  is_consumed = models.BooleanField(default=False)
  created_at = models.DateTimeField(auto_now_add=True)
  