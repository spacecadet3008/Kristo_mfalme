from django.contrib import admin
from .models import Notification
# Register your models here.

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title','message','notification_type','recipient','sender')
    search_fields = ('recipient','sender','title','notification_type')
    list_filter = ('read_at','created_at','priority')
    add_fieldsets=(
        (None,{'classes':('wide'),
               'fields':( 'title', 'message', 'notification_type', 'priority',
            'recipient', 'scheduled_for', 'action_url', 'icon',
            'expires_at', 'content_type', 'object_id')})
    )
    

admin.site.register(Notification,NotificationAdmin)