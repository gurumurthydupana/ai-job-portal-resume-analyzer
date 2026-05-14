from django.db import models
from accounts.models import User


class Job(models.Model):
    """
    A job posting created by a recruiter.
    required_skills is stored as a comma-separated string.
    """
    EMPLOYMENT_TYPE_CHOICES = (
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('freelance', 'Freelance'),
    )

    EXPERIENCE_LEVEL_CHOICES = (
        ('entry', 'Entry Level (0-2 years)'),
        ('mid', 'Mid Level (2-5 years)'),
        ('senior', 'Senior Level (5+ years)'),
    )

    recruiter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_jobs')
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=150)
    location = models.CharField(max_length=150)
    description = models.TextField()
    required_skills = models.TextField(
        help_text="Comma-separated list of required skills, e.g. Python, Django, SQL"
    )
    salary_min = models.PositiveIntegerField(null=True, blank=True)
    salary_max = models.PositiveIntegerField(null=True, blank=True)
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES, default='full_time')
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVEL_CHOICES, default='entry')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deadline = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def get_required_skills_list(self):
        """Return required skills as a Python list."""
        if self.required_skills:
            return [s.strip() for s in self.required_skills.split(',') if s.strip()]
        return []

    def get_salary_display(self):
        if self.salary_min and self.salary_max:
            return f"₹{self.salary_min:,} – ₹{self.salary_max:,} per year"
        elif self.salary_min:
            return f"From ₹{self.salary_min:,}"
        return "Not disclosed"

    def __str__(self):
        return f"{self.title} at {self.company}"
