from django.contrib import admin
from .models import EmailTemplate, EmailSendCandidate, EmailLog, Recipient

admin.site.register(EmailTemplate)
admin.site.register(EmailSendCandidate)
admin.site.register(EmailLog)
admin.site.register(Recipient)

