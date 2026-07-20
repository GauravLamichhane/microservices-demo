from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Product, PublishedEvent


@receiver(post_save, sender=Product)
def product_saved(sender, instance, created, update_fields=None, **kwargs):
    if update_fields and set(update_fields) == {'likes'}:
        return

    event_type = 'product_created' if created else 'product_updated'
    PublishedEvent.objects.create(
        channel='product-events',
        payload={
            'id': instance.id,
            'title': instance.title,
            'image': instance.image,
            'likes': instance.likes,
        },
        extra={'type': event_type},
    )


@receiver(post_delete, sender=Product)
def product_deleted(sender, instance, **kwargs):
    PublishedEvent.objects.create(
        channel='product-events',
        payload=instance.pk,
        extra={'type': 'product_deleted'},
    )