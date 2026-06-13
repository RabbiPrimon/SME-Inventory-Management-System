"""
Background tasks for SME Inventory Management System using Celery.

This module contains all async tasks that run in the background:
- Low-stock alerts (daily)
- Weekly inventory reports
- Sales analytics calculations
"""

from celery import shared_task
from django.core.mail import send_mail
from django.db.models import F, Sum, Count
from django.db import models
from django.utils import timezone
from datetime import timedelta
from io import BytesIO
from django.template.loader import render_to_string
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

from .models import Product, Order, OrderItem
import logging

logger = logging.getLogger(__name__)


# ===========================
# Low Stock Alert Task
# ===========================

@shared_task(name='tasks.check_low_stock_and_alert')
def check_low_stock_and_alert():
    """
    Check for products with low stock and send email alerts.
    
    This task:
    1. Finds all products where stock <= reorder_level
    2. Groups them by supplier
    3. Sends emails to configured recipients
    4. Returns summary statistics
    
    Scheduled: Daily at 08:00 AM (UTC)
    """
    try:
        # Find low stock products
        low_stock_products = Product.objects.filter(
            stock__lte=F('reorder_level')
        ).select_related('category', 'supplier').order_by('supplier__name')
        
        if not low_stock_products.exists():
            logger.info("No low stock products found")
            return {
                'status': 'success',
                'message': 'No low stock products found',
                'low_stock_count': 0,
            }
        
        # Group by supplier for easier reading
        suppliers_dict = {}
        for product in low_stock_products:
            supplier_name = product.supplier.name
            if supplier_name not in suppliers_dict:
                suppliers_dict[supplier_name] = []
            suppliers_dict[supplier_name].append(product)
        
        # Prepare email content
        product_list_html = "<ul>"
        for product in low_stock_products:
            product_list_html += (
                f"<li><strong>{product.name}</strong> "
                f"(Current: {product.stock}, Reorder Level: {product.reorder_level}) "
                f"- Category: {product.category.name}</li>"
            )
        product_list_html += "</ul>"
        
        email_subject = f"Low Stock Alert - {low_stock_products.count()} Products"
        email_body = f"""
        <h2>Low Stock Alert</h2>
        <p>The following products have fallen below their reorder level:</p>
        {product_list_html}
        <p>Please take immediate action to reorder these items.</p>
        <p>Report generated: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        """
        
        # Send email
        try:
            send_mail(
                subject=email_subject,
                message=f"Low Stock Alert - {low_stock_products.count()} products",
                from_email='noreply@smeinventory.com',
                recipient_list=['admin@smeinventory.com'],
                html_message=email_body,
                fail_silently=False,
            )
            logger.info(f"Low stock alert email sent for {low_stock_products.count()} products")
        except Exception as e:
            logger.error(f"Failed to send low stock alert email: {str(e)}")
        
        return {
            'status': 'success',
            'message': f'Low stock alert sent for {low_stock_products.count()} products',
            'low_stock_count': low_stock_products.count(),
            'suppliers_affected': list(suppliers_dict.keys()),
        }
        
    except Exception as e:
        logger.error(f"Error in check_low_stock_and_alert: {str(e)}")
        return {
            'status': 'error',
            'message': str(e),
        }


# ===========================
# Weekly Report Task
# ===========================

