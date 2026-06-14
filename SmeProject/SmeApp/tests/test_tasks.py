from django.test import TestCase, override_settings
from django.core import mail
from django.core.cache import cache
from SmeApp.models import Category, Supplier, Product, Order, OrderItem
from SmeApp.tasks import test_task, check_low_stock_and_alert, generate_weekly_report, calculate_sales_analytics


class CeleryTaskTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Analytics')
        self.supplier = Supplier.objects.create(
            name='Analytics Supplier',
            email='analytics@example.com',
            phone='1110002222',
        )
        self.product = Product.objects.create(
            name='Analytics Product',
            category=self.category,
            supplier=self.supplier,
            price='10.00',
            stock=3,
            reorder_level=5,
        )
        self.order = Order.objects.create(status='completed')
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            price='10.00',
        )

    def tearDown(self):
        cache.clear()

    def test_test_task(self):
        result = test_task(message='Hello')
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['message'], 'Hello')

    def test_low_stock_alert_task(self):
        cache.clear()
        result = check_low_stock_and_alert()
        self.assertEqual(result['status'], 'success')
        self.assertIn('low_stock_count', result)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_generate_weekly_report_task(self):
        mail.outbox = []
        result = generate_weekly_report()
        self.assertEqual(result['status'], 'success')
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Weekly Inventory Report', mail.outbox[0].subject)

    def test_calculate_sales_analytics_task(self):
        cache.clear()
        result = calculate_sales_analytics()
        self.assertEqual(result['status'], 'success')
        self.assertIn('analytics', result)
        cached = cache.get('sales_analytics')
        self.assertIsNotNone(cached)
