# AI Job Portal — Complete Study Guide
## From Scratch to Interview-Ready

---

## PART 1: HOW TO SET UP THE PROJECT FROM SCRATCH

### Step 1 — Install Python & check version
```bash
python --version       # Should be 3.10 or higher
```

### Step 2 — Create project folder and virtual environment
```bash
mkdir ai-job-portal-resume-analyzer
cd ai-job-portal-resume-analyzer

# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

### Step 3 — Install all dependencies
```bash
pip install -r requirements.txt
```

Key packages and WHY we need them:
| Package | Why |
|---------|-----|
| `django` | Main framework |
| `djangorestframework` | Build REST APIs |
| `rest_framework_simplejwt` | JWT token auth for APIs |
| `django-crispy-forms` | Beautiful forms with Bootstrap |
| `pdfplumber` | Extract text from PDF resumes |
| `Pillow` | Handle profile picture uploads |
| `python-decouple` | Read settings from `.env` file |
| `whitenoise` | Serve static files in production |
| `gunicorn` | Production WSGI server (Render) |

### Step 4 — Set up environment variables
```bash
cp .env.example .env
# Open .env and set your SECRET_KEY
```

### Step 5 — Run migrations (create the database tables)
```bash
python manage.py migrate
```

What this does:
- Reads all `models.py` files in every app
- Creates SQL `CREATE TABLE` statements
- Executes them on SQLite (or MySQL in production)

### Step 6 — Create admin superuser
```bash
python manage.py createsuperuser
# Enter email, username, password when prompted
```

### Step 7 — Load demo data
```bash
python manage.py seed_data
```
This runs `jobs/management/commands/seed_data.py` and creates:
- 2 recruiter accounts
- 3 job seeker accounts  
- 10 realistic job postings

All passwords: `Demo@1234`

### Step 8 — Start the server
```bash
python manage.py runserver
```
Visit http://127.0.0.1:8000

---

## PART 2: PROJECT ARCHITECTURE — HOW EVERYTHING CONNECTS

```
Browser Request
      │
      ▼
config/urls.py          ← URL Router — decides which app handles the request
      │
      ├── /              → jobs/urls.py → home_view
      ├── /accounts/     → accounts/urls.py → register, login, dashboard, profile
      ├── /jobs/         → jobs/urls.py → list, detail, post, edit, delete
      ├── /applications/ → applications/urls.py → apply, my-apps, applicants
      ├── /resume/       → resume_analyzer/urls.py → analyze, skill-gap
      └── /api/          → api_urls.py → DRF endpoints (JSON)
                │
                ▼
            View Function
            (accounts/views.py, jobs/views.py, etc.)
                │
                ├── Talks to Model (ORM query)
                ├── Calls utils (resume_analyzer/utils.py for AI logic)
                ├── Sends email if needed
                └── Renders Template (HTML) OR returns Response (JSON)
```

---

## PART 3: DEEP DIVE — EACH MODULE EXPLAINED

---

### MODULE 1: accounts — Authentication & Profiles

#### models.py

**User (Custom)**
```python
class User(AbstractUser):
    role = models.CharField(choices=ROLE_CHOICES)  # 'job_seeker' or 'recruiter'
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'   # login with email, not username
```

Why extend `AbstractUser` instead of `AbstractBaseUser`?
- `AbstractUser` gives you all default fields (username, password, is_staff, etc.)
- We just ADD the `role` field
- `AbstractBaseUser` is for when you want to build from scratch — more work, more control

**Profile (OneToOne)**
```python
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    skills = models.TextField()     # "Python, Django, SQL"
    resume = models.FileField(upload_to='resumes/')
```

`OneToOneField` vs `ForeignKey`:
- `OneToOneField` = each User has exactly 1 Profile (like a person and their passport)
- `ForeignKey` = one Job can have many Applications (one-to-many)

#### signals.py

```python
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)
```

What is a signal?
- Django's event system — when something happens (User saved), Django fires a signal
- `post_save` fires AFTER the model is saved to the database
- This ensures every new User automatically gets a Profile — we never have to remember to create it manually

#### views.py — register_view

```python
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            with transaction.atomic():     # if anything fails, rollback everything
                user = form.save()
                Profile.objects.create(user=user)
            login(request, user)           # log them in immediately
            return redirect('dashboard')
