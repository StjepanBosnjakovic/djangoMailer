from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from encrypted_model_fields.fields import EncryptedCharField
import uuid


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    smtp_host = models.CharField(max_length=255, blank=True)
    smtp_port = models.IntegerField(default=587)
    smtp_username = models.CharField(max_length=255, blank=True)
    smtp_password = EncryptedCharField(max_length=255, blank=True)
    use_tls = models.BooleanField(default=True)
    use_ssl = models.BooleanField(default=False)
    from_email = models.EmailField()
    max_emails_per_hour = models.IntegerField(default=100)
    direct_send = models.BooleanField(
        default=False,
        help_text="Send emails directly to recipient mail servers without using SMTP relay"
    )

    def __str__(self):
        return f"{self.user.username}'s Profile"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


class EmailTemplate(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="email_templates")
    name = models.CharField(max_length=100)
    subject = models.CharField(max_length=255)
    body = models.TextField()

    def __str__(self):
        return self.name


class Recipient(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="recipients")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    company = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField()
    country = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    free_field1 = models.CharField(max_length=255, null=True, blank=True)
    free_field2 = models.CharField(max_length=255, null=True, blank=True)
    free_field3 = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        unique_together = ("user_profile", "email")  # Ensure unique email per user

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"


class EmailCampaign(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="email_campaigns")
    name = models.CharField(max_length=100)
    template = models.ForeignKey(EmailTemplate, on_delete=models.CASCADE)
    recipients = models.ManyToManyField(Recipient)
    scheduled_time = models.DateTimeField()

    def __str__(self):
        return self.name


class EmailLog(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="email_logs")
    recipient = models.EmailField()
    campaign = models.ForeignKey(EmailCampaign, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=10)
    error_message = models.TextField(blank=True, null=True)
    sent_time = models.DateTimeField()

    def __str__(self):
        return f"{self.recipient} - {self.status}"


class EmailSendCandidate(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="email_send_candidates")
    recipient = models.ForeignKey(Recipient, on_delete=models.CASCADE)
    template = models.ForeignKey(EmailTemplate, on_delete=models.CASCADE)
    scheduled_time = models.DateTimeField()
    sent = models.BooleanField(default=False)
    sent_time = models.DateTimeField(null=True, blank=True)
    campaign = models.ForeignKey(EmailCampaign, on_delete=models.CASCADE, null=True, blank=True)
    tracking_id = models.UUIDField(default=uuid.uuid4, editable=False, db_index=True)

    def __str__(self):
        return f"{self.recipient.email} - {self.template.name}"

    def save(self, *args, **kwargs):
        # Ensure tracking_id is unique
        if not self.tracking_id:
            self.tracking_id = uuid.uuid4()
        super().save(*args, **kwargs)


class EmailEvent(models.Model):
    """
    Tracks all email delivery events for detailed analytics.
    Supports: sent, delivered, opened, clicked, bounced, failed events.
    """
    EVENT_TYPES = [
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('opened', 'Opened'),
        ('clicked', 'Clicked'),
        ('bounced', 'Bounced'),
        ('failed', 'Failed'),
        ('complained', 'Spam Complaint'),
    ]

    email_candidate = models.ForeignKey(
        EmailSendCandidate,
        on_delete=models.CASCADE,
        related_name="events"
    )
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, db_index=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    user_agent = models.TextField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)  # For additional event data

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['email_candidate', 'event_type']),
            models.Index(fields=['event_type', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.email_candidate.recipient.email} - {self.event_type} at {self.timestamp}"


class CampaignStatistics(models.Model):
    """
    Aggregated statistics for email campaigns.
    Updated periodically or on-demand for performance.
    """
    campaign = models.OneToOneField(
        EmailCampaign,
        on_delete=models.CASCADE,
        related_name="statistics"
    )

    # Counts
    total_recipients = models.IntegerField(default=0)
    sent_count = models.IntegerField(default=0)
    delivered_count = models.IntegerField(default=0)
    opened_count = models.IntegerField(default=0)
    clicked_count = models.IntegerField(default=0)
    bounced_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)
    complained_count = models.IntegerField(default=0)

    # Unique counts (for opens and clicks, count unique recipients only)
    unique_opens = models.IntegerField(default=0)
    unique_clicks = models.IntegerField(default=0)

    # Rates (calculated fields, stored for performance)
    delivery_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)  # delivered/sent
    open_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)  # opened/delivered
    click_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)  # clicked/delivered
    bounce_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)  # bounced/sent

    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Statistics for {self.campaign.name}"

    def update_statistics(self):
        """
        Recalculate all statistics from EmailEvent data.
        """
        from django.db.models import Count, Q

        candidates = self.campaign.emailsendcandidate_set.all()
        self.total_recipients = candidates.count()

        # Count events by type
        self.sent_count = candidates.filter(events__event_type='sent').distinct().count()
        self.delivered_count = candidates.filter(events__event_type='delivered').distinct().count()
        self.bounced_count = candidates.filter(events__event_type='bounced').distinct().count()
        self.failed_count = candidates.filter(events__event_type='failed').distinct().count()
        self.complained_count = candidates.filter(events__event_type='complained').distinct().count()

        # Unique opens and clicks
        self.unique_opens = candidates.filter(events__event_type='opened').distinct().count()
        self.unique_clicks = candidates.filter(events__event_type='clicked').distinct().count()

        # Total opens and clicks (including multiple opens/clicks per recipient)
        self.opened_count = EmailEvent.objects.filter(
            email_candidate__campaign=self.campaign,
            event_type='opened'
        ).count()
        self.clicked_count = EmailEvent.objects.filter(
            email_candidate__campaign=self.campaign,
            event_type='clicked'
        ).count()

        # Calculate rates
        if self.sent_count > 0:
            self.delivery_rate = round((self.delivered_count / self.sent_count) * 100, 2)
            self.bounce_rate = round((self.bounced_count / self.sent_count) * 100, 2)

        if self.delivered_count > 0:
            self.open_rate = round((self.unique_opens / self.delivered_count) * 100, 2)
            self.click_rate = round((self.unique_clicks / self.delivered_count) * 100, 2)

        self.save()
