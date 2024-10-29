from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from campaign.models import Email, EmailLog
from django.conf import settings

MAX_EMAILS_PER_HOUR = 100

class Command(BaseCommand):
    help = 'Send queued emails'

    def handle(self, *args, **options):
        now = timezone.now()
        one_hour_ago = now - timezone.timedelta(hours=1)
        emails_sent_last_hour = EmailLog.objects.filter(sent_time__gte=one_hour_ago).count()
        emails_remaining = MAX_EMAILS_PER_HOUR - emails_sent_last_hour
        if emails_remaining <= 0:
            self.stdout.write('Hourly email limit reached.')
            return

        emails_to_send = Email.objects.filter(sent=False, scheduled_time__lte=now)[:emails_remaining]
        for email in emails_to_send:
            try:
                # Personalize the email body if necessary
                message = email.template.body.format(
                    first_name=email.recipient.first_name,
                    last_name=email.recipient.last_name,
                    company=email.recipient.company,
                    free_field1=email.recipient.free_field1,
                    free_field2=email.recipient.free_field2,
                    free_field3=email.recipient.free_field3,
                )

                send_mail(
                    subject=email.template.subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email.recipient.email],
                )
                email.sent = True
                email.sent_time = now
                email.save()
                EmailLog.objects.create(
                    recipient=email.recipient.email,
                    template=email.template,
                    status='Sent',
                )
                self.stdout.write(f"Email sent to {email.recipient.email}")
            except Exception as e:
                EmailLog.objects.create(
                    recipient=email.recipient.email,
                    template=email.template,
                    status='Failed',
                    error_message=str(e),
                )
                self.stdout.write(f"Failed to send email to {email.recipient.email}: {e}")
