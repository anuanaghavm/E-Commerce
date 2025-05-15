from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'products', views.ProductViewSet)
router.register(r'products/(?P<product_pk>\d+)/images', views.ProductImageViewSet, basename='product-image')

urlpatterns = [
    path('', include(router.urls)),
] 