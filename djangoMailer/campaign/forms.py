from django import forms
from .models import EmailTemplate, EmailSendCandidate, EmailCampaign, Recipient, UserProfile

class EmailTemplateForm(forms.ModelForm):
    class Meta:
        model = EmailTemplate
        fields = ['name', 'subject', 'body']

class EmailForm(forms.ModelForm):
    class Meta:
        model = EmailSendCandidate
        fields = ['recipient', 'template', 'scheduled_time']


class RecipientUploadForm(forms.Form):
    csv_file = forms.FileField()


class EmailCampaignForm(forms.ModelForm):
    scheduled_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        required=True
    )

    class Meta:
        model = EmailCampaign
        fields = ['name', 'template', 'scheduled_time']


class RecipientFilterForm(forms.Form):
    first_name = forms.CharField(max_length=100, required=False)
    last_name = forms.CharField(max_length=100, required=False)
    company = forms.CharField(max_length=100, required=False)
    email = forms.EmailField(required=False)
    country = forms.CharField(max_length=100, required=False)
    city = forms.CharField(max_length=100, required=False)
    free_field1 = forms.CharField(max_length=255, required=False)
    free_field2 = forms.CharField(max_length=255, required=False)
    free_field3 = forms.CharField(max_length=255, required=False)

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['smtp_host', 'smtp_port', 'smtp_username', 'smtp_password', 'use_tls', 'use_ssl', 'from_email']
        widgets = {
            'smtp_password': forms.PasswordInput(),
        }