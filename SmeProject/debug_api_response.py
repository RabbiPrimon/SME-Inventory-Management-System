import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SmeProject.settings')
import django
django.setup()
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from SmeApp.models import Category, Supplier, Product

client = APIClient()
user = User.objects.create_user(username='testuser', password='password123')
client.force_authenticate(user=user)
cat = Category.objects.create(name='Garden')
supp = Supplier.objects.create(name='Supplier Y', email='suppliery@example.com', phone='2223334444')
prod = Product.objects.create(name='Garden Shovel', category=cat, supplier=supp, price='15.00', stock=25, reorder_level=5)
response = client.get('/api/products/')
print('status:', response.status_code)
print('content_type:', response['Content-Type'])
print('data_type:', type(response.data))
print('data_repr:', repr(response.data))
print('content_repr:', repr(response.content[:500]))
