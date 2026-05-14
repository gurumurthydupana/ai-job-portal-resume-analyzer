from django.urls import path
from . import views

urlpatterns = [
    path('analyze/', views.analyze_resume_view, name='analyze_resume'),
    path('analyze/<int:job_id>/', views.analyze_resume_view, name='analyze_resume_for_job'),
    path('skill-gap/', views.skill_gap_view, name='skill_gap'),
]
