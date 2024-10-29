from django import forms
from .models import EmailTemplate, EmailSendCandidate

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
