from django.urls import path

from .views import (
    CategoryListCreateView,
    SupplierListCreateView,
    ProductListCreateView,
    ProductDetailView,
    OrderListCreateView,
    OrderDetailView,
    LowStockAlertsView,
)

urlpatterns = [
    path('categories/', CategoryListCreateView.as_view(), name='category-list-create'),
    path('suppliers/', SupplierListCreateView.as_view(), name='supplier-list-create'),
    path('products/', ProductListCreateView.as_view(), name='product-list-create'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('orders/', OrderListCreateView.as_view(), name='order-list-create'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('alerts/low-stock/', LowStockAlertsView.as_view(), name='low-stock-alerts'),
]