```

`transaction.atomic()` — Why?
- If `form.save()` succeeds but `Profile.objects.create()` fails, we'd have a User with no Profile
- `atomic()` wraps both in one database transaction — either both succeed or both rollback

---

### MODULE 2: jobs — Job Posting & Search

#### models.py

```python
class Job(models.Model):
    recruiter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_jobs')
    required_skills = models.TextField()   # "Python, Django, SQL"

    def get_required_skills_list(self):
        return [s.strip() for s in self.required_skills.split(',') if s.strip()]
```

`related_name='posted_jobs'` — Why?
- Lets you do `recruiter_user.posted_jobs.all()` instead of `Job.objects.filter(recruiter=user)`
- More readable, Django-idiomatic

#### views.py — job_list_view (Advanced Search)

```python
def job_list_view(request):
    jobs = Job.objects.filter(is_active=True)    # start with all active jobs

    if keyword:
        jobs = jobs.filter(
            Q(title__icontains=keyword) |
            Q(description__icontains=keyword) |
            Q(required_skills__icontains=keyword)
        )
```

`Q objects` — Why?
- Django ORM uses `AND` by default between `.filter()` arguments
- `Q` objects let you use `OR` (`|`) and `NOT` (`~`)
- `Q(title__icontains=kw) | Q(description__icontains=kw)` = SQL `WHERE title LIKE '%kw%' OR description LIKE '%kw%'`

`icontains` = case-insensitive LIKE in SQL

---

### MODULE 3: applications — Application Tracking

#### models.py

```python
class Application(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    applicant = models.ForeignKey(User, on_delete=models.CASCADE)
    resume_score = models.FloatField(default=0.0)   # AI-calculated
    status = models.CharField(choices=STATUS_CHOICES, default='applied')

    class Meta:
        unique_together = ('job', 'applicant')   # PREVENTS DUPLICATE APPLICATIONS
```

`unique_together` — The Database-Level Defence:
- Creates a SQL `UNIQUE INDEX (job_id, applicant_id)` in the database
- Even if our Python code has a bug, the database will reject duplicate insertions
- Our view code also checks first and shows a friendly message

#### views.py — apply_to_job_view

```python
def apply_to_job_view(request, job_id):
    # 1. Check duplicate
    if Application.objects.filter(job=job, applicant=request.user).exists():
        messages.warning(request, "Already applied!")
        return redirect('job_detail', job_id=job_id)

    # 2. Calculate match score using AI
    score, matched, missing = calculate_match_score(
        extracted_skills, job_skills, return_details=True
    )

    # 3. Save application with score
    application = Application.objects.create(
        job=job, applicant=request.user,
        resume_score=score,
        matched_skills=', '.join(matched),
        missing_skills=', '.join(missing),
    )

    # 4. Email recruiter
    send_mail(subject=..., message=..., recipient_list=[job.recruiter.email], fail_silently=True)
```

---

### MODULE 4: resume_analyzer — The AI Core

#### utils.py — Full Pipeline

```
PDF File
  │
  ▼  pdfplumber.open(path)
Raw Text (string)
  │
  ▼  re.search(r'\bpython\b', text)
Extracted Skills = ['python', 'django', 'sql', 'html']
  │
  ▼  set intersection
Matched = resume_skills ∩ job_required_skills
Missing = job_required_skills - resume_skills
  │
  ▼  formula
Score = (len(matched) / len(required)) * 100
  │
  ▼  resource_map lookup
Suggestions = [{'skill': 'javascript', 'url': 'https://javascript.info/'}, ...]
```

**The Match Score Formula Explained:**

```
Job requires:  Python, Django, SQL, JavaScript    (4 skills)
Resume has:    Python, Django, HTML, CSS          (4 skills, but different)

Matched = Python, Django                          (2 skills in common)
Missing = SQL, JavaScript                         (in job but not resume)

Score = 2 / 4 × 100 = 50%
```

**Why keyword matching instead of ML?**
- Simpler, fully explainable, no training data needed
- Skills are structured keywords — "Python" is "Python"
- A TF-IDF or cosine similarity approach would be overkill and harder to explain
- For a portfolio project, this demonstrates the concept clearly

---

### MODULE 5: REST APIs — Django REST Framework

#### Why DRF?
- Without DRF: you write `JsonResponse({'jobs': list(jobs.values())})` everywhere — messy
- With DRF: Serializers handle validation + serialization, ViewSets handle CRUD, Authentication is pluggable

#### JWT vs Session Authentication
| | Session | JWT |
|--|---------|-----|
| Storage | Server-side (database) | Client-side (token) |
| Stateless | No | Yes |
| Mobile-friendly | No | Yes |
| Scalable | Harder | Easy |

We support BOTH — web browser uses session, mobile/API uses JWT.

#### How to get a JWT token (test with curl or Postman)

```bash
# Get token
curl -X POST http://127.0.0.1:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"email": "seeker1@gmail.com", "password": "Demo@1234"}'

# Response
{"access": "eyJ...", "refresh": "eyJ..."}

# Use token to call API
curl http://127.0.0.1:8000/api/jobs/ \
  -H "Authorization: Bearer eyJ..."
```

---

## PART 4: TEMPLATE SYSTEM — HOW TEMPLATES WORK

All templates extend `templates/base.html`:

```html
<!-- base.html -->
<html>
  <head>...</head>
  <body>
    <nav>...</nav>
    {% block content %}{% endblock %}   ← child templates fill this
    <footer>...</footer>
  </body>
</html>
```

Child template:
```html
{% extends 'base.html' %}
{% block content %}
  <h1>My Content Here</h1>
{% endblock %}
```

Template tags used:
| Tag | What it does |
|-----|-------------|
| `{{ variable }}` | Output a variable |
| `{% if user.is_authenticated %}` | Conditional |
| `{% for job in jobs %}` | Loop |
| `{{ job.created_at\|timesince }}` | Filter — e.g., "3 days ago" |
| `{{ job.description\|truncatechars:100 }}` | Truncate text |
| `{% url 'job_detail' job.id %}` | Reverse URL lookup |
| `{% csrf_token %}` | CSRF protection in forms |
| `{% crispy form %}` | Render crispy form |

---

## PART 5: SETTINGS EXPLAINED

```python
# config/settings.py

AUTH_USER_MODEL = 'accounts.User'    # Tell Django to use our custom User

MEDIA_URL = '/media/'                # URL prefix for uploaded files
MEDIA_ROOT = BASE_DIR / 'media'     # Folder where files are stored

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # API
        'rest_framework.authentication.SessionAuthentication',          # Web
    ),
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Dev
# Change to smtp.EmailBackend for production
```

---

## PART 6: DEPLOYMENT ON RENDER — STEP BY STEP

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: AI Job Portal"
   git remote add origin https://github.com/YOUR_USERNAME/ai-job-portal-resume-analyzer.git
   git push -u origin main
   ```

