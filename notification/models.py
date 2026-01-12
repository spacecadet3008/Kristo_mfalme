from django.db import models
from member.models import Member
from django.utils import timezone
from users.models import User

# Create your models here.

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('announcement', 'Announcement'),
        ('event', 'Event'),
        ('prayer_request', 'Prayer Request'),
        ('donation', 'Donation'),
        ('attendance', 'Attendance'),
        ('birthday', 'Birthday'),
        ('anniversary', 'Anniversary'),
        ('volunteer', 'Volunteer'),
        ('meeting', 'Meeting'),
        ('broadcast', 'Broadcast'),
        ('reminder', 'Reminder'),
        ('alert', 'Alert'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('read', 'Read'),
        ('archived', 'Archived'),
    ]
    
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    priority = models.CharField(max_length=20, choices=PRIORITY_LEVELS, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Recipient information
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_notifications')
    
    # Metadata
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    scheduled_for = models.DateTimeField(null=True, blank=True)
    
    # Additional fields
    action_url = models.URLField(max_length=500, blank=True, null=True, help_text="URL to redirect when notification is clicked")
    icon = models.CharField(max_length=50, blank=True, null=True, help_text="Icon class or name")
    
    # Related content (optional - can link to specific models)
    content_type = models.CharField(max_length=100, blank=True, null=True, help_text="Type of related content")
    object_id = models.PositiveIntegerField(blank=True, null=True, help_text="ID of related object")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True, help_text="Notification expiry date")
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['notification_type', 'status']),
            models.Index(fields=['-created_at']),
        ]
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
    
    def __str__(self):
        return f"{self.title} - {self.recipient.username}"
    
    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.status = 'read'
            self.save()
    
    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False