from django import forms
from django.core.exceptions import ValidationError
import bleach

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Layout, Submit

from .models import EmailCampaign, EmailSendCandidate, EmailTemplate, UserProfile


class EmailTemplateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EmailTemplateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.template_pack = "tailwind"
        self.helper.layout = "vertical"
        self.helper.add_input(
            Submit(
                "submit",
                "Save Template",
                css_class="w-full py-2 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none",
            )
        )

    def clean_subject(self):
        """Sanitize email subject to prevent injection attacks."""
        subject = self.cleaned_data.get('subject', '')
        # Remove any newline characters that could be used for header injection
        sanitized_subject = subject.replace('\n', '').replace('\r', '').strip()
        # Limit length to prevent abuse
        if len(sanitized_subject) > 255:
            raise ValidationError("Subject line is too long (max 255 characters).")
        return sanitized_subject

    def clean_body(self):
        """Sanitize email body to prevent XSS and injection attacks."""
        body = self.cleaned_data.get('body', '')
        # Allow basic HTML tags but strip dangerous ones
        allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'a', 'ul', 'ol', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']
        allowed_attributes = {'a': ['href', 'title']}
        sanitized_body = bleach.clean(body, tags=allowed_tags, attributes=allowed_attributes, strip=True)
        return sanitized_body

    class Meta:
        model = EmailTemplate
        fields = ["name", "subject", "body"]


class EmailForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EmailForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.template_pack = "tailwind"
        self.helper.layout = "vertical"
        self.helper.add_input(
            Submit(
                "submit",
                "Save",
                css_class="w-full py-2 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none",
            )
        )

    class Meta:
        model = EmailSendCandidate
        fields = ["recipient", "template", "scheduled_time"]


class RecipientUploadForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(RecipientUploadForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.template_pack = "tailwind"
        self.helper.layout = "vertical"
        self.helper.add_input(
            Submit(
                "submit",
                "Save",
                css_class="w-full py-2 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none",
            )
        )

    csv_file = forms.FileField()


class EmailCampaignForm(forms.ModelForm):
    scheduled_time = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={
                "type": "datetime-local",
            }
        ),
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super(EmailCampaignForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"

        # Define the layout
        self.helper.layout = Layout(
            "name",
            "template",
            "scheduled_time",
            # Hidden field to store selected recipient IDs
            Field("recipients", type="hidden", id="selected_recipients"),
            Submit(
                "submit",
                "Create Campaign",
                css_class="w-full py-2 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none",
            ),
        )

    class Meta:
        model = EmailCampaign
        fields = ["name", "template", "scheduled_time"]


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

    def __init__(self, *args, **kwargs):
        super(RecipientFilterForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "get"  # Use 'get' method for filtering
        self.helper.form_class = "mb-4"

        # Define the layout
        self.helper.layout = Layout(
            "first_name",
            "last_name",
            "company",
            "email",
            "country",
            "city",
            "free_field1",
            "free_field2",
            "free_field3",
            Submit("filter", "Apply Filters", css_class="px-4 py-2 bg-green-500 text-white rounded", attrs={"value": "1"}),
        )

    class Meta:
        fields = [
            "first_name",
            "last_name",
            "company",
            "email",
            "country",
            "city",
            "free_field1",
            "free_field2",
            "free_field3",
        ]


class UserProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.template_pack = "tailwind"
        self.helper.layout = "vertical"
        self.helper.add_input(
            Submit(
                "submit",
                "Save",
                css_class="w-full py-2 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none",
            )
        )

    class Meta:
        model = UserProfile
        fields = [
            "smtp_host",
            "smtp_port",
            "smtp_username",
            "smtp_password",
            "use_tls",
            "use_ssl",
            "from_email",
            "max_emails_per_hour",
        ]
        widgets = {
            "smtp_password": forms.PasswordInput(),
        }
