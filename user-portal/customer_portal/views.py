from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse, HttpResponse, FileResponse
from django.urls import reverse
import secrets
import datetime
import os
import sys
import django
import requests
from .models import Customer, AdminLog
from .forms import CustomerForm
from .utils import generate_pdf, send_webhook_notification, log_admin_action
from django.core.paginator import Paginator
import json

def home(request):
    """Home page view"""
    return render(request, 'customer_portal/home.html')

@login_required
def dashboard(request):
    """Dashboard view showing all customers"""
    customers = Customer.objects.filter(created_by=request.user).order_by('-created_at')
    return render(request, 'customer_portal/dashboard.html', {'customers': customers})

@login_required
def add_customer(request):
    """Add new customer view with multi-step form"""
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            # Save customer with current user
            customer = form.save(commit=False)
            customer.created_by = request.user
            customer.save()
            
            # Generate PDF
            pdf_path = generate_pdf(customer)
            if pdf_path:
                customer.pdf_file = os.path.relpath(pdf_path, settings.MEDIA_ROOT)
                customer.save()
            
            # Log the action
            log_admin_action(request.user, 'submission', f"Added customer: {customer.get_full_name()}")
            
            # Send webhook notification
            send_webhook_notification(request.user, 'customer_added', customer)
            
            # Return JSON response for AJAX submission
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'redirect_url': reverse('thank_you', args=[customer.id])
                })
            
            # Redirect to thank you page for regular form submission
            return redirect('thank_you', pk=customer.id)
    else:
        form = CustomerForm()
    
    return render(request, 'customer_portal/add_customer.html', {'form': form})

@login_required
def customer_detail(request, pk):
    """Customer detail view"""
    customer = get_object_or_404(Customer, pk=pk, created_by=request.user)
    return render(request, 'customer_portal/customer_detail.html', {'customer': customer})

@login_required
def edit_customer(request, pk):
    """Edit existing customer view"""
    customer = get_object_or_404(Customer, pk=pk, created_by=request.user)
    
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            # Save the updated customer
            updated_customer = form.save()
            
            # Generate new PDF
            pdf_path = generate_pdf(updated_customer)
            if pdf_path:
                updated_customer.pdf_file = os.path.relpath(pdf_path, settings.MEDIA_ROOT)
                updated_customer.save()
            
            # Log the action
            log_admin_action(request.user, 'edit', f"Edited customer: {updated_customer.get_full_name()}")
            
            # Send webhook notification
            send_webhook_notification(request.user, 'customer_updated', updated_customer)
            
            messages.success(request, f"Customer {updated_customer.get_full_name()} updated successfully!")
            return redirect('customer_detail', pk=updated_customer.id)
    else:
        form = CustomerForm(instance=customer)
    
    return render(request, 'customer_portal/edit_customer.html', {
        'form': form,
        'customer': customer
    })

@login_required
def delete_customer(request, pk):
    """Delete customer view"""
    customer = get_object_or_404(Customer, pk=pk, created_by=request.user)
    
    if request.method == 'POST':
        customer_name = customer.get_full_name()
        
        # Send webhook notification before deleting
        send_webhook_notification(request.user, 'customer_deleted', customer)
        
        # Delete the customer
        customer.delete()
        
        # Log the action
        log_admin_action(request.user, 'delete', f"Deleted customer: {customer_name}")
        
        messages.success(request, f"Customer {customer_name} deleted successfully!")
        return redirect('dashboard')
    
    return render(request, 'customer_portal/delete_customer.html', {'customer': customer})

@login_required
def thank_you(request, pk):
    """Thank you page after adding a customer"""
    customer = get_object_or_404(Customer, pk=pk, created_by=request.user)
    return render(request, 'customer_portal/thank_you.html', {'customer': customer})

@login_required
def download_pdf(request, pk):
    """Download customer PDF"""
    customer = get_object_or_404(Customer, pk=pk, created_by=request.user)
    
    if not customer.pdf_file:
        # Generate PDF if it doesn't exist
        pdf_path = generate_pdf(customer)
        if pdf_path:
            customer.pdf_file = os.path.relpath(pdf_path, settings.MEDIA_ROOT)
            customer.save()
        else:
            messages.error(request, "Failed to generate PDF. Please try again.")
            return redirect('customer_detail', pk=customer.id)
    
    # Get the full path to the PDF file
    pdf_path = os.path.join(settings.MEDIA_ROOT, customer.pdf_file.name)
    
    # Check if the file exists
    if not os.path.exists(pdf_path):
        messages.error(request, "PDF file not found. Generating a new one.")
        
        # Generate a new PDF
        pdf_path = generate_pdf(customer)
        if pdf_path:
            customer.pdf_file = os.path.relpath(pdf_path, settings.MEDIA_ROOT)
            customer.save()
            pdf_path = os.path.join(settings.MEDIA_ROOT, customer.pdf_file.name)
        else:
            messages.error(request, "Failed to generate PDF. Please try again.")
            return redirect('customer_detail', pk=customer.id)
    
    # Log the action
    log_admin_action(request.user, 'download', f"Downloaded PDF for customer: {customer.get_full_name()}")
    
    # Return the PDF file as a response
    return FileResponse(open(pdf_path, 'rb'), as_attachment=True, filename=customer.get_pdf_filename())

