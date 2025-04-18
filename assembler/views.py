from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    TemplateView
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q
from .models import AssemblyTask, TaskCheckpoint, IssueReport
from .forms import (
    TaskUpdateForm,
    CheckpointForm,
    IssueReportForm,
    AssemblerProfileForm,
    AvailabilityForm
)

class AssemblerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return (
            self.request.user.is_authenticated and 
            self.request.user.profile.is_assembler and 
            self.request.user.profile.is_approved
        )

class DashboardView(AssemblerRequiredMixin, TemplateView):
    template_name = 'assembler/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get tasks statistics
        context['pending_tasks'] = AssemblyTask.objects.filter(
            assembler=self.request.user,
            status='pending'
        ).count()
        
        context['in_progress_tasks'] = AssemblyTask.objects.filter(
            assembler=self.request.user,
            status__in=['preparing', 'assembling', 'testing']
        ).count()
        
        context['completed_tasks'] = AssemblyTask.objects.filter(
            assembler=self.request.user,
            status='completed'
        ).count()
        
        # Get recent tasks
        context['recent_tasks'] = AssemblyTask.objects.filter(
            assembler=self.request.user
        ).order_by('-created_at')[:5]
        
        # Get reported issues
        context['open_issues'] = IssueReport.objects.filter(
            reported_by=self.request.user,
            resolved=False
        ).count()
        
        return context

class TaskListView(AssemblerRequiredMixin, ListView):
    model = AssemblyTask
    template_name = 'assembler/task_list.html'
    context_object_name = 'tasks'
    paginate_by = 10

    def get_queryset(self):
        queryset = AssemblyTask.objects.filter(assembler=self.request.user)
        
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

