from django.contrib import admin
from .models import Job


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'location', 'employment_type', 'is_active', 'created_at']
    list_filter = ['is_active', 'employment_type', 'experience_level']
    search_fields = ['title', 'company', 'location', 'required_skills']
    list_editable = ['is_active']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']
