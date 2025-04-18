from django.views.generic import CreateView, UpdateView, DetailView, TemplateView
from django.contrib.auth.views import LoginView as AuthLoginView, LogoutView as AuthLogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import PasswordChangeForm
from django.urls import reverse_lazy
from django.contrib import messages
from .models import UserProfile, RegistrationRequest
from .forms import (
    UserRegistrationForm,
    UserProfileForm,
    NotificationPreferenceForm,
    LoginForm,
)

class LoginView(AuthLoginView):
    template_name = 'accounts/login.html'
    form_class = LoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        if self.request.user.is_staff:
            return reverse_lazy('supervisor:dashboard')
        elif hasattr(self.request.user, 'profile'):
            if self.request.user.profile.is_assembler:
                return reverse_lazy('assembler:dashboard')
            else:
                return reverse_lazy('customer:dashboard')
        return reverse_lazy('core:home')

class LogoutView(AuthLogoutView):
    next_page = 'core:home'

class RegisterView(CreateView):
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            'Registration successful! Please wait for admin approval.'
        )
        return response

class ProfileView(LoginRequiredMixin, DetailView):
    model = UserProfile
    template_name = 'accounts/profile.html'
    context_object_name = 'profile'

    def get_object(self):
        return self.request.user.profile

class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self):
        return self.request.user.profile

    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)

class ChangePasswordView(LoginRequiredMixin, UpdateView):
    form_class = PasswordChangeForm
    template_name = 'accounts/change_password.html'
    success_url = reverse_lazy('accounts:profile')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Password changed successfully!')
        return super().form_valid(form)

class NotificationPreferencesView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = NotificationPreferenceForm
    template_name = 'accounts/notification_preferences.html'
    success_url = reverse_lazy('accounts:notification_preferences')

    def get_object(self):
        return self.request.user.profile

    def form_valid(self, form):
        messages.success(self.request, 'Notification preferences updated successfully!')
        return super().form_valid(form)
