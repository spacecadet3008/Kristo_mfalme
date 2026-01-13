from django import forms

from .models import Member, Ministry, CommunityLeader


class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = [
            'name', 'code', 'active', 'shepherd', 'ministry', 'telephone',
            'location', 'fathers_name', 'mothers_name', 'guardians_name',
            'new_believer_school', 'pays_tithe', 'working', 'schooling', 'picture','transfer_update','transfered'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter full name'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 001PT'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+255 XXX XXX XXX'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter location'}),
            'fathers_name': forms.TextInput(attrs={'class': 'form-control'}),
            'mothers_name': forms.TextInput(attrs={'class': 'form-control'}),
            'guardians_name': forms.TextInput(attrs={'class': 'form-control'}),
            'shepherd': forms.Select(attrs={'class': 'form-control'}),
            'ministry': forms.Select(attrs={'class': 'form-control'}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'new_believer_school': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'pays_tithe': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'working': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'schooling': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'transfered': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'transfer_update': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Enter details of the member'}),
            'picture': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
"""    def clean_telephone(self):
        telephone = self.cleaned_data.get('telephone')
        if telephone and not telephone.startswith('+'):
            raise forms.ValidationError("Phone number must start with country code (e.g., +255)")
        return telephone"""

class MinistryForm(forms.ModelForm):
    class Meta:
        fields = ['name', 'leader', 'description','feast_date','feast_name']
        model = Ministry


class ShepherdForm(forms.ModelForm):
    class Meta:
        model = CommunityLeader
        fields = ['community_name', 'name', 'leader', 'description', 'phone']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
