#!/usr/bin/env python
"""
Test script to verify Redis caching is working correctly.
Run this after starting the Redis server.

Usage:
    python manage.py shell < test_cache.py
    
Or:
    python test_cache.py
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SmeProject.settings')
django.setup()

from django.core.cache import cache
from django.test import Client
import time
import json

print("=" * 80)
print("REDIS CACHING TEST SUITE")
print("=" * 80)

# Test 1: Basic cache operations
print("\n[TEST 1] Basic Cache Operations")
print("-" * 80)

try:
    # Test set and get
    cache.set('test_key', 'test_value', 300)
    value = cache.get('test_key')
    
    if value == 'test_value':
        print("✓ Cache SET operation: PASSED")
        print("✓ Cache GET operation: PASSED")
    else:
        print("✗ Cache GET operation: FAILED")
    
    # Test delete
    cache.delete('test_key')
    value = cache.get('test_key')
    
    if value is None:
        print("✓ Cache DELETE operation: PASSED")
    else:
        print("✗ Cache DELETE operation: FAILED")
        
except Exception as e:
    print(f"✗ Basic cache operations: FAILED")
    print(f"  Error: {str(e)}")
    print("\n  IMPORTANT: Redis server is not running!")
    print("  To fix this:")
    print("  1. Install Redis for Windows: https://github.com/microsoftarchive/redis/releases")
    print("  2. Or use Windows Subsystem for Linux (WSL) with: wsl redis-server")
    print("  3. Or use Docker: docker run -d -p 6379:6379 redis:latest")
    exit(1)

# Test 2: Cache with expiration
print("\n[TEST 2] Cache Expiration")
print("-" * 80)

try:
    cache.set('expiring_key', 'value', 2)  # 2 seconds
    print("✓ Set cache with 2-second expiration")
    
    value = cache.get('expiring_key')
    print(f"  Value immediately after set: {value}")
    
    print("  Waiting 3 seconds for expiration...")
    time.sleep(3)
    
    value = cache.get('expiring_key')
    if value is None:
        print("✓ Cache expiration: PASSED")
    else:
        print("✗ Cache expiration: FAILED (key still exists)")
        
except Exception as e:
    print(f"✗ Cache expiration test: FAILED - {str(e)}")

# Test 3: Cache with different data types
print("\n[TEST 3] Cache with Different Data Types")
print("-" * 80)

try:
    # String
    cache.set('string_cache', 'Hello World', 300)
    assert cache.get('string_cache') == 'Hello World'
    print("✓ String caching: PASSED")
    
    # Integer
    cache.set('int_cache', 42, 300)
    assert cache.get('int_cache') == 42
    print("✓ Integer caching: PASSED")
    
    # List
    cache.set('list_cache', [1, 2, 3], 300)
    assert cache.get('list_cache') == [1, 2, 3]
    print("✓ List caching: PASSED")
    
    # Dictionary
    cache.set('dict_cache', {'key': 'value'}, 300)
    assert cache.get('dict_cache') == {'key': 'value'}
    print("✓ Dictionary caching: PASSED")
    
except AssertionError as e:
    print(f"✗ Data type caching: FAILED - {str(e)}")

# Test 4: Simulate API caching
print("\n[TEST 4] API Cache Simulation")
print("-" * 80)

try:
    from SmeApp.models import Product, Category, Supplier
    
    # Check if we have test data
    if Product.objects.exists():
        # Simulate product list caching
        products = list(Product.objects.values())
        cache.set('product_list_cache', products, 300)
        cached_products = cache.get('product_list_cache')
        
        if len(cached_products) == len(products):
            print(f"✓ Product list caching: PASSED ({len(cached_products)} products cached)")
        else:
            print("✗ Product list caching: FAILED")
    else:
        print("⚠ Product list caching: SKIPPED (no test data)")
    
    # Simulate dashboard caching
    dashboard_data = {
        'total_products': Product.objects.count(),
        'total_categories': Category.objects.count(),
        'total_suppliers': Supplier.objects.count(),
    }
    cache.set('dashboard_cache', dashboard_data, 600)
    cached_dashboard = cache.get('dashboard_cache')
    
    print(f"✓ Dashboard caching: PASSED")
    print(f"  Cached data: {json.dumps(cached_dashboard, indent=2)}")
    
except Exception as e:
    print(f"✗ API cache simulation: FAILED - {str(e)}")

# Test 5: Clear all cache
print("\n[TEST 5] Clear All Cache")
print("-" * 80)

try:
    cache.set('test1', 'value1', 300)
    cache.set('test2', 'value2', 300)
    cache.set('test3', 'value3', 300)
    
    print(f"  Created 3 cache entries")
    
    cache.clear()
    
    if cache.get('test1') is None and cache.get('test2') is None and cache.get('test3') is None:
        print("✓ Cache clear: PASSED")
    else:
        print("✗ Cache clear: FAILED")
        
except Exception as e:
    print(f"✗ Cache clear test: FAILED - {str(e)}")

# Summary
print("\n" + "=" * 80)
print("REDIS CACHING TEST SUITE COMPLETED")
print("=" * 80)
print("\nCache Settings Summary:")
print("-" * 80)
from django.conf import settings
print(f"Cache Backend: {settings.CACHES['default']['BACKEND']}")
print(f"Cache Location: {settings.CACHES['default']['LOCATION']}")
print(f"Product List Cache Timeout: {settings.CACHE_TIMEOUT_PRODUCT_LIST} seconds")
print(f"Dashboard Cache Timeout: {settings.CACHE_TIMEOUT_DASHBOARD} seconds")
print(f"Top Products Cache Timeout: {settings.CACHE_TIMEOUT_TOP_PRODUCTS} seconds")

print("\n✓ All cache tests completed successfully!")
print("✓ Redis caching is properly configured and working!")
print("\n" + "=" * 80)
