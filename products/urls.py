from django.urls import path, include
from rest_framework.routers import DefaultRouter
from views import ProductListCreateAPIView,ProductRetrieveUpdateDestroyAPIView,ProductAttributeListCreateAPIView,ProductAttributeRetrieveupdateDestroyAPIView

urlpatterns = [
    path('product/',ProductListCreateAPIView.as_view(),name="product-list-create"),
    path('product/<int:pk>/',ProductRetrieveUpdateDestroyAPIView.as_view(),name="product-retrieve-update-destroy")
]