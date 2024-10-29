from django.contrib import admin
from .models import EmailTemplate, EmailSendCandidate, EmailLog, Recipient, EmailCampaign

admin.site.register(EmailTemplate)
admin.site.register(EmailSendCandidate)
admin.site.register(EmailLog)
admin.site.register(Recipient)
admin.site.register(EmailCampaign)
