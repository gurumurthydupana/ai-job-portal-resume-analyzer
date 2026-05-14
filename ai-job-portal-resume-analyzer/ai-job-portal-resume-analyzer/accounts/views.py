from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction

from .models import User, Profile
from .forms import RegisterForm, LoginForm, JobSeekerProfileForm, RecruiterProfileForm
from jobs.models import Job
from applications.models import Application


def register_view(request):
    """Handle user registration with role selection."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save()
                # Auto-create profile
                Profile.objects.create(user=user)
            login(request, user)
            messages.success(request, f"Welcome, {user.username}! Your account has been created.")
            return redirect('dashboard')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """Handle user login."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, "Invalid email or password.")
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """Log out the user."""
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')


@login_required
def dashboard_view(request):
    """
    Role-based dashboard:
    - Job seekers see recommended jobs and their applications.
    - Recruiters see their posted jobs and applicants.
    """
    user = request.user
    context = {'user': user}

    if user.is_recruiter():
        posted_jobs = Job.objects.filter(recruiter=user).order_by('-created_at')
        total_applicants = Application.objects.filter(job__recruiter=user).count()
        recent_applicants = Application.objects.filter(
            job__recruiter=user
        ).select_related('applicant', 'job').order_by('-applied_at')[:5]

        context.update({
            'posted_jobs': posted_jobs,
            'total_applicants': total_applicants,
            'recent_applicants': recent_applicants,
            'total_jobs': posted_jobs.count(),
        })
        return render(request, 'accounts/recruiter_dashboard.html', context)
    else:
        my_applications = Application.objects.filter(
            applicant=user
        ).select_related('job').order_by('-applied_at')
        recommended_jobs = Job.objects.filter(is_active=True).order_by('-created_at')[:6]

        context.update({
            'my_applications': my_applications,
            'recommended_jobs': recommended_jobs,
            'total_applications': my_applications.count(),
        })
        return render(request, 'accounts/jobseeker_dashboard.html', context)


@login_required
def profile_view(request):
    """View own profile."""
    profile, _ = Profile.objects.get_or_create(user=request.user)
    return render(request, 'accounts/profile.html', {'profile': profile})


@login_required
def edit_profile_view(request):
    """Edit profile — uses role-specific form."""
    profile, _ = Profile.objects.get_or_create(user=request.user)

    FormClass = RecruiterProfileForm if request.user.is_recruiter() else JobSeekerProfileForm

    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = FormClass(instance=profile)

    return render(request, 'accounts/edit_profile.html', {'form': form, 'profile': profile})


def public_profile_view(request, user_id):
    """View another user's public profile."""
    user = get_object_or_404(User, id=user_id)
    profile = get_object_or_404(Profile, user=user)
    return render(request, 'accounts/public_profile.html', {'profile': profile, 'viewed_user': user})