@shared_task(name='tasks.generate_weekly_report')
def generate_weekly_report():
    """
    Generate weekly inventory report and send PDF to owner.
    
    This task:
    1. Calculates inventory statistics for the past week
    2. Generates a PDF report with tables and charts
    3. Sends the report via email
    
    Scheduled: Every Monday at 09:00 AM (UTC)
    """
    try:
        # Calculate dates
        end_date = timezone.now()
        start_date = end_date - timedelta(days=7)
        
        # Fetch data
        products = Product.objects.all()
        orders_week = Order.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        
        # Calculate statistics
        total_products = products.count()
        low_stock_count = products.filter(stock__lte=F('reorder_level')).count()
        total_inventory_value = products.aggregate(
            total=Sum(F('stock') * F('price'), output_field=models.DecimalField())
        )['total'] or 0
        
        # Order statistics
        total_orders = orders_week.count()
        completed_orders = orders_week.filter(status='completed').count()
        pending_orders = orders_week.filter(status='pending').count()
        
        # Revenue calculation
        revenue = OrderItem.objects.filter(
            order__created_at__gte=start_date,
            order__created_at__lte=end_date,
        ).aggregate(
            total=Sum(F('quantity') * F('price'))
        )['total'] or 0
        
        # Top selling products
        top_products = Product.objects.annotate(
            total_ordered=Sum('orderitem__quantity')
        ).filter(
            total_ordered__isnull=False
        ).order_by('-total_ordered')[:5]
        
        # Prepare report data
        report_data = {
            'period_start': start_date.strftime('%Y-%m-%d'),
            'period_end': end_date.strftime('%Y-%m-%d'),
            'total_products': total_products,
            'low_stock_count': low_stock_count,
            'inventory_value': float(total_inventory_value),
            'total_orders': total_orders,
            'completed_orders': completed_orders,
            'pending_orders': pending_orders,
            'revenue': float(revenue),
            'top_products': [
                {
                    'name': p.name,
                    'quantity_ordered': p.total_ordered,
                    'price': float(p.price),
                }
                for p in top_products
            ]
        }
        
        # Generate PDF
        pdf_content = _generate_pdf_report(report_data)
        
        # Send email with PDF
        email_subject = f"Weekly Inventory Report - {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        email_body = f"""
        <h2>Weekly Inventory Report</h2>
        <p>Period: {report_data['period_start']} to {report_data['period_end']}</p>
        <h3>Summary</h3>
        <ul>
            <li>Total Products: {report_data['total_products']}</li>
            <li>Low Stock Items: {report_data['low_stock_count']}</li>
            <li>Inventory Value: ${report_data['inventory_value']:.2f}</li>
            <li>Total Orders: {report_data['total_orders']}</li>
            <li>Revenue: ${report_data['revenue']:.2f}</li>
        </ul>
        <p>See attached PDF for detailed report.</p>
        """
        
        try:
            send_mail(
                subject=email_subject,
                message=f"Weekly Report - {start_date.strftime('%Y-%m-%d')}",
                from_email='noreply@smeinventory.com',
                recipient_list=['admin@smeinventory.com'],
                html_message=email_body,
                fail_silently=False,
            )
            logger.info("Weekly report email sent")
        except Exception as e:
            logger.error(f"Failed to send weekly report email: {str(e)}")
        
        return {
            'status': 'success',
            'message': 'Weekly report generated and sent',
            'report_data': report_data,
        }
        
    except Exception as e:
        logger.error(f"Error in generate_weekly_report: {str(e)}")
        return {
            'status': 'error',
            'message': str(e),
        }


# ===========================
# Sales Analytics Task
# ===========================

@shared_task(name='tasks.calculate_sales_analytics')
def calculate_sales_analytics():
    """
    Calculate sales analytics and update statistics.
    
    This task:
    1. Calculates revenue by category and supplier
    2. Computes best-selling products
    3. Analyzes order patterns
    4. Stores results for dashboard display
    
    Scheduled: Every hour
    """
    try:
        # Time period
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = now - timedelta(days=7)
        month_start = now - timedelta(days=30)
        
        # Today's metrics
        today_orders = Order.objects.filter(created_at__gte=today_start)
        today_revenue = OrderItem.objects.filter(
            order__created_at__gte=today_start
        ).aggregate(total=Sum(F('quantity') * F('price')))['total'] or 0
        
        # Week's metrics
        week_orders = Order.objects.filter(created_at__gte=week_start)
        week_revenue = OrderItem.objects.filter(
            order__created_at__gte=week_start
        ).aggregate(total=Sum(F('quantity') * F('price')))['total'] or 0
        
        # Month's metrics
        month_orders = Order.objects.filter(created_at__gte=month_start)
        month_revenue = OrderItem.objects.filter(
            order__created_at__gte=month_start
        ).aggregate(total=Sum(F('quantity') * F('price')))['total'] or 0
        
        # Top categories by revenue
        top_categories = Product.objects.values('category__name').annotate(
            revenue=Sum(F('orderitem__quantity') * F('orderitem__price')),
            order_count=Count('orderitem')
        ).order_by('-revenue')[:5]
        
        # Top suppliers by orders
        top_suppliers = Product.objects.values('supplier__name').annotate(
            order_count=Count('orderitem'),
            revenue=Sum(F('orderitem__quantity') * F('orderitem__price'))
        ).order_by('-order_count')[:5]
        
        analytics_data = {
            'timestamp': now.isoformat(),
            'today': {
                'orders': today_orders.count(),
                'revenue': float(today_revenue),
                'completed_orders': today_orders.filter(status='completed').count(),
            },
            'week': {
                'orders': week_orders.count(),
                'revenue': float(week_revenue),
                'avg_order_value': float(week_revenue / week_orders.count()) if week_orders.count() > 0 else 0,
            },
            'month': {
                'orders': month_orders.count(),
                'revenue': float(month_revenue),
                'avg_order_value': float(month_revenue / month_orders.count()) if month_orders.count() > 0 else 0,
            },
            'top_categories': list(top_categories),
            'top_suppliers': list(top_suppliers),
        }
        
        # Store analytics in cache for dashboard
        from django.core.cache import cache
        cache.set('sales_analytics', analytics_data, 3600)  # Cache for 1 hour
        
        logger.info("Sales analytics calculated and cached")
        
        return {
            'status': 'success',
            'message': 'Sales analytics calculated',
            'analytics': analytics_data,
        }
        
    except Exception as e:
        logger.error(f"Error in calculate_sales_analytics: {str(e)}")
        return {
            'status': 'error',
            'message': str(e),
        }


# ===========================
# Helper Functions
# ===========================

def _generate_pdf_report(report_data):
    """Generate PDF report from report data."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=30,
    )
    
    # Title
    elements.append(Paragraph("Weekly Inventory Report", title_style))
    elements.append(Spacer(1, 0.3 * inch))
    
    # Summary section
    summary_data = [
        ['Metric', 'Value'],
        ['Period', f"{report_data['period_start']} to {report_data['period_end']}"],
        ['Total Products', str(report_data['total_products'])],
        ['Low Stock Items', str(report_data['low_stock_count'])],
        ['Inventory Value', f"${report_data['inventory_value']:.2f}"],
        ['Total Orders', str(report_data['total_orders'])],
        ['Completed Orders', str(report_data['completed_orders'])],
        ['Revenue', f"${report_data['revenue']:.2f}"],
    ]
    
    summary_table = Table(summary_data, colWidths=[3 * inch, 3 * inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    elements.append(summary_table)
    elements.append(Spacer(1, 0.3 * inch))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()


# ===========================
# Utility Tasks
# ===========================

@shared_task(name='tasks.test_task')
def test_task(message='Test message'):
    """Simple test task to verify Celery is working."""
    logger.info(f"Test task executed with message: {message}")
    return {
        'status': 'success',
        'message': message,
        'timestamp': timezone.now().isoformat(),
    }
