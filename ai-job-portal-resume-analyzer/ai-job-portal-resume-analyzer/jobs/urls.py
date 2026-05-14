from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('list/', views.job_list_view, name='job_list'),
    path('<int:job_id>/', views.job_detail_view, name='job_detail'),
    path('post/', views.post_job_view, name='post_job'),
    path('<int:job_id>/edit/', views.edit_job_view, name='edit_job'),
    path('<int:job_id>/delete/', views.delete_job_view, name='delete_job'),
    path('my-jobs/', views.my_posted_jobs_view, name='my_jobs'),
]
