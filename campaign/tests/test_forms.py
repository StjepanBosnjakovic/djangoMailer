"""
Unit tests for campaign forms.

This module contains tests for all forms in the campaign application:
- EmailTemplateForm
- RecipientUploadForm
- RecipientFilterForm
- UserProfileForm
"""

import io

from django.contrib.auth.models import User
from django.test import TestCase

from campaign.forms import (
    EmailTemplateForm,
    RecipientFilterForm,
    RecipientUploadForm,
    UserProfileForm,
)


class EmailTemplateFormTest(TestCase):
    """Test cases for EmailTemplateForm"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.profile = self.user.profile

    def test_valid_form(self):
        """Test form with valid data"""
        form_data = {
            'user_profile': self.profile.id,
            'name': 'Test Template',
            'subject': 'Test Subject',
            'body': 'Test Body'
        }
        form = EmailTemplateForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form_missing_name(self):
        """Test form with missing required field"""
        form_data = {
            'user_profile': self.profile.id,
            'subject': 'Test Subject',
            'body': 'Test Body'
        }
        form = EmailTemplateForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)


class RecipientUploadFormTest(TestCase):
    """Test cases for RecipientUploadForm"""

    def test_valid_form(self):
        """Test form with valid CSV file"""
        csv_content = "First,Last,Company,Email,Country,City,Field1,Field2,Field3\n"
        csv_file = io.StringIO(csv_content)
        form_data = {}
        file_data = {'csv_file': csv_file}
        form = RecipientUploadForm(data=form_data, files=file_data)
        self.assertIn('csv_file', form.fields)

    def test_invalid_form_missing_file(self):
        """Test form without file"""
        form = RecipientUploadForm(data={}, files={})
        self.assertFalse(form.is_valid())


class RecipientFilterFormTest(TestCase):
    """Test cases for RecipientFilterForm"""

    def test_form_all_fields_optional(self):
        """Test that all form fields are optional"""
        form = RecipientFilterForm(data={})
        self.assertTrue(form.is_valid())

    def test_form_with_filters(self):
        """Test form with filter data"""
        form_data = {
            'first_name': 'John',
            'email': 'john@example.com',
            'country': 'USA'
        }
        form = RecipientFilterForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['first_name'], 'John')


class UserProfileFormTest(TestCase):
    """Test cases for UserProfileForm"""

    def test_valid_form(self):
        """Test form with valid data"""
        form_data = {
            'smtp_host': 'smtp.gmail.com',
            'smtp_port': 587,
            'smtp_username': 'test@gmail.com',
            'smtp_password': 'password123',
            'use_tls': True,
            'use_ssl': False,
            'from_email': 'sender@example.com',
            'max_emails_per_hour': 100
        }
        form = UserProfileForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_password_field_widget(self):
        """Test that password field uses PasswordInput widget"""
        form = UserProfileForm()
        self.assertEqual(
            form.fields['smtp_password'].widget.__class__.__name__,
            'PasswordInput'
        )