2. **Go to render.com** → New → Web Service

3. **Connect GitHub** → Select your repo

4. **Render auto-reads `render.yaml`** which sets:
   - Build: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - Start: `gunicorn config.wsgi:application`

5. **Set environment variables** in Render dashboard:
   - `SECRET_KEY` = (generate at https://djecrety.ir/)
   - `DEBUG` = `False`
   - `ALLOWED_HOSTS` = `.onrender.com`

6. **Click Deploy** — Render builds and deploys in ~3 minutes

Why `gunicorn`?
- Django's built-in `runserver` is single-threaded, for development only
- Gunicorn is a production-grade WSGI server that handles multiple concurrent requests

Why `whitenoise`?
- In production, Django doesn't serve static files (CSS/JS/images)
- WhiteNoise middleware adds that capability efficiently, with compression and caching headers

---

## PART 7: COMMON INTERVIEW QUESTIONS — WITH FULL ANSWERS

---

**Q1: Walk me through how a candidate applies for a job in your system.**

1. Candidate logs in → goes to Job List → clicks "View Details"
2. On job detail page, sees match score preview (calculated from profile skills vs job skills)
3. Clicks "Apply Now" → taken to `apply_to_job_view`
4. View checks: (a) user is a job seeker, (b) job is active, (c) no duplicate application
5. Extracts skills from resume PDF using `pdfplumber` → runs `calculate_match_score()`
6. Shows apply form with pre-calculated score and matched/missing skills
7. Candidate writes cover letter → submits form
8. Application saved to DB with score, matched skills, missing skills
9. `send_mail()` sends email to recruiter: "New application for {job_title}, match score: {score}%"
10. Candidate redirected to application detail page with success message

---

**Q2: How does the recruiter see and manage applicants?**

1. Recruiter logs in → Dashboard shows posted jobs with applicant counts
2. Clicks "View Applicants" for a job → `job_applicants_view`
3. All applications for that job are fetched, ordered by `-resume_score` (highest first)
4. Each applicant card shows: name, email, match score bar, matched/missing skills, resume PDF link
5. Recruiter selects new status from dropdown → submits form → `update_application_status_view`
6. Status is updated in DB, `send_mail()` notifies candidate of the change

---

**Q3: Explain the database relationships in your project.**

```
User (1) ←──────── (1) Profile     [OneToOne]
User (1) ←──────── (N) Job         [ForeignKey: recruiter]
Job  (1) ←──────── (N) Application [ForeignKey: job]
User (1) ←──────── (N) Application [ForeignKey: applicant]
```

A User who is a recruiter can post many Jobs. Each Job can receive many Applications. Each Application links one Job to one Applicant (User), and the `unique_together` constraint ensures one applicant can't apply to the same job twice.

---

**Q4: What security measures did you implement?**

- **CSRF protection**: All POST forms include `{% csrf_token %}` — Django rejects requests without valid CSRF tokens
- **Authentication gates**: `@login_required` decorator on all views that need a logged-in user
- **Role checks**: Every recruiter-only view checks `request.user.is_recruiter()` before proceeding
- **Object-level permissions**: Edit/delete job views check `job.recruiter == request.user` — you can't edit someone else's job
- **SQL injection prevention**: All DB queries use ORM — Django auto-parameterises all values
- **Password hashing**: Django uses PBKDF2 with SHA256 by default — passwords are never stored in plain text
- **Secret key**: Loaded from `.env` via `python-decouple`, never hardcoded
- **`.gitignore`**: Excludes `.env`, `db.sqlite3`, `media/` from version control

---

**Q5: How would you scale this for 100,000 users?**

- Switch from SQLite to PostgreSQL (better concurrency, indexing)
- Add database indexes on frequently filtered columns: `Job.created_at`, `Application.status`
- Use Redis for caching job listings (jobs don't change every second)
- Use Celery + Redis for async email sending (don't block HTTP response)
- Deploy behind a load balancer with multiple gunicorn workers
- Use S3 (or similar) for media file storage instead of local disk
- Add rate limiting on API endpoints

---

## PART 8: HOW TO EXPLAIN THE PROJECT IN AN INTERVIEW (SCREEN SHARE)

### Opening (30 seconds)
> "This is an AI-powered job portal built with Django. It has two user roles — job seekers and recruiters. The main feature is an AI resume analyzer that extracts skills from a PDF resume and calculates a match score against job requirements. Let me show you the code structure first."

### Show GitHub Structure (1 minute)
> "The project is divided into 4 Django apps: `accounts` for auth and profiles, `jobs` for job posting, `applications` for the apply flow, and `resume_analyzer` which is the AI core. There's also a `config` folder for project-level settings and URLs."

### Show the AI Core — utils.py (2 minutes)
> "Here in `resume_analyzer/utils.py` is the most interesting part. `extract_text_from_pdf` uses pdfplumber to read the PDF. `extract_skills_from_resume` scans the text with regex word-boundary matching against our skills database. `calculate_match_score` uses Python set operations — intersection for matched skills, difference for missing. The score is matched divided by required, times 100."

### Show the Model Design — models.py (1 minute)
> "The key design decision here is the `unique_together` constraint on Application — this prevents duplicate applications at the database level. And you can see the `resume_score`, `matched_skills`, and `missing_skills` fields stored on every application, so recruiters can sort and filter by AI score."

### Show the REST API (1 minute)
> "For the REST API, I used Django REST Framework with JWT authentication. You can POST to `/api/auth/token/` to get a JWT, then include it as a Bearer token on API calls. The `IsRecruiterOrReadOnly` custom permission class ensures only recruiters can create or modify jobs."

### Close (30 seconds)
> "The project is deployed on Render with gunicorn and WhiteNoise for static files. All settings are environment-variable driven via python-decouple, so there are no secrets in the code. I've also included a seed_data management command to populate it with demo data in one command."
