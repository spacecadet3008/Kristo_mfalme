from django import forms
from django.core.exceptions import ValidationError
from .models import Notification
from users.models import User


class NotificationForm(forms.ModelForm):
    """Form for creating individual notifications"""
    
    class Meta:
        model = Notification
        fields = [
            'title', 'message', 'notification_type', 'priority',
            'recipient', 'scheduled_for', 'action_url', 'icon',
            'expires_at', 'content_type', 'object_id'
        ]
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4}),
            'scheduled_for': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'expires_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notification_type': forms.Select(),
            'priority': forms.Select(),
        }
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        if self.request:
            # Filter recipients based on user permissions
            self.fields['recipient'].queryset = User.objects.exclude(id=self.request.user.id)
        
        # Add CSS classes
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'form-select'
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs['class'] = 'form-control'
                field.widget.attrs['style'] = 'min-height: 150px;'
            else:
                field.widget.attrs['class'] = 'form-control'
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Ensure content_type and object_id are both provided or both empty
        content_type = cleaned_data.get('content_type')
        object_id = cleaned_data.get('object_id')
        
        if (content_type and not object_id) or (object_id and not content_type):
            raise forms.ValidationError(
                "Both content type and object ID must be provided together, or both left empty."
            )
        
        return cleaned_data

class BulkNotificationForm(forms.Form):
    """Form for sending bulk notifications"""
    recipients = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'select2-multiple'})
    )
    title = forms.CharField(max_length=255)
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}))
    notification_type = forms.ChoiceField(choices=Notification.NOTIFICATION_TYPES)
    priority = forms.ChoiceField(choices=Notification.PRIORITY_LEVELS, initial='medium')
    action_url = forms.URLField(required=False)
    icon = forms.CharField(max_length=50, required=False)
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        if self.request:
            # Exclude current user from recipients
            self.fields['recipients'].queryset = User.objects.exclude(id=self.request.user.id)