from rest_framework import serializers
from .models import Application
from jobs.serializers import JobSerializer
from accounts.serializers import UserSerializer


class ApplicationSerializer(serializers.ModelSerializer):
    job = JobSerializer(read_only=True)
    applicant = UserSerializer(read_only=True)
    job_id = serializers.PrimaryKeyRelatedField(
        queryset=__import__('jobs.models', fromlist=['Job']).Job.objects.all(),
        source='job',
        write_only=True,
    )
    score_badge = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = [
            'id', 'job', 'job_id', 'applicant', 'cover_letter',
            'resume_score', 'matched_skills', 'missing_skills',
            'status', 'applied_at', 'score_badge',
        ]
        read_only_fields = ['id', 'applicant', 'resume_score', 'matched_skills', 'missing_skills', 'applied_at']

    def get_score_badge(self, obj):
        return obj.get_score_badge_class()
