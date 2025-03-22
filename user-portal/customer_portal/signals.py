from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.models import User
from allauth.account.signals import user_signed_up
from .models import AdminLog

@receiver(user_signed_up)
def log_user_signup(request, user, **kwargs):
    """Log when a user signs up"""
    AdminLog.objects.create(
        user=user,
        action='signup',
        details=f"User {user.username} signed up"
    )

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Log when a user logs in"""
    AdminLog.objects.create(
        user=user,
        action='login',
        details=f"User {user.username} logged in"
    )

