from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .api_views import RegisterAPIView, UserProfileAPIView

urlpatterns = [
    # JWT token endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Register via API
    path('register/', RegisterAPIView.as_view(), name='api_register'),

    # Authenticated user's profile
    path('me/', UserProfileAPIView.as_view(), name='api_me'),
]
