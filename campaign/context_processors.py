from .models import EmailLog, EmailSendCandidate, EmailTemplate, Recipient


def statistics(request):
    return {
        "recipient_count": Recipient.objects.count(),
        "template_count": EmailTemplate.objects.count(),
        "email_count": EmailSendCandidate.objects.count(),
        "email_sent_count": EmailSendCandidate.objects.filter(sent=True).count(),
        "email_pending_count": EmailSendCandidate.objects.filter(sent=False).count(),
        "email_log_count": EmailLog.objects.count(),
    }
