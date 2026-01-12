from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Q
from .models import Notification, User
from .forms import NotificationForm, BulkNotificationForm
import json

class NotificationDashboardView(LoginRequiredMixin, View):
    """Dashboard for notification management"""
    
    def get(self, request):
        # Get user's notifications
        user_notifications = Notification.objects.filter(
            recipient=request.user
        ).order_by('-created_at')[:10]
        
        # Get sent notifications (if user is sender)
        sent_notifications = Notification.objects.filter(
            sender=request.user
        ).order_by('-created_at')[:5]
        
        # Get notification statistics
        total_notifications = Notification.objects.filter(recipient=request.user).count()
        unread_notifications = Notification.objects.filter(
            recipient=request.user, 
            is_read=False
        ).count()
        
        context = {
            'user_notifications': user_notifications,
            'sent_notifications': sent_notifications,
            'total_notifications': total_notifications,
            'unread_notifications': unread_notifications,
            'notification_types': Notification.NOTIFICATION_TYPES,
            'priority_levels': Notification.PRIORITY_LEVELS,
        }
        
        return render(request, 'notification/dashboard.html', context)


class CreateNotificationView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """View for creating and sending individual notifications"""
    model = Notification
    form_class = NotificationForm
    template_name = 'notification/create_notification.html'  # Fixed path
    permission_required = 'notification.add_notification'
    success_url = reverse_lazy('notification-dashboard')
    
    def get_form_kwargs(self):
        """Pass request to form"""
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
    
    def get_context_data(self, **kwargs):
        """Add users to context for recipient selection"""
        context = super().get_context_data(**kwargs)
        context['users'] = User.objects.exclude(id=self.request.user.id)
        context['create_notification_active'] = True
        return context
    
    def form_valid(self, form):
        """Set sender and handle notification sending"""
        form.instance.sender = self.request.user
        
        # If scheduled_for is set, status should be pending
        if form.instance.scheduled_for:
            form.instance.status = 'pending'
        else:
            form.instance.status = 'sent'
            form.instance.sent_at = timezone.now()
        
        response = super().form_valid(form)
        messages.success(self.request, f'Notification sent to {form.instance.recipient.username}')
        return response
    
    def form_invalid(self, form):
        """Handle invalid form"""
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)

class BulkNotificationView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """View for sending bulk notifications to multiple users"""
    template_name = 'notification/bulk_notification.html'
    permission_required = 'notification.add_notification'
    
    def get(self, request):
        form = BulkNotificationForm(request=request)
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = BulkNotificationForm(request.POST, request=request)
        
        if form.is_valid():
            # Get recipients
            recipients = form.cleaned_data['recipients']
            
            # Get additional parameters
            title = form.cleaned_data['title']
            message = form.cleaned_data['message']
            notification_type = form.cleaned_data['notification_type']
            priority = form.cleaned_data['priority']
            action_url = form.cleaned_data.get('action_url')
            icon = form.cleaned_data.get('icon')
            
            sent_count = 0
            failed_count = 0
            
            for recipient in recipients:
                try:
                    notification = Notification.objects.create(
                        title=title,
                        message=message,
                        notification_type=notification_type,
                        priority=priority,
                        recipient=recipient,
                        sender=request.user,
                        status='sent',
                        sent_at=timezone.now(),
                        action_url=action_url,
                        icon=icon
                    )
                    sent_count += 1
                except Exception as e:
                    failed_count += 1
                    # Log error if needed
            
            messages.success(
                request, 
                f'Successfully sent {sent_count} notifications. Failed: {failed_count}'
            )
            return redirect('notification-dashboard')
        
        return render(request, self.template_name, {'form': form})


