from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import os
from datetime import date
import urllib.parse

class Customer(models.Model):
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    )
    
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customers')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    pdf_file = models.FileField(upload_to='pdfs/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_full_name(self):
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"
    
    def get_age(self):
        today = date.today()
        born = self.date_of_birth
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
    
    def get_pdf_filename(self):
        return f"customer_{self.id}_{self.first_name}_{self.last_name}.pdf"
    
    def get_whatsapp_message(self):
        from django.conf import settings
        
        company_name = settings.COMPANY_NAME
        message = f"""Hello {self.first_name} {self.last_name},
This message is to inform you that, You have been successfully added as a customer at {company_name}.
Please verify your details if they are correct or they needs to be changed
Name: {self.get_full_name()}
Gender: {self.get_gender_display()}
Age: {self.get_age()}
Email: {self.email}
Phone: {self.phone}
If the Details given are correct, please reply as "CORRECT". If any changes need to be made, reply as "To be Changed".
Please reply within 48 hrs of recieveing this message or we will assume your reply as "CORRECT".
Thanks and regards
Team {company_name}"""
        
        return message
    
    def get_whatsapp_url(self):
        """
        Generate a properly formatted WhatsApp URL with the encoded message
        """
        # Get the message content
        message = self.get_whatsapp_message()
        
        # URL encode the message
        encoded_message = urllib.parse.quote(message)
        
        # Format the phone number for WhatsApp
        # Remove any non-numeric characters from the phone
        phone = ''.join(filter(str.isdigit, self.phone))
        
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
        
        return whatsapp_url

class AdminLog(models.Model):
    ACTION_CHOICES = (
        ('signup', 'User Signup'),
        ('login', 'User Login'),
        ('submission', 'Form Submission'),
        ('edit', 'Record Edit'),
        ('delete', 'Record Delete'),
        ('download', 'PDF Download'),
        ('whatsapp', 'WhatsApp Message'),  # Add this if it's missing
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    details = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.timestamp}"

