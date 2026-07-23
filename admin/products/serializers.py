# admin/products/serializers.py
from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'image', 'likes']
        extra_kwargs = {
            'likes': {'read_only': True, 'help_text': 'Managed automatically via Kafka events; not settable directly.'},
            'title': {'help_text': 'Product display name.'},
            'image': {'help_text': 'Public image URL (external link or MinIO-hosted).'},
        }