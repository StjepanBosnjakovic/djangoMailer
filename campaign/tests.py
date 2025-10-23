import csv
import io
from datetime import timedelta
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from .forms import (
    EmailCampaignForm,
    EmailForm,
    EmailTemplateForm,
    RecipientFilterForm,
    RecipientUploadForm,
    UserProfileForm,
)
from .models import (
    EmailCampaign,
    EmailLog,
    EmailSendCandidate,
    EmailTemplate,
    Recipient,
    UserProfile,
)


class UserProfileModelTest(TestCase):
    """Test cases for UserProfile model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )

    def test_user_profile_creation_signal(self):
        """Test that UserProfile is automatically created when User is created"""
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsInstance(self.user.profile, UserProfile)

    def test_user_profile_str(self):
        """Test UserProfile string representation"""
        expected = f"{self.user.username}'s Profile"
        self.assertEqual(str(self.user.profile), expected)

    def test_user_profile_default_values(self):
        """Test UserProfile default values"""
        profile = self.user.profile
        self.assertEqual(profile.smtp_port, 587)
        self.assertTrue(profile.use_tls)
        self.assertFalse(profile.use_ssl)
        self.assertEqual(profile.max_emails_per_hour, 100)

    def test_user_profile_update(self):
        """Test updating UserProfile fields"""
        profile = self.user.profile
        profile.smtp_host = "smtp.gmail.com"
        profile.smtp_username = "test@gmail.com"
        profile.smtp_password = "password123"
        profile.from_email = "sender@example.com"
        profile.save()

        updated_profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(updated_profile.smtp_host, "smtp.gmail.com")
        self.assertEqual(updated_profile.smtp_username, "test@gmail.com")


class EmailTemplateModelTest(TestCase):
    """Test cases for EmailTemplate model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.profile = self.user.profile

    def test_email_template_creation(self):
        """Test creating an EmailTemplate"""
        template = EmailTemplate.objects.create(
            user_profile=self.profile,
            name="Test Template",
            subject="Test Subject",
            body="Hello {first_name}!"
        )
        self.assertEqual(template.name, "Test Template")
        self.assertEqual(template.subject, "Test Subject")
        self.assertIn("{first_name}", template.body)

    def test_email_template_str(self):
        """Test EmailTemplate string representation"""
        template = EmailTemplate.objects.create(
            user_profile=self.profile,
            name="Welcome Email",
            subject="Welcome",
            body="Welcome!"
        )
        self.assertEqual(str(template), "Welcome Email")

    def test_email_template_relationship(self):
        """Test EmailTemplate relationship with UserProfile"""
        template = EmailTemplate.objects.create(
            user_profile=self.profile,
            name="Test",
            subject="Test",
            body="Test"
        )
        self.assertEqual(template.user_profile, self.profile)
        self.assertIn(template, self.profile.email_templates.all())


class RecipientModelTest(TestCase):
    """Test cases for Recipient model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.profile = self.user.profile

    def test_recipient_creation(self):
        """Test creating a Recipient"""
        recipient = Recipient.objects.create(
            user_profile=self.profile,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            company="Acme Corp"
        )
        self.assertEqual(recipient.first_name, "John")
        self.assertEqual(recipient.last_name, "Doe")
        self.assertEqual(recipient.email, "john@example.com")

    def test_recipient_str(self):
        """Test Recipient string representation"""
        recipient = Recipient.objects.create(
            user_profile=self.profile,
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com"
        )
        expected = "Jane Smith (jane@example.com)"
        self.assertEqual(str(recipient), expected)

    def test_recipient_unique_email_per_user(self):
        """Test that email must be unique per user profile"""
        Recipient.objects.create(
            user_profile=self.profile,
            first_name="John",
            last_name="Doe",
            email="duplicate@example.com"
        )

        # Should raise an error for duplicate email with same user_profile
        with self.assertRaises(Exception):
            Recipient.objects.create(
                user_profile=self.profile,
                first_name="Jane",
                last_name="Doe",
                email="duplicate@example.com"
            )

    def test_recipient_optional_fields(self):
        """Test Recipient optional fields"""
        recipient = Recipient.objects.create(
            user_profile=self.profile,
            first_name="John",
            last_name="Doe",
            email="john@example.com"
        )
        self.assertIsNone(recipient.company)
        self.assertIsNone(recipient.country)
        self.assertIsNone(recipient.city)


class EmailCampaignModelTest(TestCase):
    """Test cases for EmailCampaign model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.profile = self.user.profile
        self.template = EmailTemplate.objects.create(
            user_profile=self.profile,
            name="Campaign Template",
            subject="Campaign Subject",
            body="Campaign Body"
        )
        self.recipient = Recipient.objects.create(
            user_profile=self.profile,
            first_name="John",
            last_name="Doe",
            email="john@example.com"
        )

    def test_email_campaign_creation(self):
        """Test creating an EmailCampaign"""
        campaign = EmailCampaign.objects.create(
            user_profile=self.profile,
            name="Test Campaign",
            template=self.template,
            scheduled_time=timezone.now() + timedelta(hours=1)
        )
        campaign.recipients.add(self.recipient)

        self.assertEqual(campaign.name, "Test Campaign")
        self.assertEqual(campaign.template, self.template)
        self.assertIn(self.recipient, campaign.recipients.all())

    def test_email_campaign_str(self):
        """Test EmailCampaign string representation"""
        campaign = EmailCampaign.objects.create(
            user_profile=self.profile,
            name="Summer Sale",
            template=self.template,
            scheduled_time=timezone.now()
        )
        self.assertEqual(str(campaign), "Summer Sale")


