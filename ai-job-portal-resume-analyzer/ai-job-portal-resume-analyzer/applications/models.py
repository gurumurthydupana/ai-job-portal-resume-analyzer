from django.db import models
from accounts.models import User
from jobs.models import Job


class Application(models.Model):
    """
    Represents a job seeker's application to a specific job.
    Tracks workflow stages and resume match score.
    """
    STATUS_CHOICES = (
        ('applied', 'Applied'),
        ('reviewed', 'Reviewed'),
        ('shortlisted', 'Shortlisted'),
        ('interview', 'Interview Scheduled'),
        ('rejected', 'Rejected'),
        ('hired', 'Hired'),
    )

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    cover_letter = models.TextField(blank=True)
    resume_score = models.FloatField(default=0.0, help_text="Match score between resume skills and job requirements (0-100)")
    matched_skills = models.TextField(blank=True, help_text="Comma-separated matched skills")
    missing_skills = models.TextField(blank=True, help_text="Comma-separated missing skills")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    recruiter_notes = models.TextField(blank=True)

    class Meta:
        # Prevent duplicate applications
        unique_together = ('job', 'applicant')
        ordering = ['-applied_at']

    def get_matched_skills_list(self):
        if self.matched_skills:
            return [s.strip() for s in self.matched_skills.split(',') if s.strip()]
        return []

    def get_missing_skills_list(self):
        if self.missing_skills:
            return [s.strip() for s in self.missing_skills.split(',') if s.strip()]
        return []

    def get_score_badge_class(self):
        """Return Bootstrap badge color based on score."""
        if self.resume_score >= 75:
            return 'success'
        elif self.resume_score >= 50:
            return 'warning'
        return 'danger'

    def __str__(self):
        return f"{self.applicant.email} → {self.job.title} ({self.status})"
