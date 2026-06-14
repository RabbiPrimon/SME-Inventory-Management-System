from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from SmeApp.models import Category, Supplier, Product, Order


class ProductApiTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.category = Category.objects.create(name='Garden')
        self.supplier = Supplier.objects.create(
            name='Supplier Y',
            email='suppliery@example.com',
            phone='2223334444',
        )
        self.product = Product.objects.create(
            name='Garden Shovel',
            category=self.category,
            supplier=self.supplier,
            price='15.00',
            stock=25,
            reorder_level=5,
        )
        self.client.force_authenticate(user=self.user)

    def test_list_products(self):
        url = reverse('product-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertTrue(any(item.get('name') == 'Garden Shovel' for item in results if isinstance(item, dict)))

    def test_create_product(self):
        url = reverse('product-list-create')
        payload = {
            'name': 'Garden Fork',
            'category_id': self.category.id,
            'supplier_id': self.supplier.id,
            'price': '12.00',
            'stock': 30,
            'reorder_level': 8,
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Garden Fork')
        self.assertEqual(response.data['category']['name'], 'Garden')

    def test_retrieve_product(self):
        url = reverse('product-detail', kwargs={'pk': self.product.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Garden Shovel')


class OrderApiTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='orderuser', password='password123')
        self.category = Category.objects.create(name='Office Supplies')
        self.supplier = Supplier.objects.create(
            name='Supplier Z',
            email='supplierz@example.com',
            phone='5556667777',
        )
        self.product = Product.objects.create(
            name='Desk Pad',
            category=self.category,
            supplier=self.supplier,
            price='20.00',
            stock=40,
            reorder_level=10,
        )
        self.client.force_authenticate(user=self.user)

    def test_create_order(self):
        url = reverse('order-list-create')
        payload = {
            'status': 'pending',
            'items': [
                {
                    'product_id': self.product.id,
                    'quantity': 2,
                    'price': '20.00',
                }
            ]
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'pending')
        self.assertEqual(len(response.data['items']), 1)
