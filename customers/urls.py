from django.urls import path
from . import views

app_name = 'customer'

urlpatterns = [
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('request/create/', views.AssemblyRequestCreateView.as_view(), name='request_create'),
    path('request/<int:pk>/', views.AssemblyRequestDetailView.as_view(), name='request_detail'),
    path('request/<int:pk>/edit/', views.AssemblyRequestUpdateView.as_view(), name='request_edit'),
    path('request/<int:pk>/cancel/', views.AssemblyRequestCancelView.as_view(), name='request_cancel'),
    path('requests/', views.AssemblyRequestListView.as_view(), name='request_list'),
]
