from django.urls import path
from .api_views import JobListCreateAPIView, JobRetrieveUpdateDestroyAPIView, RecruiterJobsAPIView

urlpatterns = [
    path('jobs/', JobListCreateAPIView.as_view(), name='api_jobs'),
    path('jobs/<int:pk>/', JobRetrieveUpdateDestroyAPIView.as_view(), name='api_job_detail'),
    path('jobs/my-jobs/', RecruiterJobsAPIView.as_view(), name='api_my_jobs'),
]
