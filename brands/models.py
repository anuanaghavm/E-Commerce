from django.db import models
from django.utils.text import slugify
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

class Brand(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    logo = models.ImageField(upload_to='brands/logos/', blank=True, null=True)
    description = models.TextField(blank=True)
    landing_page_content = models.TextField(blank=True)
    meta_title = models.CharField(max_length=100, blank=True)
    meta_description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Brand'
        verbose_name_plural = 'Brands'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['is_active']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        self.clear_cache()

    def delete(self, *args, **kwargs):
        self.clear_cache()
        super().delete(*args, **kwargs)

    def get_absolute_url(self):
        return f'/brands/{self.slug}/'

    def clear_cache(self):
        """Clear all cached data related to this brand"""
        cache_keys = [
            f'brand_{self.id}',
            f'brand_{self.slug}',
            'brand_list',
            'active_brands',
        ]
        cache.delete_many(cache_keys)

    @classmethod
    def get_active_brands(cls):
        """Get all active brands with caching"""
        cache_key = 'active_brands'
        brands = cache.get(cache_key)
        if brands is None:
            brands = list(cls.objects.filter(is_active=True))
            cache.set(cache_key, brands, timeout=3600)  # Cache for 1 hour
        return brands

    @classmethod
    def get_brand_by_slug(cls, slug):
        """Get brand by slug with caching"""
        cache_key = f'brand_{slug}'
        brand = cache.get(cache_key)
        if brand is None:
            try:
                brand = cls.objects.get(slug=slug)
                cache.set(cache_key, brand, timeout=3600)
            except cls.DoesNotExist:
                return None
        return brand

# Signal handlers for cache management
@receiver([post_save, post_delete], sender=Brand)
def clear_brand_cache(sender, instance, **kwargs):
    instance.clear_cache() 