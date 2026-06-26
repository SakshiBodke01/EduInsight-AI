from django import forms
from django.contrib.auth.forms import UserCreationForm
from portal.models import User, StudentProfile, Result, Subject

class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Email Address'}))
    role = forms.ChoiceField(choices=User.ROLE_CHOICES[1:], widget=forms.Select(attrs={'class': 'form-select'}))
    
    # Extra fields for student profile setup (only needed if role is student)
    roll_number = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'placeholder': 'Roll Number (Students only)'}))
    class_name = forms.CharField(max_length=50, required=False, initial='Class A', widget=forms.TextInput(attrs={'placeholder': 'Class/Grade (Students only)'}))
    department = forms.CharField(max_length=50, required=False, initial='Data Science', widget=forms.TextInput(attrs={'placeholder': 'Department/Major (Students only)'}))
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email', 'role')

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        roll_number = cleaned_data.get('roll_number')
        
        # If student, require roll number
        if role == 'student' and not roll_number:
            self.add_error('roll_number', 'Roll number is required for students.')
            
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.role = self.cleaned_data['role']
        
        if commit:
            user.save()
            if user.role == 'student':
                profile, created = StudentProfile.objects.get_or_create(user=user)
                profile.roll_number = self.cleaned_data.get('roll_number')
                profile.class_name = self.cleaned_data.get('class_name') or 'Class A'
                profile.department = self.cleaned_data.get('department') or 'Data Science'
                profile.save()
        return user

class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        label='Select CSV/Excel File',
        help_text='Supported formats: .csv, .xlsx',
        widget=forms.FileInput(attrs={'accept': '.csv, .xlsx', 'class': 'form-control'})
    )
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text='Select the subject for which you are uploading the marks.'
    )

class ResultForm(forms.ModelForm):
    student = forms.ModelChoiceField(
        queryset=StudentProfile.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    subject = models_subject = forms.ModelChoiceField(
        queryset=Subject.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = Result
        fields = ['student', 'subject', 'attendance_percentage', 'study_hours', 'mid_term_marks', 'assignment_marks']
        widgets = {
            'attendance_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '0', 'max': '100'}),
            'study_hours': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '0', 'max': '168'}),
            'mid_term_marks': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '0', 'max': '100'}),
            'assignment_marks': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '0', 'max': '100'}),
        }
