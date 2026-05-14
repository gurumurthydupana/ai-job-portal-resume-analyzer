"""
Management command to seed the database with realistic demo data.

Usage:
    python manage.py seed_data

Creates:
    - 2 recruiter accounts
    - 3 job seeker accounts
    - 10 realistic job postings
    - Sample profiles for all users
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from accounts.models import User, Profile
from jobs.models import Job


SAMPLE_JOBS = [
    {
        "title": "Senior Django Developer",
        "company": "TechCorp India",
        "location": "Bangalore, India",
        "description": (
            "We are looking for an experienced Django developer to join our backend team. "
            "You will design, build, and maintain scalable REST APIs, work closely with frontend "
            "engineers, and deploy services on AWS. Strong understanding of ORM, caching, "
            "and Celery task queues is required."
        ),
        "required_skills": "Python, Django, REST API, PostgreSQL, Redis, Docker, Git",
        "salary_min": 1200000,
        "salary_max": 1800000,
        "employment_type": "full_time",
        "experience_level": "senior",
    },
    {
        "title": "Full Stack Developer",
        "company": "StartupHub",
        "location": "Hyderabad, India",
        "description": (
            "Join our fast-growing startup as a Full Stack Developer. You will own features "
            "from database schema design to React UI. We value initiative, clean code, and "
            "a product-first mindset."
        ),
        "required_skills": "Python, Django, React, JavaScript, SQL, Git, HTML, CSS",
        "salary_min": 800000,
        "salary_max": 1400000,
        "employment_type": "full_time",
        "experience_level": "mid",
    },
    {
        "title": "Python Backend Engineer",
        "company": "Fintech Solutions",
        "location": "Chennai, India",
        "description": (
            "Build secure, high-performance APIs for our financial products. "
            "Experience with payment gateways, JWT-based auth, and compliance-aware coding is a plus."
        ),
        "required_skills": "Python, FastAPI, PostgreSQL, Docker, AWS, JWT, REST API",
        "salary_min": 1000000,
        "salary_max": 1600000,
        "employment_type": "full_time",
        "experience_level": "mid",
    },
    {
        "title": "Machine Learning Engineer",
        "company": "AI Labs Pvt Ltd",
        "location": "Pune, India",
        "description": (
            "Design and deploy ML models at scale. Work on NLP pipelines, recommendation "
            "systems, and computer vision projects. Strong maths background and hands-on "
            "PyTorch experience required."
        ),
        "required_skills": "Python, Machine Learning, PyTorch, scikit-learn, NLP, Docker, Git",
        "salary_min": 1500000,
        "salary_max": 2500000,
        "employment_type": "full_time",
        "experience_level": "senior",
    },
    {
        "title": "Junior Django Developer",
        "company": "WebAgency Co",
        "location": "Mumbai, India",
        "description": (
            "Great entry-level opportunity for a fresh Django developer. You will work on "
            "client websites, implement REST endpoints, and learn from a senior team. "
            "Good communication skills are important."
        ),
        "required_skills": "Python, Django, HTML, CSS, JavaScript, SQL, Git",
        "salary_min": 400000,
        "salary_max": 700000,
        "employment_type": "full_time",
        "experience_level": "entry",
    },
    {
        "title": "DevOps Engineer",
        "company": "CloudBase Technologies",
        "location": "Remote",
        "description": (
            "Manage CI/CD pipelines, container orchestration, and cloud infrastructure. "
            "You will work with development teams to improve deployment velocity and reliability."
        ),
        "required_skills": "Docker, Kubernetes, AWS, Terraform, Jenkins, Linux, Python, Git",
        "salary_min": 1100000,
        "salary_max": 1900000,
        "employment_type": "full_time",
        "experience_level": "mid",
    },
    {
        "title": "Data Analyst",
        "company": "Analytics Corp",
        "location": "Delhi, India",
        "description": (
            "Analyse large datasets to derive business insights. Build dashboards in "
            "Tableau and Power BI. Collaborate with product and marketing teams to define KPIs."
        ),
        "required_skills": "Python, SQL, Pandas, NumPy, Tableau, Power BI, Excel",
        "salary_min": 600000,
        "salary_max": 1000000,
        "employment_type": "full_time",
        "experience_level": "entry",
    },
    {
        "title": "React Frontend Developer",
        "company": "UX Studio",
        "location": "Bangalore, India",
        "description": (
            "Build beautiful, accessible, and performant UIs using React and TypeScript. "
            "You will translate Figma designs into pixel-perfect components."
        ),
        "required_skills": "React, JavaScript, TypeScript, HTML, CSS, Git, REST API",
        "salary_min": 700000,
        "salary_max": 1300000,
        "employment_type": "full_time",
        "experience_level": "mid",
    },
    {
        "title": "Django Intern",
        "company": "GrowthStartup",
        "location": "Remote",
        "description": (
            "Ideal for final-year students or fresh graduates. You will assist in building "
            "Django views, writing unit tests, and contributing to our open-source projects."
        ),
        "required_skills": "Python, Django, HTML, CSS, Git",
        "salary_min": 150000,
        "salary_max": 250000,
        "employment_type": "internship",
        "experience_level": "entry",
    },
    {
        "title": "Cloud Solutions Architect",
        "company": "Enterprise Systems Ltd",
        "location": "Hyderabad, India",
        "description": (
            "Lead the design and implementation of cloud infrastructure for enterprise clients. "
            "You will conduct architecture reviews, produce technical documentation, and "
            "mentor junior engineers."
        ),
        "required_skills": "AWS, Azure, Docker, Kubernetes, Terraform, Python, Linux, CI/CD",
        "salary_min": 2000000,
        "salary_max": 3500000,
        "employment_type": "full_time",
        "experience_level": "senior",
    },
]


class Command(BaseCommand):
    help = "Seeds the database with demo users and job postings."

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("Seeding database with demo data..."))

        with transaction.atomic():
            # ── Recruiters ──
            rec1, created = User.objects.get_or_create(
                email="recruiter1@techcorp.com",
                defaults={"username": "hr_techcorp", "role": "recruiter"}
            )
            if created:
                rec1.set_password("Demo@1234")
                rec1.save()
                Profile.objects.filter(user=rec1).update(
                    full_name="Priya Sharma",
                    company_name="TechCorp India",
                    company_website="https://techcorp.example.com",
                    location="Bangalore, India",
                )
                self.stdout.write(f"  Created recruiter: {rec1.email}")

            rec2, created = User.objects.get_or_create(
                email="recruiter2@startups.com",
                defaults={"username": "hr_startups", "role": "recruiter"}
            )
            if created:
                rec2.set_password("Demo@1234")
                rec2.save()
                Profile.objects.filter(user=rec2).update(
                    full_name="Arjun Mehta",
                    company_name="StartupHub",
                    location="Hyderabad, India",
                )
                self.stdout.write(f"  Created recruiter: {rec2.email}")

            # ── Job Seekers ──
            seekers_data = [
                {
                    "email": "seeker1@gmail.com",
                    "username": "dev_ravi",
                    "full_name": "Ravi Kumar",
                    "skills": "Python, Django, REST API, SQL, Git, HTML, CSS",
                    "experience_years": 3,
                },
                {
                    "email": "seeker2@gmail.com",
                    "username": "dev_ananya",
                    "full_name": "Ananya Patel",
                    "skills": "Python, Machine Learning, scikit-learn, Pandas, NumPy, SQL",
                    "experience_years": 2,
                },
                {
                    "email": "seeker3@gmail.com",
                    "username": "dev_kiran",
                    "full_name": "Kiran Singh",
                    "skills": "React, JavaScript, HTML, CSS, Git, REST API",
                    "experience_years": 1,
                },
            ]

            for sd in seekers_data:
                seeker, created = User.objects.get_or_create(
                    email=sd["email"],
                    defaults={"username": sd["username"], "role": "job_seeker"}
                )
                if created:
                    seeker.set_password("Demo@1234")
                    seeker.save()
                    Profile.objects.filter(user=seeker).update(
                        full_name=sd["full_name"],
                        skills=sd["skills"],
                        experience_years=sd["experience_years"],
                        location="India",
                    )
                    self.stdout.write(f"  Created job seeker: {seeker.email}")

            # ── Jobs ──
            recruiters = [rec1, rec2]
            for i, job_data in enumerate(SAMPLE_JOBS):
                recruiter = recruiters[i % 2]
                job, created = Job.objects.get_or_create(
                    title=job_data["title"],
                    company=job_data["company"],
                    defaults={
                        "recruiter": recruiter,
                        **{k: v for k, v in job_data.items() if k not in ["title", "company"]},
                    }
                )
                if created:
                    self.stdout.write(f"  Created job: {job.title} @ {job.company}")

        self.stdout.write(self.style.SUCCESS("\n✅ Database seeded successfully!"))
        self.stdout.write("\nDemo credentials (all passwords: Demo@1234):")
        self.stdout.write("  Recruiter 1 : recruiter1@techcorp.com")
        self.stdout.write("  Recruiter 2 : recruiter2@startups.com")
        self.stdout.write("  Job Seeker 1: seeker1@gmail.com")
        self.stdout.write("  Job Seeker 2: seeker2@gmail.com")
        self.stdout.write("  Job Seeker 3: seeker3@gmail.com")
