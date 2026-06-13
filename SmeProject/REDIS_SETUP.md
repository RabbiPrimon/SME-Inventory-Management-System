# Redis Setup Guide for Windows

This guide explains how to set up Redis for the SME Inventory Management System on Windows.

## What is Redis?

Redis is an in-memory data store that works as a cache for your application. It dramatically improves performance by storing frequently accessed data in memory instead of querying the database repeatedly.

## Installation Methods

### Method 1: Windows Subsystem for Linux (WSL) - Recommended

This is the easiest method for Windows 10/11 users.

1. **Enable WSL2**:
   ```powershell
   wsl --install
   ```

2. **Install Redis in WSL**:
   ```bash
   # Open WSL terminal
   wsl
   
   # Update package manager
   sudo apt-get update
   
   # Install Redis
   sudo apt-get install redis-server
   ```

3. **Start Redis**:
   ```bash
   redis-server
   ```

### Method 2: Memurai Redis for Windows

Memurai maintains an actively-updated Redis build for Windows.

1. **Download Memurai**: https://www.memurai.com/
2. **Run installer**
3. **Start Redis** (automatically as service or manually):
   ```powershell
   redis-server
   ```

### Method 3: Docker

If you have Docker installed:

```bash
# Pull and run Redis image
docker run -d -p 6379:6379 --name redis redis:latest

# Start the container (if stopped)
docker start redis
```

### Method 4: GitHub Archive (Legacy)

Download pre-built Redis: https://github.com/microsoftarchive/redis/releases

## Verify Redis Installation

Test Redis connection:

```bash
# Install redis-cli
pip install redis

# Test connection with Python
python
>>> import redis
>>> r = redis.Redis(host='localhost', port=6379, db=0)
>>> r.ping()
True
```

Or use command line:

```bash
redis-cli ping
# Should return: PONG
```

## Running the Development Server with Redis

1. **Start Redis server** (in separate terminal):
   ```bash
   # WSL
   redis-server
   
   # Or Windows service (Memurai)
   redis-server.exe
   
   # Or Docker
   docker start redis
   ```

2. **Verify Redis is running**:
   ```bash
   redis-cli ping
   # Returns: PONG
   ```

3. **Start Django development server**:
   ```bash
   cd e:\Projects\SME-Inventory-Management-System\SmeProject
   python manage.py runserver
   ```

## Testing Redis Cache

Run the included test script:

```bash
python test_cache.py
```

Expected output:
```
[TEST 1] Basic Cache Operations
✓ Cache SET operation: PASSED
✓ Cache GET operation: PASSED
✓ Cache DELETE operation: PASSED

[TEST 2] Cache Expiration
✓ Cache expiration: PASSED

[TEST 3] Cache with Different Data Types
✓ String caching: PASSED
✓ Integer caching: PASSED
✓ List caching: PASSED
✓ Dictionary caching: PASSED

...

✓ All cache tests completed successfully!
✓ Redis caching is properly configured and working!
```

## Troubleshooting

### Error: "Connection refused"

**Cause**: Redis server is not running

**Solution**:
1. Ensure Redis is installed
2. Start Redis server
3. Verify with: `redis-cli ping`

### Error: "ModuleNotFoundError: No module named 'redis'"

**Cause**: Redis Python package not installed

**Solution**:
```bash
pip install -r requirements.txt
```

### Error: "MISCONF Redis is configured to save RDB snapshots"

This is a warning, not an error. Redis is working fine. To suppress:
- If using WSL: run `redis-server --appendonly no`
- If using Memurai: modify redis.conf

### Connection hangs or times out

**Solution**:
1. Ensure Redis is running: `redis-cli ping`
2. Check Redis port is 6379 (or update `SmeProject/settings.py`)
3. Verify firewall allows localhost:6379

## Cache Configuration

Current settings in `SmeProject/settings.py`:

```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            'IGNORE_EXCEPTIONS': True,  # Fallback to database if Redis unavailable
        }
    }
}

# Cache timeouts
CACHE_TIMEOUT_PRODUCT_LIST = 300  # 5 minutes
CACHE_TIMEOUT_DASHBOARD = 600     # 10 minutes
CACHE_TIMEOUT_TOP_PRODUCTS = 3600 # 1 hour
```

### Customizing Cache Settings

Edit `SmeProject/settings.py`:

```python
# Change Redis location
'LOCATION': 'redis://your-redis-server:6379/1',

# Change timeouts (in seconds)
CACHE_TIMEOUT_PRODUCT_LIST = 600  # 10 minutes
CACHE_TIMEOUT_DASHBOARD = 1800    # 30 minutes
CACHE_TIMEOUT_TOP_PRODUCTS = 7200 # 2 hours
```

## Cache Disabled Fallback

If Redis is unavailable, caching is automatically disabled (`IGNORE_EXCEPTIONS': True`).

The application will:
1. Try to use Redis cache
2. If Redis is down, query the database directly
3. Gracefully handle cache misses

**Production Note**: Monitor Redis availability. Use `IGNORE_EXCEPTIONS': False` in production to catch cache issues.

## Monitoring Redis

### Check Redis Status

```bash
redis-cli INFO
```

### View cached keys

```bash
redis-cli KEYS "*"
```

### Clear all cache

```bash
redis-cli FLUSHDB
```

Or in Python:

```python
from django.core.cache import cache
cache.clear()
```

### Monitor real-time commands

```bash
redis-cli MONITOR
```

Then make API requests to see cache operations in real-time.

## Performance Tips

1. **Use appropriate cache timeouts**:
   - Dashboard: 10 minutes (frequently accessed)
   - Product list: 5 minutes (moderate changes)
   - Top products: 1 hour (rarely changes)

2. **Monitor cache hit rate**:
   ```bash
   redis-cli INFO stats
   ```

3. **Use cache versioning** for cache invalidation:
   ```python
   cache.set('product_list_v1', data, 300)
   ```

4. **Separate cache database**:
   - Default: database 0
   - Current: database 1 (configured in `LOCATION`)

## Production Deployment

For production:

1. **Use dedicated Redis server** (not local)
2. **Enable Redis persistence**:
   ```
   appendonly yes
   ```

3. **Set strong authentication**:
   ```python
   'LOCATION': 'redis://:password@redis.example.com:6379/1',
   ```

4. **Use Redis Sentinel** for high availability
5. **Monitor with** `redis-cli INFO` or tools like Redis Commander
6. **Regular backups** of Redis data

## Further Reading

- Redis Documentation: https://redis.io/documentation
- django-redis: https://github.com/jazzband/django-redis
- Redis Windows Setup: https://docs.microsoft.com/en-us/windows/wsl/tutorials/wsl-database#install-redis