class TemplateBasedNotificationView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """View for sending notifications based on templates"""
    
    # Notification templates
    TEMPLATES = {
        'welcome': {
            'title': 'Welcome to Our Community!',
            'message': 'Welcome {user}! We are excited to have you join our community.',
            'type': 'announcement',
            'priority': 'medium',
            'icon': 'welcome',
        },
        'birthday': {
            'title': 'Happy Birthday!',
            'message': 'Happy Birthday {user}! May God bless you abundantly.',
            'type': 'birthday',
            'priority': 'high',
            'icon': 'birthday',
        },
        'anniversary': {
            'title': 'Anniversary Celebration',
            'message': 'Congratulations on your anniversary! {message}',
            'type': 'anniversary',
            'priority': 'high',
            'icon': 'anniversary',
        },
        'prayer_reminder': {
            'title': 'Prayer Reminder',
            'message': 'Reminder: {message}',
            'type': 'prayer_request',
            'priority': 'medium',
            'icon': 'prayer',
        },
        'event_reminder': {
            'title': 'Upcoming Event',
            'message': 'Reminder: {message}',
            'type': 'event',
            'priority': 'medium',
            'icon': 'event',
        },
    }
    
    def get(self, request):
        return render(request, 'notifications/template_notification.html', {
            'templates': self.TEMPLATES
        })
    
    def post(self, request):
        template_key = request.POST.get('template')
        recipients_ids = request.POST.getlist('recipients')
        custom_message = request.POST.get('custom_message', '')
        
        if template_key not in self.TEMPLATES:
            messages.error(request, 'Invalid template selected')
            return redirect('template-notification')
        
        template = self.TEMPLATES[template_key]
        recipients = User.objects.filter(id__in=recipients_ids)
        
        sent_count = 0
        for recipient in recipients:
            try:
                message = template['message'].format(
                    user=recipient.get_full_name() or recipient.username,
                    message=custom_message
                )
                
                Notification.objects.create(
                    title=template['title'],
                    message=message,
                    notification_type=template['type'],
                    priority=template['priority'],
                    recipient=recipient,
                    sender=request.user,
                    status='sent',
                    sent_at=timezone.now(),
                    icon=template.get('icon')
                )
                sent_count += 1
            except Exception as e:
                # Log error
                pass
        
        messages.success(request, f'Successfully sent {sent_count} template notifications')
        return redirect('notification-dashboard')


class SendToGroupView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """Send notifications to user groups or all users"""

    def get_permission_required(self):
        if self.request.user.is_superuser or self.request.user.is_staff or getattr(self.request.user, 'roles', None) == 'admin':
            return ('notification.send_to_all',)
        return ('notification.add_notification',)

    def get(self, request):
        # Get user roles (you can customize this based on your user model)
        roles = User.objects.values_list('roles', flat=True).distinct()
        return render(request, 'notification/group_notification.html', {
            'roles': roles,
            'notification_types': Notification.NOTIFICATION_TYPES
        })
    
    def post(self, request):
        roles_name = request.POST.get('roles')
        title = request.POST.get('title')
        message = request.POST.get('message')
        notification_type = request.POST.get('notification_type')
        priority = request.POST.get('priority', 'medium')
        
        if roles_name == 'all':
            recipients = User.objects.all()
        else:
            recipients = User.objects.filter(roles=roles_name)
        
        sent_count = 0
        for recipient in recipients:
            try:
                Notification.objects.create(
                    title=title,
                    message=message,
                    notification_type=notification_type,
                    priority=priority,
                    recipient=recipient,
                    sender=request.user,
                    status='sent',
                    sent_at=timezone.now()
                )
                sent_count += 1
            except Exception as e:
                # Log error
                pass
        
        messages.success(request, f'Notification sent to {sent_count} users in roles "{roles_name}"')
        return redirect('notification-dashboard')


class MarkAsReadView(LoginRequiredMixin, View):
    """Mark a notification as read"""
    
    def post(self, request, pk):
        try:
            notification = Notification.objects.get(pk=pk, recipient=request.user)
            notification.mark_as_read()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            else:
                messages.success(request, 'Notification marked as read')
                return redirect(request.META.get('HTTP_REFERER', 'notification-dashboard'))
        except Notification.DoesNotExist:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Notification not found'}, status=404)
            else:
                messages.error(request, 'Notification not found')
                return redirect('notification-dashboard')


class MarkAllAsReadView(LoginRequiredMixin, View):
    """Mark all user's notifications as read"""
    
    def post(self, request):
        unread_notifications = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        )
        
        updated_count = unread_notifications.update(
            is_read=True,
            read_at=timezone.now(),
            status='read'
        )
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'updated_count': updated_count
            })
        else:
            messages.success(request, f'Marked {updated_count} notifications as read')
            return redirect(request.META.get('HTTP_REFERER', 'notification-dashboard'))


