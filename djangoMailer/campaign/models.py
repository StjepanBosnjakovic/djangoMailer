from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class EmailTemplate(models.Model):
    name = models.CharField(max_length=100)
    subject = models.CharField(max_length=255)
    body = models.TextField()

    def __str__(self):
        return self.name
    
class Recipient(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    company = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(unique=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    free_field1 = models.CharField(max_length=255, null=True, blank=True)
    free_field2 = models.CharField(max_length=255, null=True, blank=True)
    free_field3 = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

class EmailSendCandidate(models.Model):
    recipient = models.ForeignKey(Recipient, on_delete=models.CASCADE)
    template = models.ForeignKey(EmailTemplate, on_delete=models.CASCADE)
    scheduled_time = models.DateTimeField()
    sent = models.BooleanField(default=False)
    sent_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.recipient.email} - {self.template.name}"

class EmailLog(models.Model):
    recipient = models.EmailField()
    template = models.ForeignKey(EmailTemplate, on_delete=models.CASCADE)
    sent_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50)  # 'Sent' or 'Failed'
    error_message = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.recipient} - {self.status}"
    
class EmailCampaign(models.Model):
    name = models.CharField(max_length=100)
    template = models.ForeignKey(EmailTemplate, on_delete=models.CASCADE)
    recipients = models.ManyToManyField(Recipient)
    scheduled_time = models.DateTimeField()

    def __str__(self):
        return self.name



class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    smtp_host = models.CharField(max_length=255)
    smtp_port = models.IntegerField(default=587)
    smtp_username = models.CharField(max_length=255)
    smtp_password = models.CharField(max_length=255)
    use_tls = models.BooleanField(default=True)
    use_ssl = models.BooleanField(default=False)
    from_email = models.EmailField()

    def __str__(self):
        return f"{self.user.username}'s Profile"
    
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)