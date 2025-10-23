from django.contrib import admin

from .models import EmailCampaign, EmailLog, EmailSendCandidate, EmailTemplate, Recipient, UserProfile

admin.site.register(EmailTemplate)
admin.site.register(EmailSendCandidate)
admin.site.register(EmailLog)
admin.site.register(Recipient)
admin.site.register(EmailCampaign)
admin.site.register(UserProfile)
