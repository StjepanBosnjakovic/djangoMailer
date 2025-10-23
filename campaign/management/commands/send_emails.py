# campaign/management/commands/send_emails.py

from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.core.mail.backends.smtp import EmailBackend
from django.core.management.base import BaseCommand
from django.utils import timezone

from campaign.models import EmailLog, EmailSendCandidate, UserProfile, EmailEvent
from campaign.email_backends import DirectEmailBackend
from campaign.tracking import add_tracking_pixel, replace_links_with_tracking, convert_to_html


class Command(BaseCommand):
    help = "Send queued emails"

    def handle(self, *args, **options):
        now = timezone.now()

        # Get distinct user profiles who have pending emails
        user_profile_ids = (
            EmailSendCandidate.objects.filter(sent=False, scheduled_time__lte=now)
            .values_list("user_profile", flat=True)
            .distinct()
        )

        for user_profile_id in user_profile_ids:
            user_profile = UserProfile.objects.get(id=user_profile_id)
            user = user_profile.user

            max_emails_per_hour = user_profile.max_emails_per_hour

            one_hour_ago = now - timezone.timedelta(hours=1)
            emails_sent_last_hour = EmailLog.objects.filter(user_profile=user_profile, sent_time__gte=one_hour_ago).count()
            emails_remaining = max_emails_per_hour - emails_sent_last_hour
            if emails_remaining <= 0:
                self.stdout.write(f"Hourly email limit reached for user {user.username}.")
                continue

            emails_to_send = EmailSendCandidate.objects.filter(
                sent=False, scheduled_time__lte=now, user_profile=user_profile
            ).order_by("scheduled_time")[:emails_remaining]

            for email_candidate in emails_to_send:
                try:
                    # Use direct sending or user-specific SMTP settings
                    if user_profile.direct_send:
                        backend = DirectEmailBackend(
                            fail_silently=False,
                            from_email=user_profile.from_email,
                        )
                    else:
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
                    plain_message = email_candidate.campaign.template.body.format(
                        first_name=email_candidate.recipient.first_name or '',
                        last_name=email_candidate.recipient.last_name or '',
                        company=email_candidate.recipient.company or '',
                        free_field1=email_candidate.recipient.free_field1 or '',
                        free_field2=email_candidate.recipient.free_field2 or '',
                        free_field3=email_candidate.recipient.free_field3 or '',
                    )

                    # Convert to HTML and add tracking
                    html_message = convert_to_html(plain_message)
                    html_message = add_tracking_pixel(html_message, email_candidate.tracking_id)
                    html_message = replace_links_with_tracking(html_message, email_candidate.tracking_id)

                    # Create multipart email with plain text and HTML
                    email = EmailMultiAlternatives(
                        subject=email_candidate.campaign.template.subject,
                        body=plain_message,  # Plain text version
                        from_email=user_profile.from_email,
                        to=[email_candidate.recipient.email],
                        connection=backend,
                    )
                    email.attach_alternative(html_message, "text/html")
                    email.send()

                    email_candidate.sent = True
                    email_candidate.sent_time = now
                    email_candidate.save()

                    # Create EmailLog (for backward compatibility)
                    EmailLog.objects.create(
                        user_profile=user_profile,
                        recipient=email_candidate.recipient.email,
                        campaign=email_candidate.campaign,
                        status="Sent",
                        sent_time=now,
                    )

                    # Create EmailEvent for tracking
                    EmailEvent.objects.create(
                        email_candidate=email_candidate,
                        event_type='sent',
                        metadata={'subject': email_candidate.campaign.template.subject}
                    )

                    self.stdout.write(f"Email sent to {email_candidate.recipient.email} for user {user.username}")
                except Exception as e:
                    # Create EmailLog (for backward compatibility)
                    EmailLog.objects.create(
                        user_profile=user_profile,
                        recipient=email_candidate.recipient.email,
                        campaign=email_candidate.campaign,
                        status="Failed",
                        error_message=str(e),
                        sent_time=now,
                    )

                    # Create EmailEvent for tracking
                    EmailEvent.objects.create(
                        email_candidate=email_candidate,
                        event_type='failed',
                        metadata={'error': str(e)}
                    )

                    self.stdout.write(
                        f"Failed to send email to {email_candidate.recipient.email} for user {user.username}: {e}"
                    )
