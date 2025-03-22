from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from allauth.socialaccount.models import SocialAccount
from .models import UserProfile

@receiver(post_save, sender=SocialAccount)
def create_user_profile(sender, instance, created, **kwargs):
    """Create or update user profile when a social account is created or updated"""
    user = instance.user
    
    # Get profile picture from Google
    if instance.provider == 'google':
        extra_data = instance.extra_data
        profile_picture = extra_data.get('picture', '')
        
        # Create or update user profile
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.profile_picture = profile_picture
        profile.save()

