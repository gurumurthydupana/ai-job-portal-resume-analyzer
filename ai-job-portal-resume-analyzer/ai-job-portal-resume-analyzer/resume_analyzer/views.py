from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from jobs.models import Job
from .utils import analyze_resume_for_job, extract_skills_from_resume, get_skill_suggestions


@login_required
def analyze_resume_view(request, job_id=None):
    """
    Analyze the logged-in user's resume against a specific job's requirements.
    If no job_id, show general resume skill analysis.
    """
    if not request.user.is_job_seeker():
        messages.error(request, "Resume analysis is only available for job seekers.")
        return redirect('dashboard')

    profile = getattr(request.user, 'profile', None)
    job = None
    analysis_result = None

    if job_id:
        job = get_object_or_404(Job, id=job_id, is_active=True)

    if request.method == 'POST' or job_id:
        if not profile or not profile.resume:
            messages.warning(
                request,
                "Please upload your resume in your profile first before analyzing."
            )
            return redirect('edit_profile')

        try:
            job_skills = job.get_required_skills_list() if job else []

            if job:
                analysis_result = analyze_resume_for_job(profile.resume.path, job_skills)
            else:
                # General analysis — just extract skills
                extracted = extract_skills_from_resume(profile.resume.path)
                analysis_result = {
                    'extracted_skills': extracted,
                    'score': None,
                    'matched_skills': [],
                    'missing_skills': [],
                    'skill_suggestions': [],
                    'total_required': 0,
                    'total_matched': len(extracted),
                }

        except Exception as e:
            messages.error(request, f"Could not analyze resume: {str(e)}")

    jobs_list = Job.objects.filter(is_active=True).order_by('-created_at')[:10]

    return render(request, 'resume_analyzer/analyze.html', {
        'profile': profile,
        'job': job,
        'analysis': analysis_result,
        'jobs_list': jobs_list,
    })


@login_required
def skill_gap_view(request):
    """
    Show the user's profile skills vs. skills in demand across all active jobs.
    Gives a broader skill gap analysis.
    """
    profile = getattr(request.user, 'profile', None)
    user_skills = set(profile.get_skills_list()) if profile else set()

    # Aggregate all required skills from active jobs
    all_jobs = Job.objects.filter(is_active=True)
    skill_frequency = {}
    for job in all_jobs:
        for skill in job.get_required_skills_list():
            skill_lower = skill.lower()
            skill_frequency[skill_lower] = skill_frequency.get(skill_lower, 0) + 1

    # Sort by demand
    sorted_skills = sorted(skill_frequency.items(), key=lambda x: x[1], reverse=True)

    # Top 20 in-demand skills
    top_skills = sorted_skills[:20]
    user_skills_lower = {s.lower() for s in user_skills}

    skill_data = []
    for skill, count in top_skills:
        skill_data.append({
            'skill': skill,
            'demand_count': count,
            'you_have_it': skill in user_skills_lower,
        })

    suggestions = get_skill_suggestions([
        item['skill'] for item in skill_data if not item['you_have_it']
    ][:5])

    return render(request, 'resume_analyzer/skill_gap.html', {
        'skill_data': skill_data,
        'suggestions': suggestions,
        'profile': profile,
    })
