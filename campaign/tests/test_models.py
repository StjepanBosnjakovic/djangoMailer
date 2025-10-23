"""
Unit tests for campaign models.

This module contains tests for all database models in the campaign application:
- UserProfile
- EmailTemplate
- Recipient
- EmailCampaign
- EmailLog
- EmailSendCandidate
"""

from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from campaign.models import (
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
