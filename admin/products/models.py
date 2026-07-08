from django.db import models

class Product(models.Model):
  title = models.CharField(max_length=200)
  image = models.CharField(max_length=200)
  likes = models.PositiveBigIntegerField(default=0)

  def __str__(self):
    return self.name

class User(models.Model):
  pass
