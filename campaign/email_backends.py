import dns.resolver
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate, make_msgid
from django.core.mail.backends.base import BaseEmailBackend

logger = logging.getLogger(__name__)


class DirectEmailBackend(BaseEmailBackend):
    """
    Email backend that sends emails directly to recipient mail servers
    without using a third-party SMTP relay.

    This backend:
    1. Looks up MX records for the recipient's domain
    2. Connects directly to the recipient's mail server
    3. Sends the email without authentication

    Note: This may have deliverability issues due to SPF/DKIM/DMARC
    and may be blocked by recipient servers.
    """

    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        self.from_email = kwargs.get('from_email', None)

    def send_messages(self, email_messages):
        """
        Send one or more EmailMessage objects and return the number of sent messages.
        """
        if not email_messages:
            return 0

        num_sent = 0
        for message in email_messages:
            try:
                sent = self._send(message)
                if sent:
                    num_sent += 1
            except Exception as e:
                logger.error(f"Failed to send email to {message.to}: {str(e)}")
                if not self.fail_silently:
                    raise

        return num_sent

    def _send(self, message):
        """
        Send a single email message.
        """
        if not message.recipients():
            return False

        from_email = message.from_email or self.from_email
        if not from_email:
            raise ValueError("from_email must be specified")

        # Group recipients by domain for efficiency
        recipients_by_domain = {}
        for recipient in message.recipients():
            domain = recipient.split('@')[-1]
            if domain not in recipients_by_domain:
                recipients_by_domain[domain] = []
            recipients_by_domain[domain].append(recipient)

        # Send to each domain
        all_sent = True
        for domain, recipients in recipients_by_domain.items():
            try:
                mx_records = self._get_mx_records(domain)
                if not mx_records:
                    logger.error(f"No MX records found for domain: {domain}")
                    all_sent = False
                    continue

                # Try each MX server in order of priority
                sent = False
                for priority, mx_host in mx_records:
                    try:
                        self._send_to_mx(mx_host, from_email, recipients, message)
                        sent = True
                        logger.info(f"Successfully sent email to {recipients} via {mx_host}")
                        break
                    except Exception as e:
                        logger.warning(f"Failed to send via {mx_host}: {str(e)}")
                        continue

                if not sent:
                    logger.error(f"Failed to send to {recipients} - all MX servers failed")
                    all_sent = False

            except Exception as e:
                logger.error(f"Error sending to domain {domain}: {str(e)}")
                all_sent = False
                if not self.fail_silently:
                    raise

        return all_sent

    def _get_mx_records(self, domain):
        """
        Get MX records for a domain, sorted by priority.
        Returns list of (priority, hostname) tuples.
        """
        try:
            mx_records = dns.resolver.resolve(domain, 'MX')
            records = [(record.preference, str(record.exchange).rstrip('.'))
                      for record in mx_records]
            return sorted(records, key=lambda x: x[0])
        except dns.resolver.NXDOMAIN:
            logger.error(f"Domain does not exist: {domain}")
            return []
        except dns.resolver.NoAnswer:
            logger.error(f"No MX records found for domain: {domain}")
            return []
        except Exception as e:
            logger.error(f"Error looking up MX records for {domain}: {str(e)}")
            return []

    def _send_to_mx(self, mx_host, from_email, recipients, message):
        """
        Send email to a specific MX server.
        """
        # Try port 25 (standard SMTP)
        with smtplib.SMTP(mx_host, 25, timeout=30) as smtp:
            smtp.ehlo()

            # Try to use STARTTLS if available
            try:
                if smtp.has_extn('STARTTLS'):
                    smtp.starttls()
                    smtp.ehlo()
            except Exception as e:
                logger.warning(f"STARTTLS failed, continuing without encryption: {str(e)}")

            # Send the email
            smtp.sendmail(
                from_email,
                recipients,
                message.message().as_bytes()
            )
