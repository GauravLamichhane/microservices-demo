from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from .models import Product
from .producer import publish

@receiver(post_save, sender=Product)
def product_saved(sender, instance, created, **kwargs):
    event_type = 'product_created' if created else 'product_updated'
    publish(event_type, {
        'id': instance.id,
        'title': instance.title,
        'image': instance.image,
        'likes': instance.likes,
    })

@receiver(post_delete, sender=Product)
def product_deleted(sender, instance, **kwargs):
    publish('product_deleted', instance.pk)