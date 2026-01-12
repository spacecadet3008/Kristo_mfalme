from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.NotificationDashboardView.as_view(), name='notification-dashboard'),
    
    # Notification Management
    path('create/', views.CreateNotificationView.as_view(), name='create-notification'),
    path('bulk/', views.BulkNotificationView.as_view(), name='bulk-notification'),
    path('template/', views.TemplateBasedNotificationView.as_view(), name='template-notification'),
    path('group/', views.SendToGroupView.as_view(), name='group-notification'),
    
    # Notification List & Detail
    path('list/', views.NotificationListView.as_view(), name='notification-list'),
    path('sent/', views.SentNotificationsView.as_view(), name='sent-notifications'),
    path('<int:pk>/', views.NotificationDetailView.as_view(), name='notification-detail'),
    path('<int:pk>/delete/', views.DeleteNotificationView.as_view(), name='delete-notification'),
    
    # Actions
    path('<int:pk>/read/', views.MarkAsReadView.as_view(), name='mark-as-read'),
    path('read-all/', views.MarkAllAsReadView.as_view(), name='mark-all-read'),
    
    # Statistics
    path('statistics/', views.NotificationStatisticsView.as_view(), name='notification-statistics'),
    
    # AJAX endpoints
    path('api/user-suggestions/', views.GetUserSuggestionsView.as_view(), name='user-suggestions'),
    path('api/notification-count/', views.GetNotificationCountView.as_view(), name='notification-count'),
]