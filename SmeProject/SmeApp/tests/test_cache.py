from django.test import TestCase, override_settings
from django.core.cache import cache
from SmeApp.models import Category, Supplier, Product


class CacheBehaviorTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Test')
        self.supplier = Supplier.objects.create(
            name='Cache Supplier',
            email='cache@example.com',
            phone='0001112222',
        )
        self.product = Product.objects.create(
            name='Cached Product',
            category=self.category,
            supplier=self.supplier,
            price='8.00',
            stock=8,
            reorder_level=10,
        )

    def tearDown(self):
        cache.clear()

    def test_basic_cache_operations(self):
        cache.set('cache_key', 'cache_value', 60)
        self.assertEqual(cache.get('cache_key'), 'cache_value')
        cache.delete('cache_key')
        self.assertIsNone(cache.get('cache_key'))

    def test_cache_expiration(self):
        cache.set('temp_key', 'value', 1)
        self.assertEqual(cache.get('temp_key'), 'value')
        import time
        time.sleep(1.1)
        self.assertIsNone(cache.get('temp_key'))

    @override_settings(CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    })
    def test_object_cache_with_product_list(self):
        products = list(Product.objects.values('id', 'name'))
        cache.set('product_list', products, 300)
        self.assertEqual(cache.get('product_list'), products)
