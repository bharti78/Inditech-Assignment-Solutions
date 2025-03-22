from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from customer_portal.views import home
from allauth.socialaccount.providers.google.views import oauth2_login

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', home, name='home'),
    path('portal/', include('customer_portal.urls')),
    path('accounts/google/login/', oauth2_login, name='google_login'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

