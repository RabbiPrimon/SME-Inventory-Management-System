# Celery Setup Guide for SME Inventory Management System

This guide explains how to set up Celery for background task processing in the SME Inventory Management System.

## What is Celery?

Celery is an asynchronous task queue/job queue based on distributed message passing. It is focused on real-time operation but supports scheduling as well. The execution units, called tasks, are executed concurrently on one or more worker nodes.

### Key Benefits

1. **Non-blocking operations** - Long-running tasks don't slow down API responses
2. **Scheduled tasks** - Run tasks at specific times or intervals
3. **Retries** - Automatically retry failed tasks
4. **Monitoring** - Track task execution and results
5. **Scalability** - Distribute tasks across multiple workers

## Background Tasks Overview

The system includes three main background tasks:

### 1. Low-Stock Alert (Daily)

**What it does:**
- Checks all products where stock ≤ reorder_level
- Groups products by supplier
- Sends email alerts to admin

**Schedule:** Daily at 08:00 AM UTC

**Example email:**
```
Subject: Low Stock Alert - 5 Products

The following products have fallen below their reorder level:
- Wireless Mouse (Current: 8, Reorder Level: 25)
- USB Cable (Current: 5, Reorder Level: 10)
...
```

### 2. Weekly Report (Every Monday)

**What it does:**
- Calculates inventory statistics for the past 7 days
- Generates a PDF report with:
  - Total products and inventory value
  - Order statistics
  - Revenue calculations
  - Top-selling products
- Sends report via email

**Schedule:** Every Monday at 09:00 AM UTC

### 3. Sales Analytics (Every Hour)

**What it does:**
- Calculates revenue metrics
- Analyzes order patterns
- Identifies top categories and suppliers
- Stores results in cache for dashboard display

**Schedule:** Every hour

**Metrics calculated:**
- Today's orders and revenue
- Week's orders and average order value
- Month's orders and average order value
- Top 5 categories by revenue
- Top 5 suppliers by order count

## Prerequisites

Before setting up Celery, ensure you have:

1. **Redis Server** installed and running
   - See [REDIS_SETUP.md](REDIS_SETUP.md) for installation instructions

2. **Python packages** installed
   ```bash
   pip install -r requirements.txt
   ```

3. **Django migrations** applied
   ```bash
   python manage.py migrate
   ```

## Installation

### Step 1: Install Dependencies

All required packages are in `requirements.txt`:

```bash
pip install -r requirements.txt
```

This installs:
- celery >= 5.3.0
- django-celery-beat >= 2.5.0
- django-celery-results >= 2.5.0
- email-validator >= 2.0.0
- reportlab >= 4.0.0

### Step 2: Verify Configuration

The system is already configured in `SmeProject/settings.py`:

```python
# Celery Configuration
CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60

# Email Configuration (for notifications)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Development
# For production, use SMTP:
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'your-email@gmail.com'
# EMAIL_HOST_PASSWORD = 'your-app-password'
```

### Step 3: Apply Django Celery Beat Migrations

```bash
python manage.py migrate django_celery_beat
python manage.py migrate django_celery_results
```

Expected output:
```
Running migrations:
  Applying django_celery_beat.0001_initial... OK
  Applying django_celery_results.0001_initial... OK
```

### Step 4: Verify Setup

Run the test script:

```bash
python test_celery.py
```

Expected output:
```
================================================================================
CELERY TEST SUITE
================================================================================

[TEST 1] Celery Configuration
✓ Celery app: <Celery SmeProject at 0x...>
✓ Broker: redis://127.0.0.1:6379/0
✓ Result Backend: redis://127.0.0.1:6379/0
✓ Celery configuration: PASSED

[TEST 2] Simple Task Test
✓ Simple task execution: PASSED

[TEST 3] Low Stock Alert Task
✓ Low stock alert task: REGISTERED
✓ Scheduled: Daily at 08:00 AM (UTC)

...
```

## Running Celery

### Prerequisites

1. **Start Redis Server** (in one terminal):
   ```bash
   redis-server
   # or
   redis-cli
   ```

2. **Verify Redis is running**:
   ```bash
   redis-cli ping
   # Should return: PONG
   ```

### Option 1: Run Worker Only

Start the Celery worker to execute tasks:

