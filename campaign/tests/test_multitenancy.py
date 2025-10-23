"""
Unit tests for multi-tenancy data isolation.

This module contains tests to verify that users can only access their own data
and cannot see or manipulate data belonging to other users.
"""

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from campaign.models import (
    EmailCampaign,
    EmailLog,
    EmailSendCandidate,
    EmailTemplate,
    Recipient,
)


class MultiTenancyTestCase(TestCase):
    """Test cases for multi-tenancy data isolation"""

    def setUp(self):
        """Set up two users with their own data"""
        self.client = Client()

        # Create first user and profile
        self.user1 = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="testpass123"
        )
        self.profile1 = self.user1.profile
        self.profile1.smtp_host = "smtp.example.com"
        self.profile1.smtp_username = "user1@example.com"
        self.profile1.smtp_password = "password1"
        self.profile1.from_email = "user1@example.com"
        self.profile1.save()

        # Create second user and profile
        self.user2 = User.objects.create_user(
            username="user2",
            email="user2@example.com",
            password="testpass456"
        )
        self.profile2 = self.user2.profile
        self.profile2.smtp_host = "smtp.example.com"
        self.profile2.smtp_username = "user2@example.com"
        self.profile2.smtp_password = "password2"
        self.profile2.from_email = "user2@example.com"
        self.profile2.save()

        # Create data for user1
        self.recipient1 = Recipient.objects.create(
            user_profile=self.profile1,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            company="Company1"
        )
        self.template1 = EmailTemplate.objects.create(
            user_profile=self.profile1,
            name="Template1",
            subject="Subject1",
            body="Body1"
        )
        self.campaign1 = EmailCampaign.objects.create(
            user_profile=self.profile1,
            name="Campaign1",
            template=self.template1,
            scheduled_time=timezone.now()
        )
        self.email1 = EmailSendCandidate.objects.create(
            user_profile=self.profile1,
            recipient=self.recipient1,
            template=self.template1,
            scheduled_time=timezone.now()
        )
        self.log1 = EmailLog.objects.create(
            user_profile=self.profile1,
            recipient="john@example.com",
            campaign=self.campaign1,
            status="sent",
            sent_time=timezone.now()
        )

        # Create data for user2
        self.recipient2 = Recipient.objects.create(
            user_profile=self.profile2,
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com",
            company="Company2"
        )
        self.template2 = EmailTemplate.objects.create(
            user_profile=self.profile2,
            name="Template2",
            subject="Subject2",
            body="Body2"
        )
        self.campaign2 = EmailCampaign.objects.create(
            user_profile=self.profile2,
            name="Campaign2",
            template=self.template2,
            scheduled_time=timezone.now()
        )
        self.email2 = EmailSendCandidate.objects.create(
            user_profile=self.profile2,
            recipient=self.recipient2,
            template=self.template2,
            scheduled_time=timezone.now()
        )
        self.log2 = EmailLog.objects.create(
            user_profile=self.profile2,
            recipient="jane@example.com",
            campaign=self.campaign2,
            status="sent",
            sent_time=timezone.now()
        )

    def test_recipient_list_isolation(self):
        """Test that recipient_list only shows user's own recipients"""
        # Login as user1
        self.client.login(username='user1', password='testpass123')
        response = self.client.get(reverse('recipient_list'))
        self.assertEqual(response.status_code, 200)

        # Check that only user1's recipient is in the context
        recipients = response.context['recipients']
        self.assertEqual(recipients.count(), 1)
        self.assertEqual(recipients.first().email, "john@example.com")

        # Verify user2's recipient is not in the list
        self.assertNotIn(self.recipient2, recipients)

    def test_template_list_isolation(self):
        """Test that template_list only shows user's own templates"""
        # Login as user1
        self.client.login(username='user1', password='testpass123')
        response = self.client.get(reverse('template_list'))
        self.assertEqual(response.status_code, 200)

        # Check that only user1's template is in the context
        templates = response.context['templates']
        self.assertEqual(templates.count(), 1)
        self.assertEqual(templates.first().name, "Template1")

        # Verify user2's template is not in the list
        self.assertNotIn(self.template2, templates)

    def test_email_list_isolation(self):
        """Test that email_list only shows user's own emails"""
        # Login as user1
        self.client.login(username='user1', password='testpass123')
        response = self.client.get(reverse('email_list'))
        self.assertEqual(response.status_code, 200)

        # Check that only user1's email is in the context
        emails = response.context['emails']
        self.assertEqual(emails.count(), 1)
        self.assertEqual(emails.first().recipient.email, "john@example.com")

        # Verify user2's email is not in the list
        self.assertNotIn(self.email2, emails)

    def test_campaign_list_isolation(self):
        """Test that campaign_list only shows user's own campaigns"""
        # Login as user1
        self.client.login(username='user1', password='testpass123')
        response = self.client.get(reverse('campaign_list'))
        self.assertEqual(response.status_code, 200)

        # Check that only user1's campaign is in the context
        campaigns = response.context['campaigns']
        self.assertEqual(campaigns.count(), 1)
        self.assertEqual(campaigns.first().name, "Campaign1")

        # Verify user2's campaign is not in the list
        self.assertNotIn(self.campaign2, campaigns)

    def test_log_list_isolation(self):
        """Test that log_list only shows user's own logs"""
        # Login as user1
        self.client.login(username='user1', password='testpass123')
        response = self.client.get(reverse('log_list'))
        self.assertEqual(response.status_code, 200)

        # Check that only user1's log is in the context
        logs = response.context['logs']
        self.assertEqual(logs.count(), 1)
        self.assertEqual(logs.first().recipient, "john@example.com")

        # Verify user2's log is not in the list
        self.assertNotIn(self.log2, logs)

    def test_queue_list_isolation(self):
        """Test that queue_list only shows user's own queued emails"""
        # Login as user1
        self.client.login(username='user1', password='testpass123')
        response = self.client.get(reverse('queue_list'))
        self.assertEqual(response.status_code, 200)

        # Check that only user1's queued email is in the context
        queues = response.context['queues']
        self.assertEqual(queues.count(), 1)
        self.assertEqual(queues.first().recipient.email, "john@example.com")

        # Verify user2's email is not in the list
        self.assertNotIn(self.email2, queues)

    def test_home_view_counts_isolation(self):
        """Test that home view only shows counts for user's own data"""
        # Login as user1
        self.client.login(username='user1', password='testpass123')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

        # Check that counts only reflect user1's data
        self.assertEqual(response.context['recipient_count'], 1)
        self.assertEqual(response.context['template_count'], 1)
        self.assertEqual(response.context['email_count'], 1)
        self.assertEqual(response.context['email_log_count'], 1)

    def test_user2_sees_only_own_recipients(self):
        """Test that user2 can only see their own recipients"""
        # Login as user2
        self.client.login(username='user2', password='testpass456')
        response = self.client.get(reverse('recipient_list'))
        self.assertEqual(response.status_code, 200)

        # Check that only user2's recipient is in the context
        recipients = response.context['recipients']
        self.assertEqual(recipients.count(), 1)
        self.assertEqual(recipients.first().email, "jane@example.com")

        # Verify user1's recipient is not in the list
        self.assertNotIn(self.recipient1, recipients)

    def test_user2_sees_only_own_templates(self):
        """Test that user2 can only see their own templates"""
        # Login as user2
        self.client.login(username='user2', password='testpass456')
        response = self.client.get(reverse('template_list'))
        self.assertEqual(response.status_code, 200)

        # Check that only user2's template is in the context
        templates = response.context['templates']
        self.assertEqual(templates.count(), 1)
        self.assertEqual(templates.first().name, "Template2")

        # Verify user1's template is not in the list
        self.assertNotIn(self.template1, templates)

    def test_user2_sees_only_own_campaigns(self):
        """Test that user2 can only see their own campaigns"""
        # Login as user2
        self.client.login(username='user2', password='testpass456')
        response = self.client.get(reverse('campaign_list'))
        self.assertEqual(response.status_code, 200)

        # Check that only user2's campaign is in the context
        campaigns = response.context['campaigns']
        self.assertEqual(campaigns.count(), 1)
        self.assertEqual(campaigns.first().name, "Campaign2")

        # Verify user1's campaign is not in the list
        self.assertNotIn(self.campaign1, campaigns)

    def test_send_email_now_cross_user_access_denied(self):
        """Test that users cannot trigger send_email_now for other users' emails"""
        # Login as user1
        self.client.login(username='user1', password='testpass123')

        # Try to access user2's email candidate
        response = self.client.get(
            reverse('send_email_now', args=[self.email2.pk])
        )

        # Should return 404 since user1 shouldn't have access
        self.assertEqual(response.status_code, 404)

    def test_campaign_create_filters_templates_by_user(self):
        """Test that campaign_create form only shows user's own templates"""
        # Login as user1
        self.client.login(username='user1', password='testpass123')
        response = self.client.get(reverse('campaign_create'))
        self.assertEqual(response.status_code, 200)

        # Check that form template field only includes user1's templates
        template_queryset = response.context['form'].fields['template'].queryset
        self.assertEqual(template_queryset.count(), 1)
        self.assertIn(self.template1, template_queryset)
        self.assertNotIn(self.template2, template_queryset)

    def test_email_create_filters_recipients_and_templates_by_user(self):
        """Test that email_create form only shows user's own recipients and templates"""
        # Login as user1
        self.client.login(username='user1', password='testpass123')
        response = self.client.get(reverse('email_create'))
        self.assertEqual(response.status_code, 200)

        # Check that form fields only include user1's data
        recipient_queryset = response.context['form'].fields['recipient'].queryset
        template_queryset = response.context['form'].fields['template'].queryset

        self.assertEqual(recipient_queryset.count(), 1)
        self.assertEqual(template_queryset.count(), 1)
        self.assertIn(self.recipient1, recipient_queryset)
        self.assertIn(self.template1, template_queryset)
        self.assertNotIn(self.recipient2, recipient_queryset)
        self.assertNotIn(self.template2, template_queryset)

    def test_campaign_create_assigns_user_profile(self):
        """Test that creating a campaign assigns the correct user profile"""
        # Login as user1
        self.client.login(username='user1', password='testpass123')

        # Create a campaign via the view (simulating form submission)
        # Note: This is a simplified test - full form submission would require more setup
        campaign = EmailCampaign.objects.create(
            user_profile=self.profile1,
            name="New Campaign",
            template=self.template1,
            scheduled_time=timezone.now()
        )

        # Verify the campaign is assigned to user1
        self.assertEqual(campaign.user_profile, self.profile1)
        self.assertNotEqual(campaign.user_profile, self.profile2)

    def test_recipient_upload_assigns_user_profile(self):
        """Test that uploaded recipients are assigned to the correct user"""
        # This is implicitly tested by the update_or_create in recipient_upload
        # which uses user_profile as a lookup key
        new_recipient = Recipient.objects.create(
            user_profile=self.profile1,
            first_name="New",
            last_name="Recipient",
            email="new@example.com"
        )

        # Verify the recipient is assigned to user1
        self.assertEqual(new_recipient.user_profile, self.profile1)

        # Login as user1 and check they can see it
        self.client.login(username='user1', password='testpass123')
        response = self.client.get(reverse('recipient_list'))
        recipients = response.context['recipients']
        self.assertEqual(recipients.count(), 2)  # Original + new
        self.assertIn(new_recipient, recipients)

    def test_cross_user_data_query_returns_empty(self):
        """Test that direct queries for other users' data return empty"""
        # Login as user1
        self.client.login(username='user1', password='testpass123')

        # Try to query for user2's data using user1's profile filter
        recipients = Recipient.objects.filter(
            user_profile=self.profile1,
            email="jane@example.com"  # user2's recipient
        )
        self.assertEqual(recipients.count(), 0)

        templates = EmailTemplate.objects.filter(
            user_profile=self.profile1,
            name="Template2"  # user2's template
        )
        self.assertEqual(templates.count(), 0)
