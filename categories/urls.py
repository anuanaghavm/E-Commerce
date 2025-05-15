from django.urls import path
from .views import CategoryListView, CategoryDetailView, CategoryChildrenView

urlpatterns = [
    path('category', CategoryListView.as_view(), name='category-list'),
    path('<slug:slug>/', CategoryDetailView.as_view(), name='category-detail'),
    path('<slug:slug>/children/', CategoryChildrenView.as_view(), name='category-children'),
] 