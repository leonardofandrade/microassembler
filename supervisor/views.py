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
from django.db.models import Count, Q, F
from .models import Component, ComponentType, Brand, ComponentModel, ComponentCompatibility
from customers.models import AssemblyRequest
from accounts.models import UserProfile, RegistrationRequest
from core.models import SystemAnnouncement
from .forms import (
    ComponentForm,
    ComponentTypeForm,
    BrandForm,
    ComponentModelForm,
    AnnouncementForm
)

class SupervisorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff

class DashboardView(SupervisorRequiredMixin, TemplateView):
    template_name = 'supervisor/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Assembly Requests Statistics
        context['pending_requests'] = AssemblyRequest.objects.filter(status='pending').count()
        context['in_progress_requests'] = AssemblyRequest.objects.filter(status='in_progress').count()
        context['completed_requests'] = AssemblyRequest.objects.filter(status='completed').count()
        
        # Component Statistics
        context['low_stock_components'] = Component.objects.filter(
            stock__lte=F('stock_threshold'),
            is_active=True
        ).order_by('stock')[:5]
        
        # Assembler Statistics
        context['active_assemblers'] = UserProfile.objects.filter(
            user_type='assembler',
            is_approved=True
        ).count()
        
        # Registration Requests
        context['pending_registrations'] = RegistrationRequest.objects.filter(
            status='pending'
        ).count()
        
        return context


# Component Management Views
class ComponentListView(SupervisorRequiredMixin, ListView):
    model = Component
    template_name = 'supervisor/component_list.html'
    context_object_name = 'components'
    paginate_by = 10

    def get_queryset(self):
        queryset = Component.objects.all()
        
        # Apply filters if provided
        type_id = self.request.GET.get('type')
        brand_id = self.request.GET.get('brand')
        stock_status = self.request.GET.get('stock_status')
        
        if type_id:
            queryset = queryset.filter(type_id=type_id)
        if brand_id:
            queryset = queryset.filter(brand_id=brand_id)
        if stock_status == 'low':
            queryset = queryset.filter(stock__lte=F('stock_threshold'))
        elif stock_status == 'out':
            queryset = queryset.filter(stock=0)
        
        return queryset.order_by('type__name', 'brand__name', 'name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['low_stock_components'] = Component.objects.filter(
            stock__lte=F('stock_threshold')
        )
        return context

class ComponentDetailView(SupervisorRequiredMixin, DetailView):
    model = Component
    template_name = 'supervisor/component_detail.html'
    context_object_name = 'component'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        component = self.get_object()
        context['compatibilities'] = ComponentCompatibility.objects.filter(
            Q(component=component) | Q(compatible_with=component)
        )
        return context

class ComponentCreateView(SupervisorRequiredMixin, CreateView):
    model = Component
    form_class = ComponentForm
    template_name = 'supervisor/component_form.html'
    success_url = reverse_lazy('supervisor:component_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Component created successfully!')
        return response

class ComponentUpdateView(SupervisorRequiredMixin, UpdateView):
    model = Component
    form_class = ComponentForm
    template_name = 'supervisor/component_form.html'
    success_url = reverse_lazy('supervisor:component_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Component updated successfully!')
        return response

class ComponentDeleteView(SupervisorRequiredMixin, DeleteView):
    model = Component
    template_name = 'supervisor/component_confirm_delete.html'
    success_url = reverse_lazy('supervisor:component_list')

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(request, 'Component deleted successfully!')
        return response

# Component Type Management Views
class ComponentTypeListView(SupervisorRequiredMixin, ListView):
    model = ComponentType
    template_name = 'supervisor/component_type_list.html'
    context_object_name = 'component_types'

class ComponentTypeCreateView(SupervisorRequiredMixin, CreateView):
    model = ComponentType
    form_class = ComponentTypeForm
    template_name = 'supervisor/component_type_form.html'
    success_url = reverse_lazy('supervisor:component_type_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Component type created successfully!')
        return response

