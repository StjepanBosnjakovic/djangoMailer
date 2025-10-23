"""
Unit tests for management commands.

This module contains tests for management commands in the campaign application:
- send_emails command
"""

from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from campaign.models import (
    EmailCampaign,
    EmailLog,
    EmailSendCandidate,
    EmailTemplate,
    Recipient,
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
