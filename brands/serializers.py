### serializers.py
from rest_framework import serializers
from .models import Brand,Category

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name', 'slug', 'logo', 'description', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['slug', 'created_at', 'updated_at']

class CategorySerializer(serializers.ModelSerializer):    
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug','description', 'image', 
                 'meta_title', 'meta_description', 'is_active', 
                 'created_at', 'updated_at')
        read_only_fields = ('slug', 'created_at', 'updated_at')