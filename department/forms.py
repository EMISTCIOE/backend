from .models import Department
from home.models import SocialMedia
from django import forms

class DepartmentForm(forms.ModelForm):
    social_media = forms.ModelMultipleChoiceField(queryset=SocialMedia.objects.all(), required=True)
    class Meta:
        model = Department
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'social_media': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }