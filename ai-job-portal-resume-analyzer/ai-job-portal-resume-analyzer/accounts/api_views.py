from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction

from .models import User, Profile
from .serializers import UserSerializer, ProfileSerializer, RegisterSerializer


class RegisterAPIView(generics.CreateAPIView):
    """
    POST /api/auth/register/
    Register a new user (job seeker or recruiter) via API.
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        with transaction.atomic():
            user = serializer.save()
            Profile.objects.create(user=user)


class UserProfileAPIView(APIView):
    """
    GET /api/auth/me/
    Returns the authenticated user's profile data.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        profile, _ = Profile.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'profile': ProfileSerializer(profile).data,
        })
