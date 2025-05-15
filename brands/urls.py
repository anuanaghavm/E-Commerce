from django.urls import path
from .views import BrandListView, BrandDetailView, BrandLandingPageView

app_name = 'brands'

urlpatterns = [
    path('', BrandListView.as_view(), name='brand-list'),
    path('<slug:slug>/', BrandDetailView.as_view(), name='brand-detail'),
    path('landing/<slug:slug>/', BrandLandingPageView.as_view(), name='brand-landing'),
] 