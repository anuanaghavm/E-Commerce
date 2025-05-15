from rest_framework import generics, permissions, filters, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.core.cache import cache
from django.db.models import Q
from django.utils import timezone
from .models import Brand
from .serializers import BrandSerializer

class BrandListSerializer(BrandSerializer):
    class Meta(BrandSerializer.Meta):
        fields = ('id', 'name', 'is_active', 'created_at')

class BrandListView(generics.ListCreateAPIView):
    serializer_class = BrandSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        cache_key = 'brand_list'
        queryset = cache.get(cache_key)
        
        if queryset is None:
            queryset = Brand.objects.all()
            cache.set(cache_key, queryset, timeout=3600)
        
        # Apply filters
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Apply search
        search_query = self.request.query_params.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        return queryset

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return BrandListSerializer
        return BrandSerializer

    def perform_create(self, serializer):
        serializer.save()
        cache.delete('brand_list')
        cache.delete('active_brands')

class BrandDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BrandSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'

    def get_queryset(self):
        return Brand.objects.all()

    def get_object(self):
        slug = self.kwargs.get('slug')
        brand = Brand.get_brand_by_slug(slug)
        if brand is None:
            self.permission_denied(self.request)
        return brand

    def perform_update(self, serializer):
        instance = serializer.save()
        cache.delete(f'brand_{instance.slug}')
        cache.delete('brand_list')
        cache.delete('active_brands')

    def perform_destroy(self, instance):
        instance.delete()
        cache.delete(f'brand_{instance.slug}')
        cache.delete('brand_list')
        cache.delete('active_brands')

class BrandLandingPageView(generics.RetrieveAPIView):
    serializer_class = BrandSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'

    def get_queryset(self):
        return Brand.get_active_brands()

    def get_object(self):
        slug = self.kwargs.get('slug')
        brand = Brand.get_brand_by_slug(slug)
        if brand is None or not brand.is_active:
            self.permission_denied(self.request)
        return brand 