class ComponentTypeUpdateView(SupervisorRequiredMixin, UpdateView):
    model = ComponentType
    form_class = ComponentTypeForm
    template_name = 'supervisor/component_type_form.html'
    success_url = reverse_lazy('supervisor:component_type_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Component type updated successfully!')
        return response

class ComponentTypeDeleteView(SupervisorRequiredMixin, DeleteView):
    model = ComponentType
    template_name = 'supervisor/component_type_confirm_delete.html'
    success_url = reverse_lazy('supervisor:component_type_list')

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(request, 'Component type deleted successfully!')
        return response

# Brand Management Views
class BrandListView(SupervisorRequiredMixin, ListView):
    model = Brand
    template_name = 'supervisor/brand_list.html'
    context_object_name = 'brands'

class BrandCreateView(SupervisorRequiredMixin, CreateView):
    model = Brand
    form_class = BrandForm
    template_name = 'supervisor/brand_form.html'
    success_url = reverse_lazy('supervisor:brand_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Brand created successfully!')
        return response

class BrandUpdateView(SupervisorRequiredMixin, UpdateView):
    model = Brand
    form_class = BrandForm
    template_name = 'supervisor/brand_form.html'
    success_url = reverse_lazy('supervisor:brand_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Brand updated successfully!')
        return response

class BrandDeleteView(SupervisorRequiredMixin, DeleteView):
    model = Brand
    template_name = 'supervisor/brand_confirm_delete.html'
    success_url = reverse_lazy('supervisor:brand_list')

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(request, 'Brand deleted successfully!')
        return response

# Component Compatibility Views
class ComponentCompatibilityCreateView(SupervisorRequiredMixin, CreateView):
    model = ComponentCompatibility
    template_name = 'supervisor/compatibility_form.html'
    fields = ['component', 'compatible_with', 'notes']
    
    def get_success_url(self):
        return reverse_lazy('supervisor:component_detail', 
                          kwargs={'pk': self.object.component.pk})

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Compatibility relationship created successfully.')
        return super().form_valid(form)

class ComponentCompatibilityDeleteView(SupervisorRequiredMixin, DeleteView):
    model = ComponentCompatibility
    template_name = 'supervisor/compatibility_confirm_delete.html'
    
    def get_success_url(self):
        return reverse_lazy('supervisor:component_detail', 
                          kwargs={'pk': self.object.component.pk})

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Compatibility relationship deleted successfully.')
        return super().delete(request, *args, **kwargs)

# Report Views
class ComponentReportView(SupervisorRequiredMixin, TemplateView):
    template_name = 'supervisor/reports/components.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add component statistics to context
        context['total_components'] = Component.objects.count()
        context['low_stock_components'] = Component.objects.filter(
            stock__lte=F('stock_threshold')
        ).count()
        context['out_of_stock_components'] = Component.objects.filter(
            stock=0
        ).count()
        
        return context

class ReportOverviewView(SupervisorRequiredMixin, TemplateView):
    template_name = 'supervisor/reports/overview.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add report data to context
        context['total_requests'] = AssemblyRequest.objects.count()
        context['completed_requests'] = AssemblyRequest.objects.filter(
            status='completed'
        ).count()
        context['active_assemblers'] = UserProfile.objects.filter(
            user_type='assembler',
            is_approved=True
        ).count()
        context['low_stock_components'] = Component.objects.filter(
            stock__lte=F('stock_threshold')
        ).count()
        
        return context

class ComponentReportView(SupervisorRequiredMixin, TemplateView):
    template_name = 'supervisor/reports/components.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add component statistics to context
        context['total_components'] = Component.objects.count()
        context['low_stock_components'] = Component.objects.filter(
            stock__lte=F('stock_threshold')
        ).count()
        context['out_of_stock_components'] = Component.objects.filter(
            stock=0
        ).count()
        context['components_by_type'] = ComponentType.objects.annotate(
            component_count=Count('components')
        )
        
        return context

