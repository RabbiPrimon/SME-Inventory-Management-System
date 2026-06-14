from django.test import TestCase
from SmeApp.models import Category, Supplier, Product, Order, OrderItem


class ProductModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Office Supplies')
        self.supplier = Supplier.objects.create(
            name='Supplier A',
            email='supplierA@example.com',
            phone='1234567890',
        )
        self.product = Product.objects.create(
            name='Stapler',
            category=self.category,
            supplier=self.supplier,
            price='12.50',
            stock=10,
            reorder_level=5,
        )

    def test_product_string_representation(self):
        self.assertEqual(str(self.product), 'Stapler')

    def test_product_low_stock_property(self):
        self.assertFalse(self.product.is_low_stock)
        self.product.stock = 4
        self.product.save()
        self.assertTrue(self.product.is_low_stock)


class OrderModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Office Supplies')
        self.supplier = Supplier.objects.create(
            name='Supplier B',
            email='supplierB@example.com',
            phone='0987654321',
        )
        self.product = Product.objects.create(
            name='Paper',
            category=self.category,
            supplier=self.supplier,
            price='5.00',
            stock=100,
            reorder_level=20,
        )
        self.order = Order.objects.create(status='pending')
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=5,
            price='5.00',
        )

    def test_order_string_representation(self):
        self.assertEqual(str(self.order), f'Order #{self.order.id} - pending')

    def test_order_item_relationships(self):
        self.assertEqual(self.order_item.order, self.order)
        self.assertEqual(self.order_item.product, self.product)
