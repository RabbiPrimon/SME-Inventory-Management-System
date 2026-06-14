from django.test import TestCase
from SmeApp.models import Category, Supplier, Product, Order, OrderItem
from SmeApp.serializers import CategorySerializer, SupplierSerializer, ProductSerializer, OrderSerializer


class SerializerTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Hardware')
        self.supplier = Supplier.objects.create(
            name='Supplier X',
            email='supplierx@example.com',
            phone='1112223333',
        )
        self.product = Product.objects.create(
            name='Notebook',
            category=self.category,
            supplier=self.supplier,
            price='7.25',
            stock=50,
            reorder_level=10,
        )
        self.order_data = {
            'status': 'pending',
            'items': [
                {
                    'product_id': self.product.id,
                    'quantity': 3,
                    'price': '7.25',
                }
            ]
        }

    def test_category_serializer(self):
        serializer = CategorySerializer(self.category)
        self.assertEqual(serializer.data['name'], 'Hardware')

    def test_supplier_serializer(self):
        serializer = SupplierSerializer(self.supplier)
        self.assertEqual(serializer.data['email'], 'supplierx@example.com')

    def test_product_serializer_read(self):
        serializer = ProductSerializer(self.product)
        self.assertEqual(serializer.data['name'], 'Notebook')
        self.assertEqual(serializer.data['category']['name'], 'Hardware')
        self.assertEqual(serializer.data['supplier']['name'], 'Supplier X')

    def test_order_serializer_create(self):
        serializer = OrderSerializer(data=self.order_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        order = serializer.save()
        self.assertEqual(order.status, 'pending')
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.items.first().quantity, 3)
