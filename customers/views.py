from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    TemplateView
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone
from .models import AssemblyRequest, RequestComponent
from .forms import AssemblyRequestForm, RequestComponentForm

class CustomerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and not self.request.user.profile.is_assembler

class DashboardView(CustomerRequiredMixin, TemplateView):
    template_name = 'customers/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_requests'] = AssemblyRequest.objects.filter(
            customer=self.request.user
        ).order_by('-created_at')[:5]
        context['pending_requests'] = AssemblyRequest.objects.filter(
            customer=self.request.user,
            status__in=['pending', 'approved', 'in_progress']
        ).count()
        context['completed_requests'] = AssemblyRequest.objects.filter(
            customer=self.request.user,
            status='completed'
        ).count()
        return context

class AssemblyRequestListView(CustomerRequiredMixin, ListView):
    model = AssemblyRequest
    template_name = 'customers/request_list.html'
    context_object_name = 'requests'
    paginate_by = 10

    def get_queryset(self):
        return AssemblyRequest.objects.filter(
            customer=self.request.user
        ).order_by('-created_at')

class AssemblyRequestDetailView(CustomerRequiredMixin, DetailView):
    model = AssemblyRequest
    template_name = 'customers/request_detail.html'
    context_object_name = 'request'

    def get_queryset(self):
        return AssemblyRequest.objects.filter(customer=self.request.user)

class AssemblyRequestCreateView(CustomerRequiredMixin, CreateView):
    model = AssemblyRequest
    form_class = AssemblyRequestForm
    template_name = 'customers/request_form.html'
    success_url = reverse_lazy('customer:request_list')

    def form_valid(self, form):
        form.instance.customer = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Assembly request created successfully!')
        return response

class AssemblyRequestUpdateView(CustomerRequiredMixin, UpdateView):
    model = AssemblyRequest
    form_class = AssemblyRequestForm
    template_name = 'customers/request_form.html'
    success_url = reverse_lazy('customer:request_list')

    def get_queryset(self):
        return AssemblyRequest.objects.filter(
            customer=self.request.user,
            status='pending'
        )

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Assembly request updated successfully!')
        return response

class AssemblyRequestCancelView(CustomerRequiredMixin, UpdateView):
    model = AssemblyRequest
    template_name = 'customers/request_cancel.html'
    success_url = reverse_lazy('customer:request_list')
    fields = []

    def get_queryset(self):
        return AssemblyRequest.objects.filter(
            customer=self.request.user,
            status__in=['pending', 'approved']
        )

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.status = 'cancelled'
        self.object.save()
        messages.success(self.request, 'Assembly request cancelled successfully!')
        return redirect(self.get_success_url())
