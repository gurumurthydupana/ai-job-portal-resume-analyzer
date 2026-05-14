# REST API Reference — AI Job Portal

Base URL (local): `http://127.0.0.1:8000`

---

## Authentication

All protected endpoints require: `Authorization: Bearer <access_token>`

### POST `/api/auth/token/`
Obtain JWT tokens.
```json
Request:  { "email": "user@example.com", "password": "password123" }
Response: { "access": "eyJ...", "refresh": "eyJ..." }
```

### POST `/api/auth/token/refresh/`
Refresh access token.
```json
Request:  { "refresh": "eyJ..." }
Response: { "access": "eyJ..." }
```

### POST `/api/auth/register/`
Register new user.
```json
Request:  { "username": "johndoe", "email": "john@example.com", "password": "pass123", "password2": "pass123", "role": "job_seeker" }
Response: { "id": 1, "username": "johndoe", "email": "john@example.com", "role": "job_seeker" }
```

### GET `/api/auth/me/`
Get current user profile. **Auth required.**
```json
Response: {
  "user": { "id": 1, "email": "john@example.com", "role": "job_seeker" },
  "profile": { "full_name": "John Doe", "skills": "Python, Django", "experience_years": 2 }
}
```

---

## Jobs

### GET `/api/jobs/`
List all active jobs. Supports `?search=python` query param.
```json
Response: {
  "count": 10,
  "results": [
    {
      "id": 1,
      "title": "Senior Django Developer",
      "company": "TechCorp",
      "location": "Bangalore",
      "required_skills": "Python, Django, SQL",
      "required_skills_list": ["Python", "Django", "SQL"],
      "salary_display": "₹12,00,000 – ₹18,00,000 per year",
      "employment_type": "full_time",
      "total_applications": 5,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### POST `/api/jobs/`
Create job. **Recruiter auth required.**
```json
Request: {
  "title": "Backend Developer",
  "company": "MyCompany",
  "location": "Remote",
  "description": "We need a Django expert...",
  "required_skills": "Python, Django, PostgreSQL",
  "employment_type": "full_time",
  "experience_level": "mid"
}
```

### GET `/api/jobs/<id>/`
Job detail with full description and total applications.

### PUT `/api/jobs/<id>/`
Update job. **Owner recruiter only.**

### DELETE `/api/jobs/<id>/`
Delete job. **Owner recruiter only.**

---

## Applications

### GET `/api/applications/`
List applications. Job seekers see their own; recruiters see applications for their jobs. **Auth required.**

### POST `/api/applications/`
Submit application. **Job seeker auth required.**
```json
Request:  { "job_id": 1, "cover_letter": "I am excited about this role..." }
Response: { "id": 1, "job": {...}, "resume_score": 75.0, "status": "applied" }
```

### GET `/api/applications/<id>/`
Application detail. **Auth required (applicant or job's recruiter).**

### PATCH `/api/applications/<id>/`
Update status. **Recruiter auth required.**
```json
Request:  { "status": "shortlisted" }
```
