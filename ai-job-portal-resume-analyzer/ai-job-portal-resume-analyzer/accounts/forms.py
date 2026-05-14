from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field
from .models import User, Profile


class RegisterForm(UserCreationForm):
    """User registration form with role selection."""
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Enter your email'}))
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        widget=forms.RadioSelect,
        label="I am a"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('username', placeholder='Choose a username'),
            Field('email', placeholder='Enter email address'),
            'role',
            Field('password1', placeholder='Create password'),
            Field('password2', placeholder='Confirm password'),
            Submit('submit', 'Create Account', css_class='btn btn-primary w-100 mt-3'),
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.role = self.cleaned_data['role']
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    """Custom login form using email."""
    username = forms.EmailField(
        label='Email Address',
        widget=forms.EmailInput(attrs={'autofocus': True, 'placeholder': 'Enter your email'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('username', placeholder='Email address'),
            Field('password', placeholder='Password'),
            Submit('submit', 'Login', css_class='btn btn-primary w-100 mt-3'),
        )


class JobSeekerProfileForm(forms.ModelForm):
    """Profile edit form for job seekers."""
    class Meta:
        model = Profile
        fields = [
            'full_name', 'phone', 'bio', 'location',
            'profile_picture', 'skills', 'resume',
            'linkedin_url', 'github_url', 'experience_years'
        ]
        widgets = {
            'skills': forms.TextInput(attrs={'placeholder': 'Python, Django, SQL, JavaScript'}),
            'bio': forms.Textarea(attrs={'rows': 4}),
        }
        help_texts = {
            'skills': 'Enter skills separated by commas.',
            'resume': 'Upload your resume in PDF format.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('full_name', css_class='col-md-6'),
                Column('phone', css_class='col-md-6'),
            ),
            Row(
                Column('location', css_class='col-md-6'),
                Column('experience_years', css_class='col-md-6'),
            ),
            'bio',
            'skills',
            Row(
                Column('linkedin_url', css_class='col-md-6'),
                Column('github_url', css_class='col-md-6'),
            ),
            'profile_picture',
            'resume',
            Submit('submit', 'Save Profile', css_class='btn btn-success mt-3'),
        )


class RecruiterProfileForm(forms.ModelForm):
    """Profile edit form for recruiters."""
    class Meta:
        model = Profile
        fields = [
            'full_name', 'phone', 'location',
            'company_name', 'company_website', 'company_description',
            'profile_picture'
        ]
        widgets = {
            'company_description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('full_name', css_class='col-md-6'),
                Column('phone', css_class='col-md-6'),
            ),
            Row(
                Column('company_name', css_class='col-md-6'),
                Column('company_website', css_class='col-md-6'),
            ),
            'location',
            'company_description',
            'profile_picture',
            Submit('submit', 'Save Profile', css_class='btn btn-success mt-3'),
        )
