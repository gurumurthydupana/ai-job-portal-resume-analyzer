from rest_framework import generics, permissions
from .models import Application
from .serializers import ApplicationSerializer


class ApplicationListCreateAPIView(generics.ListCreateAPIView):
    """
    GET  /api/applications/  — List current user's applications
    POST /api/applications/  — Apply to a job
    """
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_recruiter():
            return Application.objects.filter(job__recruiter=user)
        return Application.objects.filter(applicant=user)

    def perform_create(self, serializer):
        serializer.save(applicant=self.request.user)


class ApplicationRetrieveAPIView(generics.RetrieveUpdateAPIView):
    """
    GET   /api/applications/<id>/  — View application details
    PATCH /api/applications/<id>/  — Recruiter updates status
    """
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_recruiter():
            return Application.objects.filter(job__recruiter=user)
        return Application.objects.filter(applicant=user)
