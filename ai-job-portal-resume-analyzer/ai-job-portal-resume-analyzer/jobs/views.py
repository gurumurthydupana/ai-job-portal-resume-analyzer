from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .models import Job
from .forms import JobForm, JobSearchForm
from applications.models import Application


def home_view(request):
    """Landing page with featured jobs and search."""
    featured_jobs = Job.objects.filter(is_active=True).order_by('-created_at')[:6]
    search_form = JobSearchForm()
    return render(request, 'jobs/home.html', {
        'featured_jobs': featured_jobs,
        'search_form': search_form,
    })


def job_list_view(request):
    """
    Job listing with full-text search and filters.
    Supports keyword, location, type, and experience-level filtering.
    """
    jobs = Job.objects.filter(is_active=True)
    form = JobSearchForm(request.GET or None)

    if form.is_valid():
        keyword = form.cleaned_data.get('keyword')
        location = form.cleaned_data.get('location')
        emp_type = form.cleaned_data.get('employment_type')
        exp_level = form.cleaned_data.get('experience_level')

        if keyword:
            jobs = jobs.filter(
                Q(title__icontains=keyword) |
                Q(description__icontains=keyword) |
                Q(required_skills__icontains=keyword) |
                Q(company__icontains=keyword)
            )
        if location:
            jobs = jobs.filter(location__icontains=location)
        if emp_type:
            jobs = jobs.filter(employment_type=emp_type)
        if exp_level:
            jobs = jobs.filter(experience_level=exp_level)

    # Track already-applied jobs for logged-in users
    applied_job_ids = []
    if request.user.is_authenticated:
        applied_job_ids = list(
            Application.objects.filter(applicant=request.user).values_list('job_id', flat=True)
        )

    return render(request, 'jobs/job_list.html', {
        'jobs': jobs,
        'form': form,
        'applied_job_ids': applied_job_ids,
        'total_jobs': jobs.count(),
    })


def job_detail_view(request, job_id):
    """
    Job detail page.
    Shows job info, required skills, and apply button (if job seeker).
    """
    job = get_object_or_404(Job, id=job_id, is_active=True)
    already_applied = False
    match_score = None

    if request.user.is_authenticated and request.user.is_job_seeker():
        already_applied = Application.objects.filter(
            job=job, applicant=request.user
        ).exists()

        # Quick match score preview
        if hasattr(request.user, 'profile') and request.user.profile.skills:
            from resume_analyzer.utils import calculate_match_score
            match_score = calculate_match_score(
                request.user.profile.get_skills_list(),
                job.get_required_skills_list()
            )

    return render(request, 'jobs/job_detail.html', {
        'job': job,
        'already_applied': already_applied,
        'match_score': match_score,
    })


@login_required
def post_job_view(request):
    """Recruiters post new jobs."""
    if not request.user.is_recruiter():
        messages.error(request, "Only recruiters can post jobs.")
        return redirect('job_list')

    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.recruiter = request.user
            job.save()
            messages.success(request, f'Job "{job.title}" posted successfully!')
            return redirect('job_detail', job_id=job.id)
    else:
        # Pre-fill company from recruiter's profile
        initial = {}
        if hasattr(request.user, 'profile') and request.user.profile.company_name:
            initial['company'] = request.user.profile.company_name
        form = JobForm(initial=initial)

    return render(request, 'jobs/post_job.html', {'form': form})


@login_required
def edit_job_view(request, job_id):
    """Recruiters edit their own job postings."""
    job = get_object_or_404(Job, id=job_id, recruiter=request.user)

    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, "Job updated successfully!")
            return redirect('job_detail', job_id=job.id)
    else:
        form = JobForm(instance=job)

    return render(request, 'jobs/edit_job.html', {'form': form, 'job': job})


@login_required
def delete_job_view(request, job_id):
    """Recruiters delete their own job postings."""
    job = get_object_or_404(Job, id=job_id, recruiter=request.user)

    if request.method == 'POST':
        job_title = job.title
        job.delete()
        messages.success(request, f'Job "{job_title}" deleted.')
        return redirect('dashboard')

    return render(request, 'jobs/delete_job_confirm.html', {'job': job})


@login_required
def my_posted_jobs_view(request):
    """Recruiter's list of all their posted jobs."""
    if not request.user.is_recruiter():
        return redirect('dashboard')
    jobs = Job.objects.filter(recruiter=request.user)
    return render(request, 'jobs/my_jobs.html', {'jobs': jobs})
