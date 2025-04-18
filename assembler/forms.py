from django import forms
from django.utils import timezone
from .models import AssemblyTask, TaskCheckpoint, IssueReport
from accounts.models import UserProfile

class TaskUpdateForm(forms.ModelForm):
    class Meta:
        model = AssemblyTask
        fields = ['notes', 'expected_completion']
        widgets = {
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Add any notes about the task...'
            }),
            'expected_completion': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            })
        }

    def clean_expected_completion(self):
        expected_completion = self.cleaned_data.get('expected_completion')
        if expected_completion and expected_completion < timezone.now():
            raise forms.ValidationError("Expected completion date must be in the future.")
        return expected_completion

class CheckpointForm(forms.ModelForm):
    class Meta:
        model = TaskCheckpoint
        fields = ['description', 'notes']
        widgets = {
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Checkpoint description'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional notes...'
            })
        }

class IssueReportForm(forms.ModelForm):
    class Meta:
        model = IssueReport
        fields = ['title', 'description', 'priority']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Issue title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the issue in detail...'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-control'
            })
        }

class AssemblerProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'phone',
            'mobile',
            'address',
            'profile_image'
        ]
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone number'
            }),
            'mobile': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Mobile number'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Your address'
            }),
            'profile_image': forms.FileInput(attrs={
                'class': 'form-control'
            })
        }

class AvailabilityForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['is_available']
        widgets = {
            'is_available': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

class TaskFilterForm(forms.Form):
    STATUS_CHOICES = [('', 'All')] + list(AssemblyTask.STATUS_CHOICES)
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')

        if date_from and date_to and date_from > date_to:
            raise forms.ValidationError("Start date must be before end date.")

        return cleaned_data

class IssueFilterForm(forms.Form):
    PRIORITY_CHOICES = [('', 'All')] + list(IssueReport.PRIORITY_CHOICES)
    STATUS_CHOICES = [
        ('', 'All'),
        ('open', 'Open'),
        ('resolved', 'Resolved')
    ]
    
    priority = forms.ChoiceField(
        choices=PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')

        if date_from and date_to and date_from > date_to:
            raise forms.ValidationError("Start date must be before end date.")

        return cleaned_data
