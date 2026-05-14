from django.urls import path
from .api_views import ApplicationListCreateAPIView, ApplicationRetrieveAPIView

urlpatterns = [
    path('', ApplicationListCreateAPIView.as_view(), name='api_applications'),
    path('<int:pk>/', ApplicationRetrieveAPIView.as_view(), name='api_application_detail'),
]
