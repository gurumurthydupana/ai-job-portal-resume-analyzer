"""
Root URL Configuration for AI Job Portal
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Home redirect
    path('', include('jobs.urls')),

    # Accounts (auth + profiles)
    path('accounts/', include('accounts.urls')),

    # Jobs
    path('jobs/', include('jobs.urls')),

    # Applications
    path('applications/', include('applications.urls')),

    # Resume Analyzer
    path('resume/', include('resume_analyzer.urls')),

    # REST API
    path('api/', include('jobs.api_urls')),
    path('api/applications/', include('applications.api_urls')),

    # JWT Token endpoints
    path('api/auth/', include('accounts.api_urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom Admin titles
admin.site.site_header = "AI Job Portal Admin"
admin.site.site_title = "AI Job Portal"
admin.site.index_title = "Dashboard"
