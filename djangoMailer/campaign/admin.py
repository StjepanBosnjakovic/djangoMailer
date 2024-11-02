from django.contrib import admin
from .models import EmailTemplate, EmailSendCandidate, EmailLog, Recipient, EmailCampaign, UserProfile

admin.site.register(EmailTemplate)
admin.site.register(EmailSendCandidate)
admin.site.register(EmailLog)
admin.site.register(Recipient)
admin.site.register(EmailCampaign)
admin.site.register(UserProfile)

