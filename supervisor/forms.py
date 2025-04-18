from django import forms
from django.utils import timezone
from .models import Component, ComponentType, Brand, ComponentModel
from core.models import SystemAnnouncement

class ComponentForm(forms.ModelForm):
    specifications = forms.JSONField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        'rows': 4
    }))

    class Meta:
        model = Component
        fields = [
            'type',
            'brand',
            'model',
            'name',
            'description',
            'specifications',
            'price',
            'stock',
            'is_active'
        ]
        widgets = {
            'type': forms.Select(attrs={'class': 'form-control'}),
            'brand': forms.Select(attrs={'class': 'form-control'}),
            'model': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01'
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price < 0:
            raise forms.ValidationError("Price cannot be negative.")
        return price

    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        if stock < 0:
            raise forms.ValidationError("Stock cannot be negative.")
        return stock

class ComponentTypeForm(forms.ModelForm):
    class Meta:
        model = ComponentType
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            })
        }

class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['name', 'description', 'website']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'website': forms.URLInput(attrs={'class': 'form-control'})
        }

class ComponentModelForm(forms.ModelForm):
    class Meta:
        model = ComponentModel
        fields = ['name', 'brand', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'brand': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            })
        }

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = SystemAnnouncement
        fields = ['title', 'message', 'priority', 'start_date', 'end_date', 'active']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm',
                'placeholder': 'Enter announcement title'
            }),
            'message': forms.Textarea(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm',
                'rows': 4,
                'placeholder': 'Enter announcement message'
            }),
            'priority': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm'
            }),
            'start_date': forms.DateTimeInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm',
                'type': 'datetime-local'
            }),
            'end_date': forms.DateTimeInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm',
                'type': 'datetime-local'
            }),
            'active': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500'
            })
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            if start_date > end_date:
                raise forms.ValidationError("End date must be after start date.")
            if start_date < timezone.now() and not self.instance.pk:
                raise forms.ValidationError("Start date cannot be in the past for new announcements.")

        return cleaned_data

class ComponentFilterForm(forms.Form):
    type = forms.ModelChoiceField(
        queryset=ComponentType.objects.all(),
        required=False,
        empty_label="All Types",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    brand = forms.ModelChoiceField(
        queryset=Brand.objects.all(),
        required=False,
        empty_label="All Brands",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    STOCK_CHOICES = [
        ('', 'All'),
        ('low', 'Low Stock (≤10)'),
        ('out', 'Out of Stock')
    ]
    
    stock_status = forms.ChoiceField(
        choices=STOCK_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class AssemblerFilterForm(forms.Form):
    STATUS_CHOICES = [
        ('', 'All'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('pending', 'Pending Approval')
    ]
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    experience = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Minimum years of experience'
        })
    )
