from rest_framework import serializers
from .models import Product, ProductImage
from categories.serializers import CategorySerializer
from brands.serializers import BrandSerializer

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'is_feature', 'alt_text', 'order']
        read_only_fields = ['id']

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        write_only=True,
        source='category'
    )
    brand = BrandSerializer(read_only=True)
    brand_id = serializers.PrimaryKeyRelatedField(
        queryset=Brand.objects.all(),
        write_only=True,
        source='brand'
    )
    images = ProductImageSerializer(many=True, read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_percentage_calculated = serializers.IntegerField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'summary', 'description', 'sku',
            'category', 'category_id', 'brand', 'brand_id',
            'price', 'offer_price', 'discount_percentage',
            'meta_title', 'meta_description', 'slug',
            'stock_quantity', 'low_stock_threshold', 'is_in_stock',
            'is_active', 'created_at', 'updated_at',
            'images', 'is_low_stock', 'current_price',
            'discount_amount', 'discount_percentage_calculated'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'slug']

    def validate(self, data):
        if 'offer_price' in data and data['offer_price'] >= data['price']:
            raise serializers.ValidationError(
                "Offer price must be less than regular price"
            )
        return data

class ProductListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    feature_image = serializers.SerializerMethodField()
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_percentage_calculated = serializers.IntegerField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'summary', 'sku',
            'category', 'brand', 'feature_image',
            'current_price', 'discount_percentage_calculated',
            'is_in_stock', 'is_active'
        ]

    def get_feature_image(self, obj):
        feature_image = obj.images.filter(is_feature=True).first()
        if feature_image:
            return ProductImageSerializer(feature_image).data
        return None 