from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.core.cache import cache
from django.db.models import F, Q
from categories.models import Category
from brands.models import Brand

class Product(models.Model):
    title = models.CharField(max_length=200)
    summary = models.TextField(max_length=500)
    description = models.TextField()
    sku = models.CharField(max_length=50, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='products')
    
    # Price and Discount.
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    offer_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    discount_percentage = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        null=True,
        blank=True
    )
    
    # SEO Fields
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(max_length=500, blank=True)
    slug = models.SlugField(max_length=200, unique=True)
    
    # Inventory
    stock_quantity = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=10)
    is_in_stock = models.BooleanField(default=True)
    
    # Status and Timestamps
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
            models.Index(fields=['category', 'brand']),
            models.Index(fields=['price']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_in_stock']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.meta_title:
            self.meta_title = self.title
        if not self.meta_description:
            self.meta_description = self.summary
        
        # Clear cache on save
        cache_keys = [
            f'product_{self.id}',
            f'product_{self.slug}',
            'product_list',
            'active_products',
            'low_stock_products',
            'on_sale_products'
        ]
        for key in cache_keys:
            cache.delete(key)
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return f'/products/{self.slug}/'
    
    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.low_stock_threshold
    
    @property
    def current_price(self):
        if self.offer_price and self.offer_price < self.price:
            return self.offer_price
        return self.price
    
    @property
    def discount_amount(self):
        if self.offer_price and self.offer_price < self.price:
            return self.price - self.offer_price
        return 0
    
    @property
    def discount_percentage_calculated(self):
        if self.price and self.offer_price:
            return int(((self.price - self.offer_price) / self.price) * 100)
        return 0

    @classmethod
    def get_active_products(cls):
        cache_key = 'active_products'
        queryset = cache.get(cache_key)
        if queryset is None:
            queryset = cls.objects.filter(is_active=True).select_related('category', 'brand')
            cache.set(cache_key, queryset, timeout=3600)  # Cache for 1 hour
        return queryset
    
    @classmethod
    def get_low_stock_products(cls):
        cache_key = 'low_stock_products'
        queryset = cache.get(cache_key)
        if queryset is None:
            queryset = cls.objects.filter(
                stock_quantity__lte=F('low_stock_threshold'),
                is_active=True
            ).select_related('category', 'brand')
            cache.set(cache_key, queryset, timeout=1800)  # Cache for 30 minutes
        return queryset
    
    @classmethod
    def get_on_sale_products(cls):
        cache_key = 'on_sale_products'
        queryset = cache.get(cache_key)
        if queryset is None:
            queryset = cls.objects.filter(
                offer_price__isnull=False,
                offer_price__lt=F('price'),
                is_active=True
            ).select_related('category', 'brand')
            cache.set(cache_key, queryset, timeout=1800)  # Cache for 30 minutes
        return queryset

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    is_feature = models.BooleanField(default=False)
    alt_text = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', '-is_feature']
        indexes = [
            models.Index(fields=['product', 'is_feature']),
        ]
    
    def __str__(self):
        return f"{self.product.title} - Image {self.order}"
    
    def save(self, *args, **kwargs):
        if self.is_feature:
            # Use update() for better performance
            ProductImage.objects.filter(
                product=self.product,
                is_feature=True
            ).update(is_feature=False)
        
        # Clear product cache
        cache.delete(f'product_{self.product.id}')
        cache.delete(f'product_{self.product.slug}')
        
        super().save(*args, **kwargs) 