from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Adds a 'role' field to distinguish job seekers from recruiters.
    """
    ROLE_CHOICES = (
        ('job_seeker', 'Job Seeker'),
        ('recruiter', 'Recruiter'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='job_seeker')
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def is_recruiter(self):
        return self.role == 'recruiter'

    def is_job_seeker(self):
        return self.role == 'job_seeker'

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"


class Profile(models.Model):
    """
    Extended profile for each user.
    Job seekers store resume, skills, etc.
    Recruiters store company info.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    # Job Seeker specific
    skills = models.TextField(
        blank=True,
        help_text="Comma-separated list of skills, e.g. Python, Django, SQL"
    )
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    experience_years = models.PositiveIntegerField(default=0)

    # Recruiter specific
    company_name = models.CharField(max_length=150, blank=True)
    company_website = models.URLField(blank=True)
    company_description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_skills_list(self):
        """Return skills as a Python list."""
        if self.skills:
            return [s.strip() for s in self.skills.split(',') if s.strip()]
        return []

    def __str__(self):
        return f"Profile of {self.user.email}"