@login_required
def send_whatsapp_message(request, pk):
    """Send WhatsApp message to customer"""
    customer = get_object_or_404(Customer, pk=pk, created_by=request.user)
    
    # Log the action
    log_admin_action(request.user, 'whatsapp', f"Sent WhatsApp message to customer: {customer.get_full_name()}")
    
    # Generate WhatsApp URL
    import urllib.parse
    message = customer.get_whatsapp_message()
    encoded_message = urllib.parse.quote(message)
    
    # Format the phone number for WhatsApp
    # Remove any non-numeric characters from the phone
    phone = ''.join(filter(str.isdigit, customer.phone))
    
    # Ensure the phone number has the country code
    # If it doesn't start with '+', assume it needs a country code
    if not phone.startswith('+'):
        # You may need to adjust this based on your country code
        if not phone.startswith('91'):  # India country code
            phone = '91' + phone
    else:
        # If it has a '+', remove it as WhatsApp URL doesn't need it
        phone = phone[1:]
    
    # Create the WhatsApp URL
    whatsapp_url = f"https://wa.me/{phone}?text={encoded_message}"
    
    # Redirect to WhatsApp
    return redirect(whatsapp_url)

def check_env(request):
    """Check environment variables"""
    webhook_uri = getattr(settings, 'WEBHOOK_URI', 'Not set')
    webhook_secret = getattr(settings, 'WEBHOOK_SECRET_KEY', 'Not set')
    
    # Don't show the full secret in production
    secret_status = "Set (hidden)" if webhook_secret else "Not set"
    
    return HttpResponse(f"WEBHOOK_URI: {webhook_uri}<br>WEBHOOK_SECRET_KEY: {secret_status}")

@login_required
@user_passes_test(lambda u: u.is_staff)
def webhook_config(request):
    """Configure and test webhook functionality"""
    # Get current webhook settings
    webhook_uri = getattr(settings, 'WEBHOOK_URI', '')
    webhook_secret = getattr(settings, 'WEBHOOK_SECRET_KEY', '')
    
    if request.method == 'POST':
        if 'test_webhook' in request.POST:
            # Create a dummy customer for testing
            dummy_customer = Customer(
                first_name="Test",
                last_name="Customer",
                email="test@example.com",
                phone="1234567890",
                date_of_birth=datetime.date.today(),
                address="Test Address",
                created_by=request.user,
                gender="other"
            )
            
            # Set created_at and updated_at for the dummy customer
            dummy_customer.created_at = datetime.datetime.now()
            dummy_customer.updated_at = datetime.datetime.now()
            
            # Send test webhook
            try:
                success, message = send_webhook_notification(request.user, 'test_webhook', dummy_customer)
                if success:
                    messages.success(request, "Test webhook sent successfully!")
                else:
                    messages.error(request, f"Failed to send test webhook: {message}")
            except Exception as e:
                messages.error(request, f"Failed to send test webhook: {str(e)}")
        
        elif 'generate_secret' in request.POST:
            # Generate a new secret key
            new_secret = secrets.token_hex(32)
            messages.success(request, f"New webhook secret generated: {new_secret}")
            messages.info(request, "Add this to your .env file as WEBHOOK_SECRET_KEY")
        
        return redirect('webhook_config')
    
    return render(request, 'customer_portal/webhook_config.html', {
        'webhook_uri': webhook_uri,
        'webhook_secret': webhook_secret,
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def test_webhook(request):
    """Test webhook functionality and display detailed results"""
    # Get current webhook settings
    webhook_uri = getattr(settings, 'WEBHOOK_URI', '')
    webhook_secret = getattr(settings, 'WEBHOOK_SECRET_KEY', '')
    
    results = {
        'webhook_uri': webhook_uri,
        'webhook_secret_configured': bool(webhook_secret),
        'test_performed': False,
        'success': False,
        'message': '',
        'details': {}
    }
    
    if request.method == 'POST':
        # Create a dummy customer for testing
        dummy_customer = Customer(
            first_name="Test",
            last_name="Customer",
            email="test@example.com",
            phone="1234567890",
            date_of_birth=datetime.date.today(),
            address="Test Address",
            created_by=request.user,
            gender="other"
        )
        
        # Set created_at and updated_at for the dummy customer
        dummy_customer.created_at = datetime.datetime.now()
        dummy_customer.updated_at = datetime.datetime.now()
        
        # Send test webhook
        results['test_performed'] = True
        success, message = send_webhook_notification(request.user, 'test_webhook', dummy_customer)
        results['success'] = success
        results['message'] = message
        
        # Add environment details for debugging
        results['details'] = {
            'python_version': sys.version,
            'django_version': django.get_version(),
            'requests_version': requests.__version__,
            'webhook_uri_length': len(webhook_uri) if webhook_uri else 0,
            'webhook_secret_length': len(webhook_secret) if webhook_secret else 0,
        }
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse(results)
    
    return render(request, 'customer_portal/test_webhook.html', results)

@login_required
def admin_logs(request):
    """View admin logs"""
    logs = AdminLog.objects.filter(user=request.user).order_by('-timestamp')
    
    # Pagination
    paginator = Paginator(logs, 20)  # Show 20 logs per page
    page_number = request.GET.get('page')
    logs_page = paginator.get_page(page_number)
    
    return render(request, 'customer_portal/admin_logs.html', {'logs': logs_page})

def send_webhook_notification(user, event_type, customer):
    """Send webhook notification to admin"""
    webhook_url = settings.WEBHOOK_URL
    
    if not webhook_url:
        return
    
    payload = {
        'event': event_type,
        'user': user.username,
        'customer_id': customer.id,
        'customer_name': f"{customer.first_name} {customer.last_name}",
        'customer_email': customer.email,
        'timestamp': customer.created_at.isoformat(),
    }
    
    try:
        requests.post(
            webhook_url,
            data=json.dumps(payload),
            headers={'Content-Type': 'application/json'}
        )
    except Exception as e:
        print(f"Webhook notification failed: {e}")

