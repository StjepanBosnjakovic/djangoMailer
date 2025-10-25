from django.contrib import admin

from .models import (
    EmailCampaign, EmailLog, EmailSendCandidate, EmailTemplate,
    Recipient, UserProfile, EmailEvent, CampaignStatistics
)


@admin.register(EmailEvent)
class EmailEventAdmin(admin.ModelAdmin):
    list_display = ('email_candidate', 'event_type', 'timestamp', 'ip_address')
    list_filter = ('event_type', 'timestamp')
    search_fields = ('email_candidate__recipient__email',)
    readonly_fields = ('timestamp',)


@admin.register(CampaignStatistics)
class CampaignStatisticsAdmin(admin.ModelAdmin):
    list_display = (
        'campaign', 'sent_count', 'delivered_count', 'unique_opens',
        'unique_clicks', 'open_rate', 'click_rate', 'bounce_rate', 'last_updated'
    )
    readonly_fields = ('last_updated',)
    actions = ['refresh_statistics']

    def refresh_statistics(self, request, queryset):
        for stat in queryset:
            stat.update_statistics()
        self.message_user(request, f"Successfully updated {queryset.count()} campaign statistics.")
    refresh_statistics.short_description = "Refresh selected campaign statistics"


admin.site.register(EmailTemplate)
admin.site.register(EmailSendCandidate)
admin.site.register(EmailLog)
admin.site.register(Recipient)
admin.site.register(EmailCampaign)
admin.site.register(UserProfile)
