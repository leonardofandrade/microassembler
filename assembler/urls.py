from django.urls import path
from . import views

app_name = 'assembler'

urlpatterns = [
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    
    # Task management
    path('tasks/', views.TaskListView.as_view(), name='task_list'),
    path('tasks/<int:pk>/', views.TaskDetailView.as_view(), name='task_detail'),
    path('tasks/<int:pk>/start/', views.TaskStartView.as_view(), name='task_start'),
    path('tasks/<int:pk>/complete/', views.TaskCompleteView.as_view(), name='task_complete'),
    path('tasks/<int:pk>/report-issue/', views.TaskReportIssueView.as_view(), name='task_report_issue'),
    
    # Checkpoints
    path('tasks/<int:task_pk>/checkpoints/', views.CheckpointListView.as_view(), name='checkpoint_list'),
    path('tasks/<int:task_pk>/checkpoints/create/', views.CheckpointCreateView.as_view(), name='checkpoint_create'),
    path('tasks/<int:task_pk>/checkpoints/<int:pk>/complete/', views.CheckpointCompleteView.as_view(), name='checkpoint_complete'),
    
    # Issues
    path('issues/', views.IssueListView.as_view(), name='issue_list'),
    path('issues/<int:pk>/', views.IssueDetailView.as_view(), name='issue_detail'),
    path('issues/<int:pk>/resolve/', views.IssueResolveView.as_view(), name='issue_resolve'),
    
    # Profile and settings
    path('profile/', views.AssemblerProfileView.as_view(), name='profile'),
    path('profile/edit/', views.AssemblerProfileEditView.as_view(), name='profile_edit'),
    path('availability/', views.AvailabilityUpdateView.as_view(), name='availability_update'),
    
    # Reports
    path('reports/tasks/', views.TaskReportView.as_view(), name='task_report'),
    path('reports/performance/', views.PerformanceReportView.as_view(), name='performance_report'),
]
