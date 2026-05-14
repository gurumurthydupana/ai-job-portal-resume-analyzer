from django.contrib import admin
from .models import Application


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['applicant', 'job', 'status', 'resume_score', 'applied_at']
    list_filter = ['status']
    search_fields = ['applicant__email', 'job__title', 'job__company']
    list_editable = ['status']
    readonly_fields = ['applied_at', 'updated_at', 'resume_score', 'matched_skills', 'missing_skills']
    ordering = ['-applied_at']
