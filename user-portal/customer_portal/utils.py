from django.conf import settings
from django.template.loader import get_template
from .models import AdminLog
import os
from xhtml2pdf import pisa
from io import BytesIO
import json
import hmac
import hashlib
import requests
import logging
import datetime
import traceback

logger = logging.getLogger(__name__)

def log_admin_action(user, action, details=None):
    """Create an admin log entry"""
    AdminLog.objects.create(
        user=user,
        action=action,
        details=details
    )

def generate_pdf(customer):
    """Generate PDF with customer details"""
    template = get_template('customer_portal/pdf_template.html')
    context = {
        'customer': customer,
        'company_name': settings.COMPANY_NAME,
    }
    html = template.render(context)
    
    # Create PDF directory if it doesn't exist
    pdf_dir = settings.PDF_ROOT
    os.makedirs(pdf_dir, exist_ok=True)
    
    # Generate PDF filename
    pdf_filename = customer.get_pdf_filename()
    pdf_path = os.path.join(pdf_dir, pdf_filename)
    
    # Generate PDF
    with open(pdf_path, 'wb') as pdf_file:
        pisa_status = pisa.CreatePDF(
            html,
            dest=pdf_file
        )
    
    # Return path if successful
    if pisa_status.err:
        return None
    
    return pdf_path

def send_webhook_notification(user, event_type, customer):
    """
    Send webhook notification when a customer is added, updated, or deleted
    
    Args:
        user: The user who performed the action
        event_type: Type of event (customer_added, customer_updated, customer_deleted)
        customer: The customer object
    
    Returns:
        tuple: (success, message) where success is a boolean and message is a string
    """
    webhook_uri = getattr(settings, 'WEBHOOK_URI', '')
    webhook_secret = getattr(settings, 'WEBHOOK_SECRET_KEY', '')
    
    # Debug information
    logger.info(f"Webhook URI: {webhook_uri}")
    logger.info(f"Webhook Secret configured: {'Yes' if webhook_secret else 'No'}")
    
    # If webhook URI is not configured, skip
    if not webhook_uri:
        logger.warning("Webhook URI not configured, skipping notification")
        return False, "Webhook URI not configured"
    
    try:
        # Prepare payload
        payload = {
            'event_type': event_type,
            'timestamp': customer.updated_at.isoformat() if hasattr(customer, 'updated_at') else None,
            'user': user.username,
            'customer': {
                'id': customer.id if hasattr(customer, 'id') else 0,
                'name': customer.get_full_name() if hasattr(customer, 'get_full_name') else "Test Customer",
                'email': customer.email,
                'phone': customer.phone,
                'created_at': customer.created_at.isoformat() if hasattr(customer, 'created_at') else None
            }
        }
        
        # Convert payload to JSON
        payload_json = json.dumps(payload)
        logger.debug(f"Webhook payload: {payload_json}")
        
        # Generate signature if secret key is provided
        headers = {'Content-Type': 'application/json'}
        if webhook_secret:
            signature = hmac.new(
                webhook_secret.encode(),
                payload_json.encode(),
                hashlib.sha256
            ).hexdigest()
            headers['X-Webhook-Signature'] = signature
            logger.debug(f"Generated signature: {signature}")
        
        # Send the webhook
        logger.info(f"Sending webhook to {webhook_uri}")
        response = requests.post(
            webhook_uri,
            data=payload_json,
            headers=headers,
            timeout=10  # Increased timeout
        )
        
        # Log response details
        logger.info(f"Webhook response status: {response.status_code}")
        logger.debug(f"Webhook response body: {response.text}")
        
        if response.status_code >= 200 and response.status_code < 300:
            logger.info(f"Webhook sent successfully: {event_type}")
            return True, "Webhook sent successfully"
        else:
            error_msg = f"Webhook failed with status {response.status_code}: {response.text}"
            logger.error(error_msg)
            return False, error_msg
            
    except requests.exceptions.ConnectionError as e:
        error_msg = f"Connection error sending webhook: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        return False, error_msg
    except requests.exceptions.Timeout as e:
        error_msg = f"Timeout sending webhook: {str(e)}"
        logger.error(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"Error sending webhook: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        return False, error_msg

def send_form_submission_webhook(user, customer):
    """
    Send webhook notification when a customer form is successfully submitted
    
    Args:
        user: The user who submitted the form
        customer: The customer object that was created
    """
    # Check if webhook is enabled and URL is configured
    webhook_enabled = getattr(settings, 'WEBHOOK_ENABLED', False)
    webhook_url = getattr(settings, 'WEBHOOK_URL', None)
    
    if not webhook_enabled or not webhook_url:
        logger.info("Webhooks are disabled or webhook URL is not configured")
        return False
    
    # Prepare customer data for the webhook payload
    customer_data = {
        'id': customer.id,
        'name': customer.get_full_name(),
        'email': customer.email,
        'phone': customer.phone,
        'gender': customer.get_gender_display(),
        'date_of_birth': str(customer.date_of_birth),
        'address': customer.address,
        'created_at': str(customer.created_at)
    }
    
    # Prepare payload
    payload = {
        'event': 'form_submission',
        'user': user.username,
        'timestamp': datetime.datetime.now().isoformat(),
        'customer': customer_data,
        'message': f"New customer form submitted by {user.username}: {customer.get_full_name()}"
    }
    
    # Convert payload to JSON
    json_payload = json.dumps(payload)
    
    # Create signature for verification if secret is available
    webhook_secret = getattr(settings, 'WEBHOOK_SECRET', '')
    if webhook_secret:
        signature = hmac.new(
            webhook_secret.encode('utf-8'),
            json_payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # Set headers with signature
        headers = {
            'Content-Type': 'application/json',
            'X-Webhook-Signature': signature
        }
    else:
        # Set basic headers without signature
        headers = {
            'Content-Type': 'application/json'
        }
    
    try:
        # Send webhook request
        response = requests.post(
            webhook_url,
            data=json_payload,
            headers=headers,
            timeout=5  # 5 second timeout
        )
        
        # Check if request was successful
        if response.status_code >= 200 and response.status_code < 300:
            logger.info(f"Form submission webhook sent successfully for customer: {customer.get_full_name()}")
            return True
        else:
            logger.error(f"Form submission webhook failed with status code {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Error sending form submission webhook: {str(e)}")
        return False
