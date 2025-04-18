from django.urls import path
from . import views

app_name = 'supervisor'

urlpatterns = [
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    
    # Component management
    path('components/', views.ComponentListView.as_view(), name='component_list'),
    path('components/create/', views.ComponentCreateView.as_view(), name='component_create'),
    path('components/<int:pk>/', views.ComponentDetailView.as_view(), name='component_detail'),
    path('components/<int:pk>/edit/', views.ComponentUpdateView.as_view(), name='component_edit'),
    path('components/<int:pk>/delete/', views.ComponentDeleteView.as_view(), name='component_delete'),
    
    # Component compatibility management
    path('components/<int:pk>/compatibility/add/', 
         views.ComponentCompatibilityCreateView.as_view(), 
         name='compatibility_create'),
    path('compatibility/<int:pk>/delete/',
         views.ComponentCompatibilityDeleteView.as_view(),
         name='compatibility_delete'),
    
    # Component type management
    path('component-types/', views.ComponentTypeListView.as_view(), name='component_type_list'),
    path('component-types/create/', views.ComponentTypeCreateView.as_view(), name='component_type_create'),
    path('component-types/<int:pk>/edit/', views.ComponentTypeUpdateView.as_view(), name='component_type_edit'),
    path('component-types/<int:pk>/delete/', views.ComponentTypeDeleteView.as_view(), name='component_type_delete'),
    
    # Brand management
    path('brands/', views.BrandListView.as_view(), name='brand_list'),
    path('brands/create/', views.BrandCreateView.as_view(), name='brand_create'),
    path('brands/<int:pk>/edit/', views.BrandUpdateView.as_view(), name='brand_edit'),
    path('brands/<int:pk>/delete/', views.BrandDeleteView.as_view(), name='brand_delete'),
    
    # Assembly request management
    path('requests/', views.AssemblyRequestListView.as_view(), name='request_list'),
    path('requests/<int:pk>/', views.AssemblyRequestDetailView.as_view(), name='request_detail'),
    path('requests/<int:pk>/approve/', views.AssemblyRequestApproveView.as_view(), name='request_approve'),
    path('requests/<int:pk>/reject/', views.AssemblyRequestRejectView.as_view(), name='request_reject'),
    path('requests/<int:pk>/assign/', views.AssemblyRequestAssignView.as_view(), name='request_assign'),
    
    # Assembler management
    path('assemblers/', views.AssemblerListView.as_view(), name='assembler_list'),
    path('assemblers/<int:pk>/', views.AssemblerDetailView.as_view(), name='assembler_detail'),
    path('assemblers/<int:pk>/approve/', views.AssemblerApproveView.as_view(), name='assembler_approve'),
    path('assemblers/<int:pk>/reject/', views.AssemblerRejectView.as_view(), name='assembler_reject'),
    
    # Reports
    path('reports/overview/', views.ReportOverviewView.as_view(), name='report_overview'),
    path('reports/components/', views.ComponentReportView.as_view(), name='report_components'),
    path('reports/requests/', views.RequestReportView.as_view(), name='report_requests'),
    path('reports/assemblers/', views.AssemblerReportView.as_view(), name='report_assemblers'),
    
    # System announcements
    path('announcements/', views.AnnouncementListView.as_view(), name='announcement_list'),
    path('announcements/create/', views.AnnouncementCreateView.as_view(), name='announcement_create'),
    path('announcements/<int:pk>/edit/', views.AnnouncementUpdateView.as_view(), name='announcement_edit'),
    path('announcements/<int:pk>/delete/', views.AnnouncementDeleteView.as_view(), name='announcement_delete'),
]