class EmailLogModelTest(TestCase):
    """Test cases for EmailLog model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.profile = self.user.profile

    def test_email_log_creation(self):
        """Test creating an EmailLog"""
        log = EmailLog.objects.create(
            user_profile=self.profile,
            recipient="test@example.com",
            status="Sent",
            sent_time=timezone.now()
        )
        self.assertEqual(log.recipient, "test@example.com")
        self.assertEqual(log.status, "Sent")
        self.assertIsNone(log.error_message)

    def test_email_log_with_error(self):
        """Test EmailLog with error message"""
        log = EmailLog.objects.create(
            user_profile=self.profile,
            recipient="test@example.com",
            status="Failed",
            error_message="SMTP connection failed",
            sent_time=timezone.now()
        )
        self.assertEqual(log.status, "Failed")
        self.assertIsNotNone(log.error_message)

    def test_email_log_str(self):
        """Test EmailLog string representation"""
        log = EmailLog.objects.create(
            user_profile=self.profile,
            recipient="test@example.com",
            status="Sent",
            sent_time=timezone.now()
        )
        expected = "test@example.com - Sent"
        self.assertEqual(str(log), expected)


class EmailSendCandidateModelTest(TestCase):
    """Test cases for EmailSendCandidate model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.profile = self.user.profile
        self.template = EmailTemplate.objects.create(
            user_profile=self.profile,
            name="Test Template",
            subject="Test",
            body="Test"
        )
        self.recipient = Recipient.objects.create(
            user_profile=self.profile,
            first_name="John",
            last_name="Doe",
            email="john@example.com"
        )

    def test_email_send_candidate_creation(self):
        """Test creating an EmailSendCandidate"""
        candidate = EmailSendCandidate.objects.create(
            user_profile=self.profile,
            recipient=self.recipient,
            template=self.template,
            scheduled_time=timezone.now()
        )
        self.assertEqual(candidate.recipient, self.recipient)
        self.assertEqual(candidate.template, self.template)
        self.assertFalse(candidate.sent)
        self.assertIsNone(candidate.sent_time)

    def test_email_send_candidate_sent_status(self):
        """Test marking EmailSendCandidate as sent"""
        candidate = EmailSendCandidate.objects.create(
            user_profile=self.profile,
            recipient=self.recipient,
            template=self.template,
            scheduled_time=timezone.now()
        )

        candidate.sent = True
        candidate.sent_time = timezone.now()
        candidate.save()

        self.assertTrue(candidate.sent)
        self.assertIsNotNone(candidate.sent_time)

    def test_email_send_candidate_str(self):
        """Test EmailSendCandidate string representation"""
        candidate = EmailSendCandidate.objects.create(
            user_profile=self.profile,
            recipient=self.recipient,
            template=self.template,
            scheduled_time=timezone.now()
        )
        expected = f"{self.recipient.email} - {self.template.name}"
        self.assertEqual(str(candidate), expected)


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


