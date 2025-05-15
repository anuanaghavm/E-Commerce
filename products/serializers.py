# products/serializers.py
from rest_framework import serializers
from .models import Product, ProductAttribute
from brands.models import Brand, Category

class ProductAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAttribute
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    variants = ProductAttributeSerializer(many=True, read_only=True)  # Related name: variants
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = '__all__'