```bash
celery -A SmeProject worker -l info
```

**Output:**
```
 ---------- celery@COMPUTER v5.6.3 (emi)
--- ***** -----
-- ******* ----
- *** --- * ---
- ** ---------- [config]
- ** ----------
- ** ---------- .broker: redis://127.0.0.1:6379/0
- ** ---------- .app: __main__:0x...
- ** ---------- .concurrency: 4 (prefork)
- *** --- * --- [queues]
--- ******* ---- .celery: exchange:celery(direct) binding:celery
 ---------- [tasks]

[tasks]
  . tasks.check_low_stock_and_alert
  . tasks.calculate_sales_analytics
  . tasks.generate_weekly_report
  . tasks.test_task

[2026-06-13 10:30:00,000: INFO/MainProcess] celery@COMPUTER ready.
```

### Option 2: Run Celery Beat Scheduler Only

Start the Celery Beat scheduler to trigger periodic tasks:

```bash
celery -A SmeProject beat -l info
```

**Output:**
```
celery beat v5.6.3 (emi) is starting.
__    -    ... __   -        _
LocalTime -> 2026-06-13 10:30:00
Configuration ->
    . scheduler -> django_celery_beat.schedulers:DatabaseScheduler
    . db -> django_db
    . Enable UTC -> True

[tasks]
  . tasks.check_low_stock_and_alert (daily at 08:00 UTC)
  . tasks.calculate_sales_analytics (every 1 hour)
  . tasks.generate_weekly_report (monday at 09:00 UTC)
```

### Option 3: Run Worker + Beat Together

Run both in one process:

```bash
celery -A SmeProject worker -B -l info
```

This combines both worker and beat in a single process. **Recommended for development only**. For production, run them separately.

### Option 4: Using a Process Manager

For production, use a process manager like Supervisor or systemd:

**supervisor.conf:**
```ini
[program:celery_worker]
command=celery -A SmeProject worker -l info
directory=/path/to/SmeProject
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/celery_worker.log

[program:celery_beat]
command=celery -A SmeProject beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
directory=/path/to/SmeProject
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/celery_beat.log
```

## Managing Scheduled Tasks

### View Scheduled Tasks

```bash
python manage.py shell
```

Then in the Python shell:

```python
from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule

# View all periodic tasks
PeriodicTask.objects.all()

# View specific task
PeriodicTask.objects.get(name='check_low_stock_and_alert')
```

### Add New Task Programmatically

```python
from django_celery_beat.models import PeriodicTask, CrontabSchedule

# Create a cron schedule (every day at 8 AM UTC)
schedule, created = CrontabSchedule.objects.get_or_create(
    hour=8,
    minute=0,
    timezone='UTC'
)

# Create periodic task
PeriodicTask.objects.get_or_create(
    name='check_low_stock_and_alert',
    defaults={
        'task': 'tasks.check_low_stock_and_alert',
        'crontab': schedule,
        'enabled': True,
    }
)
```

### Disable/Enable Tasks

```python
task = PeriodicTask.objects.get(name='check_low_stock_and_alert')
task.enabled = False  # Disable
task.save()
```

### Delete Tasks

```python
PeriodicTask.objects.get(name='check_low_stock_and_alert').delete()
```

## Monitoring Tasks

### View Task Results

```bash
celery -A SmeProject events
```

This opens the Celery Events monitor showing real-time task execution.

### Check Task Status

```python
from celery.result import AsyncResult

# Get task result by ID
task_id = 'abc123'
result = AsyncResult(task_id, app=current_app)
print(result.status)  # 'PENDING', 'STARTED', 'SUCCESS', 'FAILURE'
print(result.result)  # Task result or exception
```

### View Task Logs

```bash
celery -A SmeProject worker -l debug
```

Increase verbosity with `-l debug` for more detailed logs.

## Testing Tasks

### Run Test Task Manually

```python
from SmeApp.tasks import test_task

# Execute immediately (synchronous)
result = test_task('Hello World')
print(result)

# Queue for worker (asynchronous)
task = test_task.delay('Hello World')
print(task.id)
print(task.status)
```

### Test Low Stock Alert

```python
from SmeApp.tasks import check_low_stock_and_alert

# Execute immediately
result = check_low_stock_and_alert()
print(result)
```

