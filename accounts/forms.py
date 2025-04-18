from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import UserProfile, RegistrationRequest

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm',
        'placeholder': 'Enter your username',
        'autocomplete': 'username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm',
        'placeholder': 'Enter your password',
        'autocomplete': 'current-password'
    }))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Username'
        self.fields['password'].label = 'Password'

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    address = forms.CharField(widget=forms.Textarea)
    phone = forms.CharField(max_length=20)
    mobile = forms.CharField(max_length=20)
    user_type = forms.ChoiceField(choices=UserProfile.USER_TYPE_CHOICES)
    profile_image = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name', 'password1',
            'password2', 'address', 'phone', 'mobile', 'user_type', 'profile_image'
        ]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            
            # Create registration request
            RegistrationRequest.objects.create(
                user=user,
                user_type=self.cleaned_data['user_type'],
                address=self.cleaned_data['address'],
                phone=self.cleaned_data['phone'],
                mobile=self.cleaned_data['mobile'],
                profile_image=self.cleaned_data.get('profile_image')
            )
            
            # Update user profile
            profile = user.profile
            profile.user_type = self.cleaned_data['user_type']
            profile.address = self.cleaned_data['address']
            profile.phone = self.cleaned_data['phone']
            profile.mobile = self.cleaned_data['mobile']
            if self.cleaned_data.get('profile_image'):
                profile.profile_image = self.cleaned_data['profile_image']
            profile.save()
        
        return user

class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = UserProfile
        fields = ['address', 'phone', 'mobile', 'profile_image']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            # Update user info
            user = profile.user
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            user.save()
            
            profile.save()
        return profile

class NotificationPreferenceForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['email_notifications', 'browser_notifications', 'notification_frequency']
        widgets = {
            'email_notifications': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500'
            }),
            'browser_notifications': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500'
            }),
            'notification_frequency': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email_notifications'].help_text = 'Receive notifications via email'
        self.fields['browser_notifications'].help_text = 'Receive notifications in browser'
        self.fields['notification_frequency'].help_text = 'How often would you like to receive notification digests?'
