from django.urls import path
from . import views

urlpatterns = [
    path('apply/<int:job_id>/', views.apply_to_job_view, name='apply_to_job'),
    path('<int:application_id>/', views.application_detail_view, name='application_detail'),
    path('my/', views.my_applications_view, name='my_applications'),
    path('job/<int:job_id>/applicants/', views.job_applicants_view, name='job_applicants'),
    path('<int:application_id>/update-status/', views.update_application_status_view, name='update_application_status'),
]
