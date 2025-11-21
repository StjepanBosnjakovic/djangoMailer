from django.urls import path

from . import views
from . import tracking_views

urlpatterns = [
    path("", views.home, name="home"),  # Home page
    path("templates/", views.template_list, name="template_list"),
    path("templates/create/", views.template_create, name="template_create"),
    path("queues/", views.queue_list, name="queue_list"),
    path("queues/create/", views.queue_create, name="queue_create"),
    path("logs/", views.log_list, name="log_list"),
    path("recipients/", views.recipient_list, name="recipient_list"),
    path("recipients/upload/", views.recipient_upload, name="recipient_upload"),
    path("recipients/download-example/", views.download_example_csv, name="download_example_csv"),
    path("emails/", views.email_list, name="email_list"),
    path("email_send_candidate/<int:pk>/send_now/", views.send_email_now, name="send_email_now"),
    path("emails/create/", views.email_create, name="email_create"),
    path("campaigns/", views.campaign_list, name="campaign_list"),
    path("campaigns/create/", views.campaign_create, name="campaign_create"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),

    # Email tracking endpoints
    path("track/pixel/<uuid:tracking_id>/", tracking_views.tracking_pixel, name="email_tracking_pixel"),
    path("track/click/<uuid:tracking_id>/", tracking_views.tracking_click, name="email_tracking_click"),
    path("track/bounce/", tracking_views.bounce_webhook, name="email_bounce_webhook"),
    path("track/delivery/", tracking_views.delivery_webhook, name="email_delivery_webhook"),

    # Campaign statistics
    path("campaigns/<int:campaign_id>/statistics/", views.campaign_statistics, name="campaign_statistics"),
]
