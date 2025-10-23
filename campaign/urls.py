from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),  # Home page
    path("templates/", views.template_list, name="template_list"),
    path("templates/create/", views.template_create, name="template_create"),
    path("queues/", views.queue_list, name="queue_list"),
    path("queues/create/", views.queue_create, name="queue_create"),
    path("logs/", views.log_list, name="log_list"),
    path("recipients/", views.recipient_list, name="recipient_list"),
    path("recipients/upload/", views.recipient_upload, name="recipient_upload"),
    path("emails/", views.email_list, name="email_list"),
    path("email_send_candidate/<int:pk>/send_now/", views.send_email_now, name="send_email_now"),
    path("emails/create/", views.email_create, name="email_create"),
    path("campaigns/", views.campaign_list, name="campaign_list"),
    path("campaigns/create/", views.campaign_create, name="campaign_create"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
]
