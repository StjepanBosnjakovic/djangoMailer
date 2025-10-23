from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    smtp_host = models.CharField(max_length=255)
    smtp_port = models.IntegerField(default=587)
    smtp_username = models.CharField(max_length=255)
    smtp_password = models.CharField(max_length=255)
    use_tls = models.BooleanField(default=True)
    use_ssl = models.BooleanField(default=False)
    from_email = models.EmailField()
    max_emails_per_hour = models.IntegerField(default=100)

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

    def __str__(self):
        return f"{self.recipient.email} - {self.template.name}"
