from django.urls import path
from . import views

urlpatterns = [
    # Your existing URL patterns
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('customer/add/', views.add_customer, name='add_customer'),
    path('customer/<int:pk>/', views.customer_detail, name='customer_detail'),
    path('customer/<int:pk>/edit/', views.edit_customer, name='edit_customer'),
    path('customer/<int:pk>/delete/', views.delete_customer, name='delete_customer'),
    path('customer/<int:pk>/thank-you/', views.thank_you, name='thank_you'),
    path('customer/<int:pk>/pdf/', views.download_pdf, name='download_pdf'),
    
    # Add this new URL pattern for WhatsApp
    path('customer/<int:pk>/whatsapp/', views.send_whatsapp_message, name='send_whatsapp'),
    
    # Other URL patterns
    path('webhook/config/', views.webhook_config, name='webhook_config'),
    path('webhook/test/', views.test_webhook, name='test_webhook'),
    path('logs/', views.admin_logs, name='admin_logs'),
    path('check-env/', views.check_env, name='check_env'),

]