class RequestReportView(SupervisorRequiredMixin, TemplateView):
    template_name = 'supervisor/reports/requests.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add request statistics to context
        context['requests_by_status'] = AssemblyRequest.objects.values(
            'status'
        ).annotate(count=Count('id'))
        
        # Get monthly statistics
        current_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        context['monthly_stats'] = {
            'total': AssemblyRequest.objects.filter(created_at__gte=current_month).count(),
            'completed': AssemblyRequest.objects.filter(
                created_at__gte=current_month,
                status='completed'
            ).count(),
            'pending': AssemblyRequest.objects.filter(
                created_at__gte=current_month,
                status='pending'
            ).count()
        }
        
        return context

class AssemblerReportView(SupervisorRequiredMixin, TemplateView):
    template_name = 'supervisor/reports/assemblers.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add assembler statistics to context
        context['total_assemblers'] = UserProfile.objects.filter(
            user_type='assembler'
        ).count()
        context['active_assemblers'] = UserProfile.objects.filter(
            user_type='assembler',
            is_approved=True
        ).count()
        context['available_assemblers'] = UserProfile.objects.filter(
            user_type='assembler',
            is_approved=True,
            is_available=True
        ).count()
        
        # Get performance statistics
        assemblers = UserProfile.objects.filter(
            user_type='assembler',
            is_approved=True
        )
        performance_stats = []
        for assembler in assemblers:
            completed_tasks = AssemblyTask.objects.filter(
                assembler=assembler.user,
                status='completed'
            )
            on_time_tasks = completed_tasks.filter(
                actual_completion__lte=F('expected_completion')
            ).count()
            total_completed = completed_tasks.count()
            
            performance_stats.append({
                'assembler': assembler,
                'completed_tasks': total_completed,
                'on_time_percentage': (on_time_tasks / total_completed * 100) if total_completed > 0 else 0
            })
        
        context['performance_stats'] = performance_stats
        
        return context

# Assembly Request Management Views
class AssemblyRequestListView(SupervisorRequiredMixin, ListView):
    model = AssemblyRequest
    template_name = 'supervisor/request_list.html'
    context_object_name = 'requests'
    paginate_by = 10

    def get_queryset(self):
        queryset = AssemblyRequest.objects.all()
        
        # Apply filters if provided
        status = self.request.GET.get('status')
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        
        if status:
            queryset = queryset.filter(status=status)
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        return queryset.order_by('-created_at')

class AssemblyRequestDetailView(SupervisorRequiredMixin, DetailView):
    model = AssemblyRequest
    template_name = 'supervisor/request_detail.html'
    context_object_name = 'request'

class AssemblyRequestAssignView(SupervisorRequiredMixin, UpdateView):
    model = AssemblyRequest
    template_name = 'supervisor/request_assign.html'
    fields = ['assigned_to']
    success_url = reverse_lazy('supervisor:request_list')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.assigned_at = timezone.now()
        self.object.save()
        messages.success(self.request, 'Assembly request assigned successfully!')
        return redirect(self.get_success_url())

class AssemblyRequestApproveView(SupervisorRequiredMixin, UpdateView):
    model = AssemblyRequest
    template_name = 'supervisor/request_approve.html'
    fields = ['review_notes']
    success_url = reverse_lazy('supervisor:request_list')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.status = 'approved'
        self.object.reviewed_by = self.request.user
        self.object.reviewed_at = timezone.now()
        self.object.save()
        messages.success(self.request, 'Assembly request approved successfully!')
        return redirect(self.get_success_url())

class AssemblyRequestRejectView(SupervisorRequiredMixin, UpdateView):
    model = AssemblyRequest
    template_name = 'supervisor/request_reject.html'
    fields = ['review_notes']
    success_url = reverse_lazy('supervisor:request_list')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.status = 'rejected'
        self.object.reviewed_by = self.request.user
        self.object.reviewed_at = timezone.now()
        self.object.save()
        messages.success(self.request, 'Assembly request rejected successfully!')
        return redirect(self.get_success_url())