class TaskDetailView(AssemblerRequiredMixin, DetailView):
    model = AssemblyTask
    template_name = 'assembler/task_detail.html'
    context_object_name = 'task'

    def get_queryset(self):
        return AssemblyTask.objects.filter(assembler=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['checkpoints'] = self.object.checkpoints.all().order_by('created_at')
        context['issues'] = self.object.issues.all().order_by('-created_at')
        return context

class TaskStartView(AssemblerRequiredMixin, UpdateView):
    model = AssemblyTask
    template_name = 'assembler/task_start.html'
    form_class = TaskUpdateForm
    success_url = reverse_lazy('assembler:task_list')

    def get_queryset(self):
        return AssemblyTask.objects.filter(
            assembler=self.request.user,
            status='pending'
        )

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.status = 'preparing'
        self.object.start_date = timezone.now()
        self.object.save()
        messages.success(self.request, 'Task started successfully!')
        return redirect(self.get_success_url())

class TaskCompleteView(AssemblerRequiredMixin, UpdateView):
    model = AssemblyTask
    template_name = 'assembler/task_complete.html'
    form_class = TaskUpdateForm
    success_url = reverse_lazy('assembler:task_list')

    def get_queryset(self):
        return AssemblyTask.objects.filter(
            assembler=self.request.user,
            status__in=['preparing', 'assembling', 'testing']
        )

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.status = 'completed'
        self.object.actual_completion = timezone.now()
        self.object.save()
        messages.success(self.request, 'Task completed successfully!')
        return redirect(self.get_success_url())

class CheckpointListView(AssemblerRequiredMixin, ListView):
    model = TaskCheckpoint
    template_name = 'assembler/checkpoint_list.html'
    context_object_name = 'checkpoints'

    def get_queryset(self):
        self.task = get_object_or_404(
            AssemblyTask,
            pk=self.kwargs['task_pk'],
            assembler=self.request.user
        )
        return self.task.checkpoints.all().order_by('created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task'] = self.task
        return context

class CheckpointCreateView(AssemblerRequiredMixin, CreateView):
    model = TaskCheckpoint
    form_class = CheckpointForm
    template_name = 'assembler/checkpoint_form.html'

    def get_success_url(self):
        return reverse_lazy('assembler:checkpoint_list', kwargs={'task_pk': self.kwargs['task_pk']})

    def form_valid(self, form):
        self.task = get_object_or_404(
            AssemblyTask,
            pk=self.kwargs['task_pk'],
            assembler=self.request.user
        )
        form.instance.task = self.task
        form.instance.completed_by = self.request.user
        return super().form_valid(form)

class CheckpointCompleteView(AssemblerRequiredMixin, UpdateView):
    model = TaskCheckpoint
    template_name = 'assembler/checkpoint_complete.html'
    fields = ['notes']

    def get_success_url(self):
        return reverse_lazy('assembler:checkpoint_list', kwargs={'task_pk': self.kwargs['task_pk']})

    def get_queryset(self):
        return TaskCheckpoint.objects.filter(
            task__assembler=self.request.user,
            task__pk=self.kwargs['task_pk']
        )

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.completed = True
        self.object.completed_at = timezone.now()
        self.object.completed_by = self.request.user
        self.object.save()
        messages.success(self.request, 'Checkpoint completed successfully!')
        return redirect(self.get_success_url())

class IssueListView(AssemblerRequiredMixin, ListView):
    model = IssueReport
    template_name = 'assembler/issue_list.html'
    context_object_name = 'issues'
    paginate_by = 10

    def get_queryset(self):
        return IssueReport.objects.filter(
            reported_by=self.request.user
        ).order_by('-created_at')

class IssueDetailView(AssemblerRequiredMixin, DetailView):
    model = IssueReport
    template_name = 'assembler/issue_detail.html'
    context_object_name = 'issue'

    def get_queryset(self):
        return IssueReport.objects.filter(reported_by=self.request.user)

class IssueResolveView(AssemblerRequiredMixin, UpdateView):
    model = IssueReport
    template_name = 'assembler/issue_resolve.html'
    fields = ['resolution_notes']
    success_url = reverse_lazy('assembler:issue_list')

    def get_queryset(self):
        return IssueReport.objects.filter(
            reported_by=self.request.user,
            resolved=False
        )

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.resolved = True
        self.object.resolved_at = timezone.now()
        self.object.resolved_by = self.request.user
        
        # If this was the only unresolved issue for the task, update task status
        if not self.object.task.issues.filter(resolved=False).exclude(pk=self.object.pk).exists():
            self.object.task.status = 'assembling'
            self.object.task.save()
        
        self.object.save()
        messages.success(self.request, 'Issue resolved successfully!')
        return redirect(self.get_success_url())

class TaskReportIssueView(AssemblerRequiredMixin, CreateView):
    model = IssueReport
    form_class = IssueReportForm
    template_name = 'assembler/report_issue.html'

    def get_success_url(self):
        return reverse_lazy('assembler:task_detail', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        self.task = get_object_or_404(
            AssemblyTask,
            pk=self.kwargs['pk'],
            assembler=self.request.user
        )
        form.instance.task = self.task
        form.instance.reported_by = self.request.user
        return super().form_valid(form)

class AssemblerProfileView(AssemblerRequiredMixin, DetailView):
    template_name = 'assembler/profile.html'
    context_object_name = 'profile'

    def get_object(self):
        return self.request.user.profile

class AssemblerProfileEditView(AssemblerRequiredMixin, UpdateView):
    form_class = AssemblerProfileForm
    template_name = 'assembler/profile_edit.html'
    success_url = reverse_lazy('assembler:profile')

    def get_object(self):
        return self.request.user.profile

    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)

class AvailabilityUpdateView(AssemblerRequiredMixin, UpdateView):
    form_class = AvailabilityForm
    template_name = 'assembler/availability_update.html'
    success_url = reverse_lazy('assembler:profile')

    def get_object(self):
        return self.request.user.profile

    def form_valid(self, form):
        messages.success(self.request, 'Availability updated successfully!')
        return super().form_valid(form)

class TaskReportView(AssemblerRequiredMixin, TemplateView):
    template_name = 'assembler/reports/tasks.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get task statistics
        tasks = AssemblyTask.objects.filter(assembler=self.request.user)
        
        context['total_tasks'] = tasks.count()
        context['completed_tasks'] = tasks.filter(status='completed').count()
        context['average_completion_time'] = tasks.filter(
            status='completed',
            actual_completion__isnull=False
        ).exclude(
            start_date__isnull=True
        ).annotate(
            completion_time=models.F('actual_completion') - models.F('start_date')
        ).aggregate(avg_time=models.Avg('completion_time'))['avg_time']
        
        return context

class PerformanceReportView(AssemblerRequiredMixin, TemplateView):
    template_name = 'assembler/reports/performance.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get performance statistics
        tasks = AssemblyTask.objects.filter(assembler=self.request.user)
        
        context['on_time_tasks'] = tasks.filter(
            status='completed',
            actual_completion__lte=models.F('expected_completion')
        ).count()
        
        context['delayed_tasks'] = tasks.filter(
            status='completed',
            actual_completion__gt=models.F('expected_completion')
        ).count()
        
        context['reported_issues'] = IssueReport.objects.filter(
            reported_by=self.request.user
        ).count()
        
        return context
