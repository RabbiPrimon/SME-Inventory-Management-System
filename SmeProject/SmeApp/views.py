from django.db.models import F, Count, Sum, DecimalField
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.core.cache import cache
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Category, Supplier, Product, Order
from .serializers import (
    CategorySerializer,
    SupplierSerializer,
    ProductSerializer,
    OrderSerializer,
)


class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class SupplierListCreateView(generics.ListCreateAPIView):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer


@method_decorator(cache_page(300), name='dispatch')
class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.select_related('category', 'supplier').all()
    serializer_class = ProductSerializer

    def post(self, request, *args, **kwargs):
        """Create product and clear cache"""
        response = super().post(request, *args, **kwargs)
        cache.delete('product_list')
        cache.delete('dashboard_data')
        cache.delete('top_selling_products')
        return response


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.select_related('category', 'supplier').all()
    serializer_class = ProductSerializer

    def put(self, request, *args, **kwargs):
        """Update product and clear cache"""
        response = super().put(request, *args, **kwargs)
        cache.delete('product_list')
        cache.delete('dashboard_data')
        cache.delete('top_selling_products')
        return response

    def patch(self, request, *args, **kwargs):
        """Partial update and clear cache"""
        response = super().patch(request, *args, **kwargs)
        cache.delete('product_list')
        cache.delete('dashboard_data')
        cache.delete('top_selling_products')
        return response

    def delete(self, request, *args, **kwargs):
        """Delete product and clear cache"""
        response = super().delete(request, *args, **kwargs)
        cache.delete('product_list')
        cache.delete('dashboard_data')
        cache.delete('top_selling_products')
        return response



@method_decorator(cache_page(300), name='dispatch')
class OrderListCreateView(generics.ListCreateAPIView):
    queryset = Order.objects.prefetch_related('items__product').all()
    serializer_class = OrderSerializer

    def post(self, request, *args, **kwargs):
        """Create order and clear cache"""
        response = super().post(request, *args, **kwargs)
        cache.delete('dashboard_data')
        cache.delete('top_selling_products')
        return response


class OrderDetailView(generics.RetrieveAPIView):
    queryset = Order.objects.prefetch_related('items__product').all()
    serializer_class = OrderSerializer


class LowStockAlertsView(APIView):
    """Get products with low stock - cached for 5 minutes"""

    @method_decorator(cache_page(300))
    def get(self, request):
        cache_key = 'low_stock_alerts'
        cached_data = cache.get(cache_key)
        
        if cached_data is not None:
            return Response(cached_data)
        
        products = Product.objects.filter(stock__lte=F('reorder_level'))
        serializer = ProductSerializer(products, many=True)
        
        # Cache the result
        cache.set(cache_key, serializer.data, 300)  # 5 minutes
        return Response(serializer.data)


class DashboardView(APIView):
    """Dashboard endpoint with aggregated inventory statistics - cached for 10 minutes"""

    def get(self, request):
        cache_key = 'dashboard_data'
        cached_data = cache.get(cache_key)
        
        if cached_data is not None:
            return Response(cached_data)
        
        # Calculate dashboard statistics
        total_products = Product.objects.count()
        total_categories = Category.objects.count()
        total_suppliers = Supplier.objects.count()
        
        # Stock statistics
        total_stock_value = Product.objects.aggregate(
            total=Sum(F('stock') * F('price'), output_field=DecimalField())
        )['total'] or 0
        
        low_stock_count = Product.objects.filter(
            stock__lte=F('reorder_level')
        ).count()
        
        # Order statistics
        total_orders = Order.objects.count()
        pending_orders = Order.objects.filter(status='pending').count()
        completed_orders = Order.objects.filter(status='completed').count()
        
        dashboard_data = {
            'overview': {
                'total_products': total_products,
                'total_categories': total_categories,
                'total_suppliers': total_suppliers,
                'low_stock_alerts': low_stock_count,
            },
            'inventory': {
                'total_stock_value': float(total_stock_value),
            },
            'orders': {
                'total_orders': total_orders,
                'pending_orders': pending_orders,
                'completed_orders': completed_orders,
                'completion_rate': round(
                    (completed_orders / total_orders * 100) if total_orders > 0 else 0, 2
                ),
            },
        }
        
        # Cache the result for 10 minutes
        cache.set(cache_key, dashboard_data, 600)
        return Response(dashboard_data)


class TopSellingProductsView(APIView):
    """Get top selling products based on order quantity - cached for 1 hour"""

    def get(self, request):
        cache_key = 'top_selling_products'
        cached_data = cache.get(cache_key)
        
        if cached_data is not None:
            return Response(cached_data)
        
        # Get top 10 products by quantity ordered
        top_products = Product.objects.annotate(
            total_ordered=Sum('orderitem__quantity')
        ).filter(
            total_ordered__isnull=False
        ).order_by('-total_ordered')[:10]
        
        serializer = ProductSerializer(top_products, many=True)
        data = [
            {
                **prod,
                'total_ordered': int(top_products.get(id=prod['id']).total_ordered or 0)
            }
            for prod in serializer.data
        ]
        
        # Cache the result for 1 hour
        cache.set(cache_key, data, 3600)
        return Response(data)