class AssemblerApproveView(SupervisorRequiredMixin, UpdateView):
    model = UserProfile
    template_name = 'supervisor/assembler_approve.html'
    fields = []
    success_url = reverse_lazy('supervisor:assembler_list')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.is_approved = True
        self.object.approved_at = timezone.now()
        self.object.approved_by = self.request.user
        self.object.save()
        messages.success(self.request, 'Assembler approved successfully!')
        return redirect(self.get_success_url())

class AssemblerRejectView(SupervisorRequiredMixin, UpdateView):
    model = UserProfile
    template_name = 'supervisor/assembler_reject.html'
    fields = ['rejection_reason']
    success_url = reverse_lazy('supervisor:assembler_list')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.is_approved = False
        self.object.rejected_at = timezone.now()
        self.object.rejected_by = self.request.user
        self.object.save()
        messages.success(self.request, 'Assembler rejected successfully!')
        return redirect(self.get_success_url())

class AssemblerListView(SupervisorRequiredMixin, ListView):
    model = UserProfile
    template_name = 'supervisor/assembler_list.html'
    context_object_name = 'assemblers'

    def get_queryset(self):
        return UserProfile.objects.filter(user_type='assembler').select_related('user')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pending_count'] = UserProfile.objects.filter(
            user_type='assembler',
            is_approved=False
        ).count()
        context['active_count'] = UserProfile.objects.filter(
            user_type='assembler',
            is_approved=True,
            is_available=True
        ).count()
        return context

class AssemblerDetailView(SupervisorRequiredMixin, DetailView):
    model = UserProfile
    template_name = 'supervisor/assembler_detail.html'
    context_object_name = 'assembler'

    def get_queryset(self):
        return UserProfile.objects.filter(user_type='assembler').select_related('user')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        assembler = self.get_object()
        
        # Get assembler's tasks
        context['completed_tasks'] = AssemblyTask.objects.filter(
            assembler=assembler.user,
            status='completed'
        ).count()
        
        context['in_progress_tasks'] = AssemblyTask.objects.filter(
            assembler=assembler.user,
            status__in=['preparing', 'assembling', 'testing']
        ).count()
        
        context['recent_tasks'] = AssemblyTask.objects.filter(
            assembler=assembler.user
        ).order_by('-created_at')[:5]
        
        # Get performance metrics
        completed_tasks = AssemblyTask.objects.filter(
            assembler=assembler.user,
            status='completed'
        )
        
        context['on_time_completion'] = completed_tasks.filter(
            actual_completion__lte=F('expected_completion')
        ).count()
        
        context['total_completed'] = completed_tasks.count()
        
        if context['total_completed'] > 0:
            context['on_time_percentage'] = (
                context['on_time_completion'] / context['total_completed']
            ) * 100
        else:
            context['on_time_percentage'] = 0
        
        return context

# System Announcement Management Views
class AnnouncementListView(SupervisorRequiredMixin, ListView):
    model = SystemAnnouncement
    template_name = 'supervisor/announcement_list.html'
    context_object_name = 'announcements'
    paginate_by = 10

    def get_queryset(self):
        return SystemAnnouncement.objects.order_by('-start_date')

class AnnouncementCreateView(SupervisorRequiredMixin, CreateView):
    model = SystemAnnouncement
    form_class = AnnouncementForm
    template_name = 'supervisor/announcement_form.html'
    success_url = reverse_lazy('supervisor:announcement_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'System announcement created successfully!')
        return response

class AnnouncementUpdateView(SupervisorRequiredMixin, UpdateView):
    model = SystemAnnouncement
    form_class = AnnouncementForm
    template_name = 'supervisor/announcement_form.html'
    success_url = reverse_lazy('supervisor:announcement_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'System announcement updated successfully!')
        return response

class AnnouncementDeleteView(SupervisorRequiredMixin, DeleteView):
    model = SystemAnnouncement
    template_name = 'supervisor/announcement_confirm_delete.html'
    success_url = reverse_lazy('supervisor:announcement_list')

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(request, 'System announcement deleted successfully!')
        return response
