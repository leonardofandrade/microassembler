from django import forms
from django.utils import timezone
from .models import AssemblyRequest, RequestComponent

class AssemblyRequestForm(forms.ModelForm):
    class Meta:
        model = AssemblyRequest
        fields = ['deadline', 'observations', 'quantity']
        widgets = {
            'deadline': forms.DateTimeInput(
                attrs={
                    'class': 'form-control',
                    'type': 'datetime-local'
                }
            ),
            'observations': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': 'Any special requirements or notes...'
                }
            ),
            'quantity': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': 1
                }
            )
        }

    def clean_deadline(self):
        deadline = self.cleaned_data.get('deadline')
        if deadline and deadline < timezone.now():
            raise forms.ValidationError("Deadline must be in the future.")
        return deadline

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity < 1:
            raise forms.ValidationError("Quantity must be at least 1.")
        return quantity

class RequestComponentForm(forms.ModelForm):
    class Meta:
        model = RequestComponent
        fields = ['component', 'quantity']
        widgets = {
            'component': forms.Select(
                attrs={
                    'class': 'form-control'
                }
            ),
            'quantity': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': 1
                }
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active components with stock available
        self.fields['component'].queryset = self.fields['component'].queryset.filter(
            is_active=True,
            stock__gt=0
        )

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        component = self.cleaned_data.get('component')
        
        if not component:
            return quantity
            
        if quantity > component.stock:
            raise forms.ValidationError(
                f"Not enough stock. Available: {component.stock}"
            )
        
        return quantity

class RequestFilterForm(forms.Form):
    STATUS_CHOICES = [('', 'All')] + list(AssemblyRequest.STATUS_CHOICES)
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
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