### Test Weekly Report

```python
from SmeApp.tasks import generate_weekly_report

# Execute immediately
result = generate_weekly_report()
print(result['message'])
```

## Email Configuration

### Development Mode (Console Output)

Default configuration outputs emails to console:

```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

Emails will appear in the Celery worker console.

### Production Mode (Gmail SMTP)

Update `SmeProject/settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-specific-password'
DEFAULT_FROM_EMAIL = 'noreply@smeinventory.com'
```

**Getting Gmail App Password:**

1. Enable 2-Factor Authentication on your Gmail account
2. Go to https://myaccount.google.com/apppasswords
3. Select "Mail" and "Windows Computer"
4. Google will generate a 16-character password
5. Use this password in `EMAIL_HOST_PASSWORD`

### Production Mode (Custom SMTP)

```python
EMAIL_HOST = 'mail.yourdomain.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'noreply@yourdomain.com'
EMAIL_HOST_PASSWORD = 'your-password'
```

## Troubleshooting

### Issue: "Connection refused" Redis

**Error:** `ConnectionError: Error 111 connecting to 127.0.0.1:6379`

**Solution:**
1. Ensure Redis is running: `redis-cli ping`
2. If not running, start Redis: `redis-server`
3. Check Redis connection in settings

### Issue: "No module named 'celery'"

**Error:** `ModuleNotFoundError: No module named 'celery'`

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: "No module named 'django_celery_beat'"

**Error:** `ModuleNotFoundError: No module named 'django_celery_beat'`

**Solution:**
```bash
pip install django-celery-beat django-celery-results
```

### Issue: Tasks not running

**Cause:** Worker is not running

**Solution:**
1. Start the Celery worker: `celery -A SmeProject worker -l info`
2. Check if tasks are queued in Redis
3. Verify task is registered: `celery -A SmeProject inspect active`

### Issue: Tasks not executing on schedule

**Cause:** Celery Beat is not running

**Solution:**
1. Start Celery Beat: `celery -A SmeProject beat -l info`
2. Verify scheduled tasks: `python manage.py shell`
   ```python
   from django_celery_beat.models import PeriodicTask
   PeriodicTask.objects.all()
   ```
3. Check if task is enabled: `task.enabled = True`

### Issue: Email not being sent

**Cause:** Email backend not configured

**Solution:**
1. Check `EMAIL_BACKEND` in settings
2. Test email manually:
   ```python
   from django.core.mail import send_mail
   send_mail('Test', 'Test message', 'from@example.com', ['to@example.com'])
   ```
3. Check SMTP credentials
4. Verify firewall allows SMTP port (587 for Gmail)

### Issue: "MISCONF Redis is configured to save RDB snapshots"

**Warning:** This is informational

**Solution:** Suppress by running:
```bash
redis-server --appendonly no
```

## Performance Tips

1. **Use multiple workers for production:**
   ```bash
   celery -A SmeProject worker -l info -c 4  # 4 concurrent processes
   ```

2. **Monitor task execution time:**
   - Set `CELERY_TASK_TIME_LIMIT` for maximum execution time
   - Log long-running tasks

3. **Use task rate limiting:**
   ```python
   @shared_task(rate_limit='100/m')  # 100 tasks per minute
   def my_task():
       pass
   ```

4. **Implement task retries:**
   ```python
   @shared_task(bind=True, max_retries=3)
   def my_task(self):
       try:
           # task code
       except Exception as exc:
           raise self.retry(exc=exc, countdown=60)
   ```

## Production Deployment Checklist

- [ ] Redis configured and running
- [ ] Celery worker running (auto-restart on failure)
- [ ] Celery Beat running (auto-restart on failure)
- [ ] Email backend configured (SMTP)
- [ ] Task timeouts configured
- [ ] Task retries implemented
- [ ] Logging configured
- [ ] Monitoring set up
- [ ] Database backups scheduled
- [ ] Error alerting configured

## Further Reading

- [Celery Documentation](https://docs.celeryproject.io/)
- [Django Celery Documentation](https://docs.celeryproject.io/en/stable/django/)
- [Celery Beat Documentation](https://docs.celeryproject.io/en/stable/userguide/periodic-tasks.html)
- [django-celery-beat GitHub](https://github.com/celery/django-celery-beat)
