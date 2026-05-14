"""
resume_analyzer/utils.py
========================
Core logic for the Resume Analyzer module.

Functions:
    extract_text_from_pdf    — Extract raw text from a PDF resume using pdfplumber
    extract_skills_from_resume — Identify skills from raw text using keyword matching
    calculate_match_score    — Compare resume skills with job requirements, return score + details
    get_skill_suggestions    — Suggest learning resources for missing skills
"""

import re
import pdfplumber


# Master skills dictionary — categorized for richer analysis
SKILLS_DATABASE = {
    'Programming Languages': [
        'python', 'java', 'javascript', 'typescript', 'c', 'c++', 'c#', 'go', 'rust',
        'ruby', 'php', 'swift', 'kotlin', 'scala', 'r', 'matlab', 'perl', 'dart',
    ],
    'Web Frameworks': [
        'django', 'flask', 'fastapi', 'react', 'angular', 'vue', 'nextjs', 'nuxtjs',
        'express', 'spring', 'laravel', 'rails', 'asp.net', 'svelte',
    ],
    'Databases': [
        'sql', 'mysql', 'postgresql', 'sqlite', 'mongodb', 'redis', 'elasticsearch',
        'cassandra', 'dynamodb', 'firebase', 'oracle', 'mssql',
    ],
    'Cloud & DevOps': [
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'ansible',
        'jenkins', 'github actions', 'ci/cd', 'linux', 'nginx', 'apache',
    ],
    'Data & ML': [
        'machine learning', 'deep learning', 'nlp', 'computer vision', 'tensorflow',
        'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy', 'matplotlib',
        'data analysis', 'data science', 'tableau', 'power bi',
    ],
    'Tools & Others': [
        'git', 'github', 'gitlab', 'jira', 'agile', 'scrum', 'rest api', 'graphql',
        'html', 'css', 'bootstrap', 'tailwind', 'jquery', 'postman', 'figma',
        'celery', 'rabbitmq', 'websocket', 'oauth', 'jwt',
    ],
}

# Flat list of all known skills (lowercase)
ALL_SKILLS = [skill for skills in SKILLS_DATABASE.values() for skill in skills]


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract all text from a PDF file using pdfplumber.

    Args:
        pdf_path: Absolute path to the PDF file.

    Returns:
        Extracted text as a single string. Returns empty string on failure.
    """
    text = ''
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + '\n'
    except Exception as e:
        print(f"[ResumeAnalyzer] PDF extraction error: {e}")
    return text


def extract_skills_from_resume(pdf_path: str) -> list:
    """
    Extract skills from a resume PDF.
    Uses keyword matching against the master skills database.

    Args:
        pdf_path: Path to the resume PDF.

    Returns:
        List of detected skill strings.
    """
    raw_text = extract_text_from_pdf(pdf_path).lower()

    # Remove punctuation except commas/slashes (common in skill lists)
    raw_text = re.sub(r'[^\w\s,/+#.]', ' ', raw_text)

    detected_skills = []
    for skill in ALL_SKILLS:
        # Match whole words (avoid matching 'c' inside 'catch' for example)
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, raw_text):
            detected_skills.append(skill)

    return list(set(detected_skills))  # deduplicate


def calculate_match_score(
    resume_skills: list,
    job_skills: list,
    return_details: bool = False
):
    """
    Calculate how well a candidate's skills match job requirements.

    Formula:
        score = (matched_skills / total_required_skills) * 100

    Args:
        resume_skills:  List of skills from the candidate's resume.
        job_skills:     List of required skills from the job posting.
        return_details: If True, returns (score, matched, missing) tuple.

    Returns:
        float — match score (0.0–100.0) if return_details is False
        tuple — (score, matched_list, missing_list) if return_details is True
    """
    if not job_skills:
        return (0.0, [], []) if return_details else 0.0

    # Normalize to lowercase for comparison
    resume_set = {s.lower().strip() for s in resume_skills}
    job_set = {s.lower().strip() for s in job_skills}

    matched = list(resume_set & job_set)
    missing = list(job_set - resume_set)

    score = round((len(matched) / len(job_set)) * 100, 1)

    if return_details:
        return score, matched, missing
    return score


def get_skill_category(skill: str) -> str:
    """Return the category of a skill."""
    skill_lower = skill.lower()
    for category, skills in SKILLS_DATABASE.items():
        if skill_lower in skills:
            return category
    return 'Other'


def get_skill_suggestions(missing_skills: list) -> list:
    """
    Return learning resource suggestions for missing skills.

    Args:
        missing_skills: List of skill names the candidate is missing.

    Returns:
        List of dicts with skill name, category, and resource URL.
    """
    suggestions = []
    resource_map = {
        'python': 'https://docs.python.org/3/tutorial/',
        'django': 'https://docs.djangoproject.com/en/5.0/intro/',
        'sql': 'https://www.w3schools.com/sql/',
        'javascript': 'https://javascript.info/',
        'react': 'https://react.dev/learn',
        'docker': 'https://docs.docker.com/get-started/',
        'aws': 'https://aws.amazon.com/training/',
        'git': 'https://git-scm.com/book/en/v2',
        'machine learning': 'https://www.coursera.org/learn/machine-learning',
        'postgresql': 'https://www.postgresql.org/docs/current/tutorial.html',
        'rest api': 'https://restfulapi.net/',
    }

    for skill in missing_skills:
        skill_lower = skill.lower()
        suggestions.append({
            'skill': skill,
            'category': get_skill_category(skill),
            'resource_url': resource_map.get(skill_lower, f'https://www.google.com/search?q=learn+{skill_lower}'),
        })

    return suggestions


def analyze_resume_for_job(pdf_path: str, job_required_skills: list) -> dict:
    """
    Full pipeline: extract → match → suggestions.

    Args:
        pdf_path:             Path to resume PDF.
        job_required_skills:  Required skills from the job.

    Returns:
        dict with keys: extracted_skills, score, matched, missing, suggestions
    """
    extracted = extract_skills_from_resume(pdf_path)
    score, matched, missing = calculate_match_score(extracted, job_required_skills, return_details=True)
    suggestions = get_skill_suggestions(missing)

    return {
        'extracted_skills': extracted,
        'score': score,
        'matched_skills': matched,
        'missing_skills': missing,
        'skill_suggestions': suggestions,
        'total_required': len(job_required_skills),
        'total_matched': len(matched),
    }
