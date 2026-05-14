from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Job
from .serializers import JobSerializer, JobCreateSerializer


class IsRecruiterOrReadOnly(permissions.BasePermission):
    """Only recruiters can create/update/delete jobs. Anyone can read."""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_recruiter()

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.recruiter == request.user


class JobListCreateAPIView(generics.ListCreateAPIView):
    """
    GET  /api/jobs/         — List all active jobs (with search/filter)
    POST /api/jobs/         — Recruiter creates a new job
    """
    queryset = Job.objects.filter(is_active=True)
    permission_classes = [IsRecruiterOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'company', 'location', 'required_skills', 'description']
    ordering_fields = ['created_at', 'salary_min']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return JobCreateSerializer
        return JobSerializer


class JobRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/jobs/<id>/   — Job detail
    PUT    /api/jobs/<id>/   — Recruiter updates job
    DELETE /api/jobs/<id>/   — Recruiter deletes job
    """
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [IsRecruiterOrReadOnly]


class RecruiterJobsAPIView(generics.ListAPIView):
    """
    GET /api/jobs/my-jobs/  — Recruiter's own jobs (authenticated)
    """
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Job.objects.filter(recruiter=self.request.user)
