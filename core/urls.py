from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('faq/', views.FAQListView.as_view(), name='faq'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('announcements/', views.AnnouncementListView.as_view(), name='announcements'),
    
    # Notification URLs
    path('notifications/', views.NotificationListView.as_view(), name='notifications'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('notifications/mark-read/<int:pk>/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/delete/<int:pk>/', views.delete_notification, name='delete_notification'),
    path('notifications/api/get-count/', views.get_notification_count, name='get_notification_count'),
]
