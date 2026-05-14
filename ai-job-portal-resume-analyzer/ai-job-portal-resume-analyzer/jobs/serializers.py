from rest_framework import serializers
from .models import Job
from accounts.serializers import UserSerializer


class JobSerializer(serializers.ModelSerializer):
    recruiter = UserSerializer(read_only=True)
    required_skills_list = serializers.SerializerMethodField()
    salary_display = serializers.SerializerMethodField()
    total_applications = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = [
            'id', 'recruiter', 'title', 'company', 'location',
            'description', 'required_skills', 'required_skills_list',
            'salary_min', 'salary_max', 'salary_display',
            'employment_type', 'experience_level',
            'is_active', 'created_at', 'deadline',
            'total_applications',
        ]
        read_only_fields = ['id', 'recruiter', 'created_at']

    def get_required_skills_list(self, obj):
        return obj.get_required_skills_list()

    def get_salary_display(self, obj):
        return obj.get_salary_display()

    def get_total_applications(self, obj):
        return obj.applications.count()


class JobCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = [
            'title', 'company', 'location', 'description',
            'required_skills', 'salary_min', 'salary_max',
            'employment_type', 'experience_level', 'deadline',
        ]

    def create(self, validated_data):
        request = self.context.get('request')
        job = Job.objects.create(recruiter=request.user, **validated_data)
        return job
