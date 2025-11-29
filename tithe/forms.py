# tithepayment/forms.py
from django import forms
from .models import TithePayment
from member.models import Member

class TithePaymentForm(forms.ModelForm):
    class Meta:
        model = TithePayment
        fields = ['name', 'contact_number', 'amount', 'status', 'date']
        widgets = {
            'date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control',
                'placeholder': 'Select date and time'
            }),
            'name': forms.Select(attrs={
                'class': 'form-control',
                'style': 'width: 100%'
            }),
            'contact_number': forms.TextInput(attrs={
                'class': 'form-control',
                'readonly': 'readonly',
                'placeholder': 'Contact number will auto-populate',
                'style': 'background-color: #f8f9fa;'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'placeholder': 'Enter amount'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            })
        }
        labels = {
            'name': 'Member',
            'status': 'Payment Method'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Customize the member dropdown - order by name
        self.fields['name'].queryset = Member.objects.all().order_by('name')
        self.fields['name'].empty_label = "Select a member..."
        
        # Set initial contact number if instance exists
        if self.instance and self.instance.pk and self.instance.name:
            self.fields['contact_number'].initial = self.instance.name.telephone  # Changed from contact_number

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount and amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")
        return amount