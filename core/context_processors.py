from .models import Notification

def notifications_processor(request):
    """Add unread notifications count and recent notifications to the context."""
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(
            recipient=request.user,
            read=False
        ).count()
        
        recent_notifications = Notification.objects.filter(
            recipient=request.user
        ).order_by('-created_at')[:5]
        
        return {
            'unread_notifications_count': unread_count,
            'recent_notifications': recent_notifications
        }
    return {
        'unread_notifications_count': 0,
        'recent_notifications': []
    }
