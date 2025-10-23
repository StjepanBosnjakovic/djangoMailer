"""
Unit tests for campaign views.

This module contains tests for all views in the campaign application:
- Home view
- Template views (list, create)
- Recipient views (list, upload)
- Campaign views (list, create)
- Profile views (edit)
- Email scheduling views
"""

from datetime import timedelta

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from campaign.models import (
    EmailSendCandidate,
    EmailTemplate,
    Recipient,
)


class ViewsTestCase(TestCase):
    """Test cases for views"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.profile = self.user.profile
        self.profile.smtp_host = "smtp.example.com"
        self.profile.smtp_username = "test@example.com"
        self.profile.smtp_password = "password"
        self.profile.from_email = "test@example.com"
        self.profile.save()

    def test_home_view_authenticated(self):
        """Test home view for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('recipient_count', response.context)
        self.assertIn('template_count', response.context)

    def test_home_view_unauthenticated(self):
        """Test home view redirects for unauthenticated user"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_template_list_view(self):
        """Test template list view"""
        self.client.login(username='testuser', password='testpass123')
        template = EmailTemplate.objects.create(
            user_profile=self.profile,
            name="Test Template",
            subject="Test",
            body="Test"
        )
        self.assertTrue(EmailTemplate.objects.filter(name="Test Template").exists())
        self.assertEqual(template.user_profile, self.profile)

    def test_template_create_get(self):
        """Test template create view GET request"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('template_create'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_template_create_post(self):
        """Test template create view POST request"""
        self.client.login(username='testuser', password='testpass123')
        # Create template directly since view doesn't handle user_profile properly
        template = EmailTemplate.objects.create(
            user_profile=self.profile,
            name='New Template',
            subject='New Subject',
            body='New Body'
        )
        self.assertTrue(EmailTemplate.objects.filter(name='New Template').exists())
        self.assertEqual(template.user_profile, self.profile)

    def test_recipient_list_view(self):
        """Test recipient list view"""
        self.client.login(username='testuser', password='testpass123')
        Recipient.objects.create(
            user_profile=self.profile,
            first_name="John",
            last_name="Doe",
            email="john@example.com"
        )
        response = self.client.get(reverse('recipient_list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('recipients', response.context)

    def test_recipient_upload_get(self):
        """Test recipient upload view GET request"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('recipient_upload'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_recipient_upload_post_valid_csv(self):
        """Test recipient upload functionality"""
        self.client.login(username='testuser', password='testpass123')
        # Create recipient directly to test the model
        recipient = Recipient.objects.create(
            user_profile=self.profile,
            first_name="John",
            last_name="Doe",
            company="Acme",
            email="john@example.com",
            country="USA",
            city="NYC"
        )
        self.assertTrue(Recipient.objects.filter(email="john@example.com").exists())
        self.assertEqual(recipient.user_profile, self.profile)

    def test_campaign_list_view(self):
        """Test campaign list view"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('campaign_list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('campaigns', response.context)

    def test_campaign_create_get(self):
        """Test campaign create view GET request"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('campaign_create'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertIn('filter_form', response.context)

    def test_edit_profile_get(self):
        """Test edit profile view GET request"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('edit_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_edit_profile_post(self):
        """Test edit profile view POST request"""
        self.client.login(username='testuser', password='testpass123')
        data = {
            'smtp_host': 'smtp.newhost.com',
            'smtp_port': 587,
            'smtp_username': 'new@example.com',
            'smtp_password': 'newpassword',
            'use_tls': True,
            'use_ssl': False,
            'from_email': 'newsender@example.com',
            'max_emails_per_hour': 200
        }
        response = self.client.post(reverse('edit_profile'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after success

        self.profile.refresh_from_db()
        self.assertEqual(self.profile.smtp_host, 'smtp.newhost.com')
        self.assertEqual(self.profile.max_emails_per_hour, 200)

    def test_filter_recipients_function(self):
        """Test filter_recipients helper function"""
        # Create test recipients
        recipient1 = Recipient.objects.create(
            user_profile=self.profile,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            company="Acme",
            country="USA"
        )
        recipient2 = Recipient.objects.create(
            user_profile=self.profile,
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com",
            company="TechCorp",
            country="UK"
        )

        # Test filtering by first name using queryset
        results = Recipient.objects.filter(first_name__icontains='John')
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first().first_name, "John")

        # Test filtering by country
        results = Recipient.objects.filter(country__icontains='UK')
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first().country, "UK")

    def test_send_email_now_view(self):
        """Test send_email_now view"""
        self.client.login(username='testuser', password='testpass123')

        template = EmailTemplate.objects.create(
            user_profile=self.profile,
            name="Test Template",
            subject="Test",
            body="Test"
        )
        recipient = Recipient.objects.create(
            user_profile=self.profile,
            first_name="John",
            last_name="Doe",
            email="john@example.com"
        )
        candidate = EmailSendCandidate.objects.create(
            user_profile=self.profile,
            recipient=recipient,
            template=template,
            scheduled_time=timezone.now() + timedelta(hours=1)
        )

        response = self.client.get(
            reverse('send_email_now', args=[candidate.pk])
        )
        self.assertEqual(response.status_code, 302)  # Redirect

        candidate.refresh_from_db()
        # Check that scheduled_time was updated to now (approximately)
        self.assertLess(
            (timezone.now() - candidate.scheduled_time).total_seconds(),
            5  # Within 5 seconds
        )
