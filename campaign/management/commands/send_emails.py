# campaign/management/commands/send_emails.py

from django.core.mail import EmailMessage
from django.core.mail.backends.smtp import EmailBackend
from django.core.management.base import BaseCommand
from django.utils import timezone

from campaign.models import EmailLog, EmailSendCandidate, UserProfile


class Command(BaseCommand):
    help = "Send queued emails"

    def handle(self, *args, **options):
        now = timezone.now()

        # Get distinct users who have pending emails
        users_with_pending_emails = (
            EmailSendCandidate.objects.filter(sent=False, scheduled_time__lte=now)
            .values_list("campaign__user", flat=True)
            .distinct()
        )

        for user_id in users_with_pending_emails:
            user_profile = UserProfile.objects.get(user__id=user_id)
            user = user_profile.user

            max_emails_per_hour = user_profile.max_emails_per_hour

            one_hour_ago = now - timezone.timedelta(hours=1)
            emails_sent_last_hour = EmailLog.objects.filter(campaign__user=user, sent_time__gte=one_hour_ago).count()
            emails_remaining = max_emails_per_hour - emails_sent_last_hour
            if emails_remaining <= 0:
                self.stdout.write(f"Hourly email limit reached for user {user.username}.")
                continue

            emails_to_send = EmailSendCandidate.objects.filter(
                sent=False, scheduled_time__lte=now, campaign__user=user
            ).order_by("scheduled_time")[:emails_remaining]

            for email_candidate in emails_to_send:
                try:
                    # Use user-specific SMTP settings
                    backend = EmailBackend(
                        host=user_profile.smtp_host,
                        port=user_profile.smtp_port,
                        username=user_profile.smtp_username,
                        password=user_profile.smtp_password,
                        use_tls=user_profile.use_tls,
                        use_ssl=user_profile.use_ssl,
                        fail_silently=False,
                    )

                    # Personalize the email body if necessary
                    message = email_candidate.campaign.template.body.format(
                        first_name=email_candidate.recipient.first_name,
                        last_name=email_candidate.recipient.last_name,
                        company=email_candidate.recipient.company,
                        free_field1=email_candidate.recipient.free_field1,
                        free_field2=email_candidate.recipient.free_field2,
                        free_field3=email_candidate.recipient.free_field3,
                    )

                    email = EmailMessage(
                        subject=email_candidate.campaign.template.subject,
                        body=message,
                        from_email=user_profile.from_email,
                        to=[email_candidate.recipient.email],
                        connection=backend,
                    )
                    email.send()

                    email_candidate.sent = True
                    email_candidate.sent_time = now
                    email_candidate.save()
                    EmailLog.objects.create(
                        recipient=email_candidate.recipient.email,
                        campaign=email_candidate.campaign,
                        status="Sent",
                        sent_time=now,
                    )
                    self.stdout.write(f"Email sent to {email_candidate.recipient.email} for user {user.username}")
                except Exception as e:
                    EmailLog.objects.create(
                        recipient=email_candidate.recipient.email,
                        campaign=email_candidate.campaign,
                        status="Failed",
                        error_message=str(e),
                        sent_time=now,
                    )
                    self.stdout.write(
                        f"Failed to send email to {email_candidate.recipient.email} for user {user.username}: {e}"
                    )
