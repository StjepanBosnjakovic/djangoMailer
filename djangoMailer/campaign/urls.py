from django.urls import path
from . import views

urlpatterns = [
    path('templates/', views.template_list, name='template_list'),
    path('templates/create/', views.template_create, name='template_create'),
    path('queues/', views.queue_list, name='queue_list'),
    path('queues/create/', views.queue_create, name='queue_create'),
    path('logs/', views.log_list, name='log_list'),
    path('recipients/', views.recipient_list, name='recipient_list'),
    path('recipients/upload/', views.recipient_upload, name='recipient_upload'),
    path('emails/', views.email_list, name='email_list'),
    path('emails/create/', views.email_create, name='email_create'),
]