class NotificationListView(LoginRequiredMixin, ListView):
    """List all notifications for a user"""
    model = Notification
    template_name = 'notification/notification_list.html'
    context_object_name = 'notifications'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Notification.objects.filter(recipient=self.request.user)
        
        # Filter by type if provided
        notification_type = self.request.GET.get('type')
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
        
        # Filter by status if provided
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by read status if provided
        is_read = self.request.GET.get('is_read')
        if is_read in ['true', 'false']:
            queryset = queryset.filter(is_read=(is_read == 'true'))
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(message__icontains=search_query)
            )
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notification_types'] = Notification.NOTIFICATION_TYPES
        context['status_choices'] = Notification.STATUS_CHOICES
        context['total_count'] = self.get_queryset().count()
        context['unread_count'] = self.get_queryset().filter(is_read=False).count()
        return context


class SentNotificationsView(LoginRequiredMixin, ListView):
    """List all notifications sent by the user"""
    model = Notification
    template_name = 'notification   /sent_notifications.html'  # Adjust path as needed
    context_object_name = 'sent_notifications'
    paginate_by = 20
    
    def get_queryset(self):
        """Get notifications sent by current user"""
        return Notification.objects.filter(
            sender=self.request.user
        ).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        """Add unread_count and other context data"""
        context = super().get_context_data(**kwargs)
        
        # Get unread count for the current user
        context['unread_count'] = Notification.objects.filter(
            recipient=self.request.user,
            is_read=False
        ).count()
        
        # Add active state for sidebar highlighting
        context['sent_notifications_active'] = True
        
        return context


class NotificationDetailView(LoginRequiredMixin, DetailView):
    """View a specific notification"""
    model = Notification
    template_name = 'notification/notification_detail.html'
    context_object_name = 'notification'
    
    def get_queryset(self):
        # Users can only view notifications sent to them
        return Notification.objects.filter(recipient=self.request.user)
    
    def get(self, request, *args, **kwargs):
        # Mark as read when viewing
        response = super().get(request, *args, **kwargs)
        if not self.object.is_read:
            self.object.mark_as_read()
        return response


class DeleteNotificationView(LoginRequiredMixin, DeleteView):
    """Delete a notification"""
    model = Notification
    template_name = 'notification/notification_confirm_delete.html'
    success_url = reverse_lazy('notification-list')
    
    def get_queryset(self):
        # Users can only delete notifications sent to them
        return Notification.objects.filter(recipient=self.request.user)


class NotificationStatisticsView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """View notification statistics and analytics"""
    permission_required = 'notification.view_notification'
    
    def get(self, request):
        # Overall statistics
        total_notifications = Notification.objects.count()
        sent_notifications = Notification.objects.filter(status='sent').count()
        read_notifications = Notification.objects.filter(is_read=True).count()
        
        # Statistics by type
        type_stats = []
        for notification_type, display_name in Notification.NOTIFICATION_TYPES:
            count = Notification.objects.filter(notification_type=notification_type).count()
            if count > 0:
                type_stats.append({
                    'type': display_name,
                    'count': count,
                    'percentage': (count / total_notifications * 100) if total_notifications > 0 else 0
                })
        
        # Statistics by priority
        priority_stats = []
        for priority, display_name in Notification.PRIORITY_LEVELS:
            count = Notification.objects.filter(priority=priority).count()
            if count > 0:
                priority_stats.append({
                    'priority': display_name,
                    'count': count
                })
        
        # Recent activity
        recent_notifications = Notification.objects.order_by('-created_at')[:10]
        
        context = {
            'total_notifications': total_notifications,
            'sent_notifications': sent_notifications,
            'read_notifications': read_notifications,
            'type_stats': type_stats,
            'priority_stats': priority_stats,
            'recent_notifications': recent_notifications,
        }
        
        return render(request, 'notification/statistics.html', context)


# AJAX views for async operations
class GetUserSuggestionsView(LoginRequiredMixin, View):
    """Get user suggestions for recipient field"""
    
    def get(self, request):
        query = request.GET.get('q', '')
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )[:10]
        
        suggestions = []
        for user in users:
            suggestions.append({
                'id': user.id,
                'text': f"{user.get_full_name()} ({user.username})" if user.get_full_name() else user.username,
                'email': user.email
            })
        
        return JsonResponse({'results': suggestions})


class GetNotificationCountView(LoginRequiredMixin, View):
    """Get unread notification count for badge"""
    
    def get(self, request):
        unread_count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
        
        return JsonResponse({'unread_count': unread_count})
    
