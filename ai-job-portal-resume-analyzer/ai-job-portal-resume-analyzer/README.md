# AI-Powered Job Portal & Resume Analyzer

> **Full-stack Django web application** with AI-driven resume analysis, role-based authentication, REST APIs, and automated email notifications.

[![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.x-green?logo=django)](https://djangoproject.com/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple?logo=bootstrap)](https://getbootstrap.com/)
[![DRF](https://img.shields.io/badge/DRF-3.15-red)](https://www.django-rest-framework.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Tech Stack](#tech-stack)
4. [Project Structure](#project-structure)
5. [Database Design](#database-design)
6. [Resume Analyzer — How It Works](#resume-analyzer--how-it-works)
7. [REST API Endpoints](#rest-api-endpoints)
8. [Setup & Installation](#setup--installation)
9. [Running the Project](#running-the-project)
10. [Seeding Demo Data](#seeding-demo-data)
11. [Deployment on Render](#deployment-on-render)
12. [Screenshots](#screenshots)
13. [Interview Q&A](#interview-qa)

---

## Project Overview

An AI-powered job portal where:

- **Job Seekers** create profiles, upload PDF resumes, search jobs, apply, and receive match scores with missing skill recommendations.
- **Recruiters** post jobs with required skills, review applicants sorted by AI match score, and update application status at each workflow stage.
- **The AI Resume Analyzer** extracts skills from a PDF resume using `pdfplumber`, compares them with job requirements, calculates a percentage match score, identifies missing skills, and suggests learning resources.
- **REST APIs** expose all core functionality for programmatic access, secured with JWT tokens.
- **Email Notifications** alert recruiters on new applications and candidates on status changes.

---

## Features

### Authentication & Roles
- Register / Login / Logout
- Custom `User` model with `role` field (`job_seeker` / `recruiter`)
- Role-based dashboards — different UI for each role
- Auto-created `Profile` via Django signals

### Job Seeker
- Edit profile with skills, resume (PDF), photo, LinkedIn/GitHub links
- Advanced job search — keyword, location, employment type, experience level
- Apply to jobs (duplicate prevention via DB `unique_together` constraint)
- Application history with status tracking across 6 workflow stages
- Resume match score preview on each job card
- Full resume analysis — matched skills, missing skills, learning resources

### Recruiter
- Post, edit, and delete job listings
- View all applicants sorted by AI match score (highest first)
- Update application status at each stage with recruiter notes
- Recruiter dashboard with posted jobs and recent applicants

### Resume Analyzer (AI Core)
- PDF text extraction using `pdfplumber`
- Keyword matching against a categorised skills database (50+ skills)
- Match score formula: `(matched / required) * 100`
- Missing skills identified with free learning resource links
- Market skill gap analysis — top 20 in-demand skills vs. your profile
- General resume skill extraction (independent of any specific job)

### REST APIs (Django REST Framework)
- JWT authentication (`/api/auth/token/`)
- Job listing with search and filters (`/api/jobs/`)
- Job CRUD for recruiters (`/api/jobs/<id>/`)
- Application create/list/status update (`/api/applications/`)
- User profile endpoint (`/api/auth/me/`)

### Email Notifications
- Recruiter notified when candidate applies (with match score in email)
- Candidate notified when application status changes (with recruiter notes)
- Console backend for development; SMTP for production

### Admin Dashboard
- Django admin with custom list displays, filters, and search
- Inline profile editing alongside user
- Bulk status updates for applications

---

## Tech Stack

| Layer          | Technology                                      |
|----------------|-------------------------------------------------|
| Language       | Python 3.x                                      |
| Framework      | Django 5.x                                      |
| REST API       | Django REST Framework 3.15 + SimpleJWT          |
| Frontend       | HTML5, CSS3, JavaScript, Bootstrap 5.3          |
| PDF Parsing    | pdfplumber                                      |
| Forms          | django-crispy-forms + crispy-bootstrap5         |
| Database       | SQLite (dev) / MySQL (production)               |
| Static Files   | WhiteNoise                                      |
| Email          | Django email (console / SMTP)                   |
| Deployment     | Render (gunicorn)                               |
| Version Control| Git / GitHub                                    |

---

## Project Structure

```
ai-job-portal-resume-analyzer/
│
├── config/                         # Django project settings
│   ├── settings.py                 # All settings (DB, email, DRF, JWT)
│   ├── urls.py                     # Root URL configuration
│   └── wsgi.py                     # WSGI entry point
│
├── accounts/                       # Authentication & user profiles
│   ├── models.py                   # Custom User + Profile models
│   ├── views.py                    # Register, login, dashboard, profile
│   ├── forms.py                    # RegisterForm, LoginForm, ProfileForm
│   ├── urls.py                     # Web URL routes
│   ├── api_views.py                # DRF views (register, me)
│   ├── api_urls.py                 # /api/auth/ routes
│   ├── serializers.py              # UserSerializer, ProfileSerializer
│   ├── signals.py                  # Auto-create profile on user save
│   └── admin.py                    # Admin configuration
│
├── jobs/                           # Job posting module
│   ├── models.py                   # Job model
│   ├── views.py                    # List, detail, post, edit, delete
│   ├── forms.py                    # JobForm, JobSearchForm
│   ├── urls.py                     # Web URL routes
│   ├── api_views.py                # DRF ListCreate, RetrieveUpdateDestroy
│   ├── api_urls.py                 # /api/jobs/ routes
│   ├── serializers.py              # JobSerializer
│   ├── admin.py                    # Admin configuration
│   └── management/
│       └── commands/
│           └── seed_data.py        # Demo data seeder command
│
├── applications/                   # Job application module
│   ├── models.py                   # Application model (status, score)
│   ├── views.py                    # Apply, my-applications, applicants
│   ├── urls.py                     # Web URL routes
│   ├── api_views.py                # DRF views
│   ├── api_urls.py                 # /api/applications/ routes
│   ├── serializers.py              # ApplicationSerializer
│   └── admin.py                    # Admin configuration
│
├── resume_analyzer/                # AI Resume Analysis module
│   ├── utils.py                    # Core logic: extract, match, suggest
│   ├── views.py                    # Analyze view, skill gap view
│   └── urls.py                     # /resume/ routes
│
├── templates/                      # All HTML templates
│   ├── base.html                   # Master layout (navbar, footer)
│   ├── accounts/                   # Login, register, dashboard, profile
│   ├── jobs/                       # Home, list, detail, post job
│   ├── applications/               # Apply, my-applications, applicants
│   └── resume_analyzer/            # Analyze, skill-gap
│
├── static/
│   ├── css/style.css               # Custom styles + score circle
│   └── js/main.js                  # Animations, tooltips, form helpers
│
├── media/                          # Uploaded files (resumes, profile pics)
├── .env.example                    # Environment variable template
├── .gitignore
├── requirements.txt
├── render.yaml                     # Render deployment config
└── manage.py
```

---

## Database Design

### User (Custom — extends AbstractUser)
| Field    | Type       | Notes                        |
|----------|------------|------------------------------|
| email    | EmailField | Unique, used as USERNAME_FIELD|
| username | CharField  | Kept for display              |
| role     | CharField  | `job_seeker` or `recruiter`  |

### Profile (OneToOne → User)
| Field               | Type        | Notes                          |
|---------------------|-------------|--------------------------------|
| user                | OneToOne    | ForeignKey to User             |
| full_name, phone    | CharField   |                                |
| skills              | TextField   | Comma-separated                |
| resume              | FileField   | PDF upload                     |
| profile_picture     | ImageField  |                                |
| company_name        | CharField   | Recruiter only                 |
| experience_years    | IntegerField|                                |

### Job
| Field           | Type        | Notes                          |
|-----------------|-------------|--------------------------------|
| recruiter       | ForeignKey  | → User (role=recruiter)        |
| title, company  | CharField   |                                |
| required_skills | TextField   | Comma-separated                |
| employment_type | CharField   | Choices                        |
| salary_min/max  | IntegerField|                                |
| is_active       | BooleanField|                                |

### Application
| Field          | Type       | Notes                            |
|----------------|------------|----------------------------------|
| job            | ForeignKey | → Job                            |
| applicant      | ForeignKey | → User                           |
| resume_score   | FloatField | 0–100 (AI calculated)            |
| matched_skills | TextField  | Comma-separated                  |
| missing_skills | TextField  | Comma-separated                  |
| status         | CharField  | applied/reviewed/shortlisted/... |
| unique_together| Constraint | (job, applicant) — no duplicates |

---

## Resume Analyzer — How It Works

```
PDF Resume
    │
    ▼
pdfplumber.open(pdf_path)        ← extract raw text from all pages
    │
    ▼
regex keyword matching            ← scan text against 50+ known skills
    │
    ▼
extracted_skills = [python, django, sql, ...]
    │
    ▼
job.get_required_skills_list()   ← e.g. [python, django, sql, javascript]
    │
    ▼
matched  = resume_skills ∩ job_skills   = [python, django, sql]
missing  = job_skills - resume_skills   = [javascript]
    │
    ▼
score = (len(matched) / len(job_skills)) × 100  = 75.0%
    │
    ▼
get_skill_suggestions(missing)   ← return learning resource URLs
```

**Example:**

| Required Skills | Resume Skills | Matched | Missing | Score |
|-----------------|---------------|---------|---------|-------|
| Python, Django, SQL, JavaScript | Python, Django, SQL, HTML | Python, Django, SQL | JavaScript | **75%** |

---

## REST API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/token/` | Obtain JWT access + refresh token |
| POST | `/api/auth/token/refresh/` | Refresh access token |
| POST | `/api/auth/register/` | Register new user |
| GET  | `/api/auth/me/` | Authenticated user's profile |

### Jobs
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/jobs/` | List all active jobs (searchable) |
| POST | `/api/jobs/` | Create a job (recruiter only) |
| GET | `/api/jobs/<id>/` | Job detail |
| PUT/PATCH | `/api/jobs/<id>/` | Update job (owner only) |
| DELETE | `/api/jobs/<id>/` | Delete job (owner only) |

### Applications
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/applications/` | List user's applications |
| POST | `/api/applications/` | Submit an application |
| GET | `/api/applications/<id>/` | Application detail |
| PATCH | `/api/applications/<id>/` | Update status (recruiter) |

---

## Setup & Installation

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/ai-job-portal-resume-analyzer.git
cd ai-job-portal-resume-analyzer
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
# Edit .env — set SECRET_KEY, DEBUG, database settings, email settings
```

### 5. Run Migrations

```bash
python manage.py migrate
```

### 6. Create Admin Superuser

```bash
python manage.py createsuperuser
```

### 7. Seed Demo Data (Optional)

```bash
python manage.py seed_data
```

This creates 2 recruiters, 3 job seekers, and 10 realistic job postings.
All demo accounts use password: `Demo@1234`

---

## Running the Project

```bash
python manage.py runserver
```

Open: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

Admin: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## Deployment on Render

1. Push project to GitHub.
2. Create a new **Web Service** on [render.com](https://render.com/).
3. Connect your GitHub repository.
4. Render auto-detects `render.yaml`.
5. Set environment variables in Render dashboard:
   - `SECRET_KEY` (generate a strong random key)
   - `DEBUG` = `False`
   - `ALLOWED_HOSTS` = `.onrender.com`
6. Click **Deploy**.

Render will install requirements, run `collectstatic`, run `migrate`, and start with `gunicorn`.

---

## Interview Q&A

**Q: Why did you use a Custom User model instead of Django's default?**
> Django's default User uses `username` as the primary login field. I replaced it with `email` for a more professional UX. I also added a `role` field to distinguish job seekers from recruiters without a separate model or complex joins. Django documentation recommends doing this at the start of a project because migrating later is very difficult.

**Q: What is the difference between ForeignKey and OneToOneField?**
> `ForeignKey` allows many-to-one: many Applications can link to one Job, or many Jobs can link to one User (recruiter). `OneToOneField` enforces a unique constraint: each User can have exactly one Profile. Internally, `OneToOneField` is a `ForeignKey` with `unique=True`.

**Q: How do you prevent duplicate applications?**
> Two layers: (1) `unique_together = ('job', 'applicant')` in the Application model — this is a database-level constraint that raises an `IntegrityError` if violated. (2) In `apply_to_job_view`, I check with `Application.objects.filter(job=job, applicant=request.user).exists()` before creating and show a warning message. This gives the user a friendly message rather than a 500 error.

**Q: How is the match score calculated?**
> `score = (len(matched_skills) / len(required_skills)) × 100`. I normalise both sets to lowercase before comparing, then find the intersection (matched) and difference (missing) using Python set operations. This is O(n) and very fast.

**Q: How do you extract text from PDF resumes?**
> I use `pdfplumber`, which is more reliable than `PyPDF2` for text extraction, especially for multi-column layouts. I open the PDF, loop through all pages, and concatenate the text. Then I use `re.search()` with `\b` word boundaries to find skill keywords. This avoids false matches (e.g., matching 'c' inside 'catch').

**Q: Why use Django ORM instead of raw SQL?**
> ORM provides: (1) database agnosticism — I can switch from SQLite to MySQL/PostgreSQL by changing one setting; (2) security — automatic parameterised queries prevent SQL injection; (3) readability — `Application.objects.filter(status='shortlisted')` is self-documenting; (4) migrations — schema changes are tracked and reversible.

**Q: How did you implement role-based access control?**
> Each view checks `request.user.is_recruiter()` or `request.user.is_job_seeker()` (methods on the custom User model). For the REST API, I wrote a custom `IsRecruiterOrReadOnly` permission class extending DRF's `BasePermission`, checking both authentication and role in `has_permission` and `has_object_permission`.

**Q: How do email notifications work?**
> I use Django's `send_mail()` function. In development, `EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'` prints emails to the terminal — no SMTP server needed. In production (Render), I switch to `smtp.EmailBackend` with Gmail App Password credentials. I wrap all `send_mail` calls in `try/except` with `fail_silently=True` so a failed email never blocks the user's action.

---

## License

MIT License — feel free to use this project as a portfolio piece or learning reference.
