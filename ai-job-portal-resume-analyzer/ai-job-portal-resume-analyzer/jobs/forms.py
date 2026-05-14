from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Field
from .models import Job


class JobForm(forms.ModelForm):
    """Form for recruiters to post or edit a job."""
    class Meta:
        model = Job
        fields = [
            'title', 'company', 'location', 'description',
            'required_skills', 'salary_min', 'salary_max',
            'employment_type', 'experience_level', 'deadline', 'is_active'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 6}),
            'required_skills': forms.TextInput(attrs={'placeholder': 'Python, Django, SQL, REST APIs'}),
            'deadline': forms.DateInput(attrs={'type': 'date'}),
        }
        help_texts = {
            'required_skills': 'Enter skills separated by commas.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('title', css_class='col-md-8'),
                Column('employment_type', css_class='col-md-4'),
            ),
            Row(
                Column('company', css_class='col-md-6'),
                Column('location', css_class='col-md-6'),
            ),
            'description',
            'required_skills',
            Row(
                Column('salary_min', css_class='col-md-4'),
                Column('salary_max', css_class='col-md-4'),
                Column('experience_level', css_class='col-md-4'),
            ),
            Row(
                Column('deadline', css_class='col-md-6'),
                Column('is_active', css_class='col-md-6 mt-4'),
            ),
            Submit('submit', 'Post Job', css_class='btn btn-primary mt-3'),
        )


class JobSearchForm(forms.Form):
    """Search and filter form for job listings."""
    keyword = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Job title, skills, company...'})
    )
    location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'City or Remote'})
    )
    employment_type = forms.ChoiceField(
        required=False,
        choices=[('', 'All Types')] + list(Job.EMPLOYMENT_TYPE_CHOICES)
    )
    experience_level = forms.ChoiceField(
        required=False,
        choices=[('', 'All Levels')] + list(Job.EXPERIENCE_LEVEL_CHOICES)
    )
