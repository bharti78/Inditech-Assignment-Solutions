from django.conf import settings

def company_info(request):
    """Add company information to context"""
    return {
        'company_name': settings.COMPANY_NAME,
        'portal_name': settings.PORTAL_NAME,
    }

