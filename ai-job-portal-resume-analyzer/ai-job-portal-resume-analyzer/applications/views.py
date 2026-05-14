from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings

from .models import Application
from jobs.models import Job
from resume_analyzer.utils import calculate_match_score, extract_skills_from_resume


@login_required
def apply_to_job_view(request, job_id):
    """
    Job seeker applies to a job.
    - Prevents duplicate applications (DB constraint + check).
    - Auto-calculates resume match score.
    - Sends email notification to recruiter.
    """
    if not request.user.is_job_seeker():
        messages.error(request, "Only job seekers can apply.")
        return redirect('job_detail', job_id=job_id)

    job = get_object_or_404(Job, id=job_id, is_active=True)

    # Duplicate check
    if Application.objects.filter(job=job, applicant=request.user).exists():
        messages.warning(request, "You have already applied for this job.")
        return redirect('job_detail', job_id=job_id)

    profile = getattr(request.user, 'profile', None)

    # Calculate resume match score
    resume_score = 0.0
    matched_skills = []
    missing_skills = []

    job_skills = job.get_required_skills_list()

    if profile and profile.resume:
        # Extract skills from uploaded resume PDF
        try:
            extracted_skills = extract_skills_from_resume(profile.resume.path)
        except Exception:
            extracted_skills = profile.get_skills_list()
    elif profile and profile.skills:
        extracted_skills = profile.get_skills_list()
    else:
        extracted_skills = []

    if extracted_skills and job_skills:
        resume_score, matched_skills, missing_skills = calculate_match_score(
            extracted_skills, job_skills, return_details=True
        )

    if request.method == 'POST':
        cover_letter = request.POST.get('cover_letter', '')

        application = Application.objects.create(
            job=job,
            applicant=request.user,
            cover_letter=cover_letter,
            resume_score=resume_score,
            matched_skills=', '.join(matched_skills),
            missing_skills=', '.join(missing_skills),
            status='applied',
        )

        # Email notification to recruiter
        try:
            send_mail(
                subject=f"New Application: {job.title}",
                message=(
                    f"Hello {job.recruiter.username},\n\n"
                    f"{request.user.get_full_name() or request.user.username} has applied for '{job.title}'.\n"
                    f"Resume Match Score: {resume_score:.1f}%\n\n"
                    f"Login to the portal to review the application."
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[job.recruiter.email],
                fail_silently=True,
            )
        except Exception:
            pass  # Don't block application if email fails

        messages.success(request, f"Successfully applied for '{job.title}'! Match score: {resume_score:.1f}%")
        return redirect('application_detail', application_id=application.id)

    return render(request, 'applications/apply.html', {
        'job': job,
        'profile': profile,
        'resume_score': resume_score,
        'matched_skills': matched_skills,
        'missing_skills': missing_skills,
    })


@login_required
def application_detail_view(request, application_id):
    """View a single application's details."""
    application = get_object_or_404(Application, id=application_id)

    # Only the applicant or the job's recruiter can view
    if request.user != application.applicant and request.user != application.job.recruiter:
        messages.error(request, "You don't have permission to view this application.")
        return redirect('dashboard')

    return render(request, 'applications/application_detail.html', {'application': application})


@login_required
def my_applications_view(request):
    """Job seeker's application history with status tracking."""
    if not request.user.is_job_seeker():
        return redirect('dashboard')

    applications = Application.objects.filter(
        applicant=request.user
    ).select_related('job').order_by('-applied_at')

    status_filter = request.GET.get('status', '')
    if status_filter:
        applications = applications.filter(status=status_filter)

    return render(request, 'applications/my_applications.html', {
        'applications': applications,
        'status_filter': status_filter,
        'status_choices': Application.STATUS_CHOICES,
    })


@login_required
def job_applicants_view(request, job_id):
    """Recruiter views all applicants for a job, sorted by match score."""
    job = get_object_or_404(Job, id=job_id, recruiter=request.user)
    applications = Application.objects.filter(job=job).select_related(
        'applicant', 'applicant__profile'
    ).order_by('-resume_score')

    return render(request, 'applications/job_applicants.html', {
        'job': job,
        'applications': applications,
    })


@login_required
def update_application_status_view(request, application_id):
    """
    Recruiter updates application status.
    Sends email notification to candidate.
    """
    application = get_object_or_404(Application, id=application_id)

    if request.user != application.job.recruiter:
        messages.error(request, "Only the job recruiter can update application status.")
        return redirect('dashboard')

    if request.method == 'POST':
        new_status = request.POST.get('status')
        notes = request.POST.get('recruiter_notes', '')

        if new_status in dict(Application.STATUS_CHOICES):
            old_status = application.status
            application.status = new_status
            application.recruiter_notes = notes
            application.save()

            # Notify candidate
            try:
                send_mail(
                    subject=f"Application Update: {application.job.title}",
                    message=(
                        f"Hello {application.applicant.username},\n\n"
                        f"Your application for '{application.job.title}' at {application.job.company} "
                        f"has been updated.\n\nNew Status: {application.get_status_display()}\n\n"
                        f"Recruiter Notes: {notes or 'None'}\n\n"
                        f"Login to view your application dashboard."
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[application.applicant.email],
                    fail_silently=True,
                )
            except Exception:
                pass

            messages.success(request, f"Status updated to '{application.get_status_display()}'.")

    return redirect('job_applicants', job_id=application.job.id)