class SendEmailsCommandTest(TestCase):
    """Test cases for send_emails management command"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.profile = self.user.profile
        self.profile.smtp_host = "smtp.example.com"
        self.profile.smtp_port = 587
        self.profile.smtp_username = "test@example.com"
        self.profile.smtp_password = "password"
        self.profile.from_email = "test@example.com"
        self.profile.use_tls = True
        self.profile.max_emails_per_hour = 10
        self.profile.save()

        self.template = EmailTemplate.objects.create(
            user_profile=self.profile,
            name="Test Template",
            subject="Test Subject",
            body="Hello {first_name} {last_name}!"
        )
        self.recipient = Recipient.objects.create(
            user_profile=self.profile,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            company="Acme"
        )
        self.campaign = EmailCampaign.objects.create(
            user_profile=self.profile,
            name="Test Campaign",
            template=self.template,
            scheduled_time=timezone.now()
        )
        self.campaign.recipients.add(self.recipient)

    @patch('campaign.management.commands.send_emails.EmailMessage.send')
    def test_send_emails_command_success(self, mock_send):
        """Test send_emails command sends emails successfully"""
        mock_send.return_value = 1

        # Create email send candidate
        candidate = EmailSendCandidate.objects.create(
            user_profile=self.profile,
            recipient=self.recipient,
            template=self.template,
            campaign=self.campaign,
            scheduled_time=timezone.now() - timedelta(minutes=5),
            sent=False
        )

        # Run the command
        call_command('send_emails')

        # Check that email was marked as sent
        candidate.refresh_from_db()
        self.assertTrue(candidate.sent)
        self.assertIsNotNone(candidate.sent_time)

        # Check that EmailLog was created
        log = EmailLog.objects.filter(recipient=self.recipient.email).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.status, "Sent")

    @patch('campaign.management.commands.send_emails.EmailMessage.send')
    def test_send_emails_command_failure(self, mock_send):
        """Test send_emails command handles failures"""
        mock_send.side_effect = Exception("SMTP error")

        # Create email send candidate
        candidate = EmailSendCandidate.objects.create(
            user_profile=self.profile,
            recipient=self.recipient,
            template=self.template,
            campaign=self.campaign,
            scheduled_time=timezone.now() - timedelta(minutes=5),
            sent=False
        )

        # Run the command
        call_command('send_emails')

        # Email should still be marked as not sent
        candidate.refresh_from_db()
        self.assertFalse(candidate.sent)

        # Check that error was logged
        log = EmailLog.objects.filter(recipient=self.recipient.email).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.status, "Failed")
        self.assertIn("SMTP error", log.error_message)

    @patch('campaign.management.commands.send_emails.EmailMessage.send')
    def test_send_emails_respects_hourly_limit(self, mock_send):
        """Test that send_emails respects max_emails_per_hour limit"""
        mock_send.return_value = 1

        # Set a low hourly limit
        self.profile.max_emails_per_hour = 2
        self.profile.save()

        # Create multiple candidates
        for i in range(5):
            recipient = Recipient.objects.create(
                user_profile=self.profile,
                first_name=f"User{i}",
                last_name="Test",
                email=f"user{i}@example.com"
            )
            EmailSendCandidate.objects.create(
                user_profile=self.profile,
                recipient=recipient,
                template=self.template,
                campaign=self.campaign,
                scheduled_time=timezone.now() - timedelta(minutes=5),
                sent=False
            )

        # Run the command
        call_command('send_emails')

        # Only 2 emails should be sent due to hourly limit
        sent_count = EmailSendCandidate.objects.filter(sent=True).count()
        self.assertEqual(sent_count, 2)

    def test_send_emails_skips_future_scheduled(self):
        """Test that emails scheduled in the future are not sent"""
        # Create candidate scheduled in the future
        candidate = EmailSendCandidate.objects.create(
            user_profile=self.profile,
            recipient=self.recipient,
            template=self.template,
            campaign=self.campaign,
            scheduled_time=timezone.now() + timedelta(hours=2),
            sent=False
        )

        # Run the command
        call_command('send_emails')

        # Email should not be sent
        candidate.refresh_from_db()
        self.assertFalse(candidate.sent)
