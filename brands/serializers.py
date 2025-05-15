from rest_framework import serializers
from django.core.cache import cache
from django.utils.text import slugify
from .models import Brand

class BrandSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Brand
        fields = ('id', 'name', 'slug', 'logo', 'logo_url', 'description', 
                 'landing_page_content', 'meta_title', 'meta_description', 
                 'is_active', 'created_at', 'updated_at')
        read_only_fields = ('slug', 'created_at', 'updated_at')
    
    def get_logo_url(self, obj):
        if obj.logo:
            return self.context['request'].build_absolute_uri(obj.logo.url)
        return None
    
    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Brand name cannot be empty.")
        
        # Check for duplicate names (case-insensitive)
        if Brand.objects.filter(name__iexact=value).exclude(
            pk=self.instance.pk if self.instance else None
        ).exists():
            raise serializers.ValidationError("A brand with this name already exists.")
        return value
    
    def validate_meta_description(self, value):
        if value and len(value) > 160:
            raise serializers.ValidationError(
                "Meta description should not exceed 160 characters for optimal SEO."
            )
        return value
    
    def create(self, validated_data):
        instance = super().create(validated_data)
        cache.delete('brand_list')
        cache.delete('active_brands')
        return instance
    
    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        cache.delete(f'brand_{instance.id}')
        cache.delete(f'brand_{instance.slug}')
        cache.delete('brand_list')
        cache.delete('active_brands')
        return instance 