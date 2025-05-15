from django.db import models
from django.utils.text import slugify
from brands.models import Brand,Category

class Product(models.Model):
    title = models.CharField(max_length=255)
    summary = models.TextField(blank=True)
    image = models.ImageField(upload_to='products/images/')
    description = models.TextField()
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    sku = models.CharField(max_length=100, unique=True)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')

    price = models.DecimalField(max_digits=10, decimal_places=2)
    offer_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    discount_percent = models.FloatField(blank=True, null=True)

    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)
    
    is_active = models.BooleanField(default=True)
    stock_quantity = models.IntegerField(default=0)
    stock_alert = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class ProductAttribute(models.Model):
    name = models.CharField(max_length=100)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    sku = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/variants/', blank=True, null=True)
    stock = models.IntegerField(default=0)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.product.title} Variant - {self.sku}"