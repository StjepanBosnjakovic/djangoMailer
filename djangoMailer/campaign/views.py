from django.shortcuts import render, redirect
from .models import EmailTemplate, EmailSendCandidate, EmailLog, Recipient, EmailCampaign
from .forms import EmailTemplateForm, EmailForm, EmailCampaignForm, RecipientFilterForm
from django.core.paginator import Paginator
import csv, io
from django.contrib import messages
from django.utils.encoding import smart_str
from .forms import RecipientUploadForm
from django.shortcuts import get_object_or_404


def home(request):
    recipient_count = Recipient.objects.count()
    template_count = EmailTemplate.objects.count()
    email_count = EmailSendCandidate.objects.count()
    email_sent_count = EmailSendCandidate.objects.filter(sent=True).count()
    email_pending_count = EmailSendCandidate.objects.filter(sent=False).count()
    email_log_count = EmailLog.objects.count()

    context = {
        'recipient_count': recipient_count,
        'template_count': template_count,
        'email_count': email_count,
        'email_sent_count': email_sent_count,
        'email_pending_count': email_pending_count,
        'email_log_count': email_log_count,
    }
    return render(request, 'home.html', context)

def template_list(request):
    templates = EmailTemplate.objects.all()
    return render(request, 'template_list.html', {'templates': templates})

def template_create(request):
    if request.method == 'POST':
        form = EmailTemplateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('template_list')
    else:
        form = EmailTemplateForm()
    return render(request, 'template_form.html', {'form': form})

def queue_list(request):
    queues = EmailSendCandidate.objects.filter(sent=False)
    return render(request, 'queue_list.html', {'queues': queues})

def queue_create(request):
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('queue_list')
    else:
        form = EmailForm()
    return render(request, 'queue_form.html', {'form': form})

def log_list(request):
    logs = EmailLog.objects.all()
    return render(request, 'log_list.html', {'logs': logs})

def recipient_upload(request):
    if request.method == 'POST':
        form = RecipientUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']

            # Check if the file is a CSV
            if not csv_file.name.endswith('.csv'):
                messages.error(request, 'This is not a CSV file')
                return redirect('recipient_upload')

            # Read the file
            data_set = csv_file.read().decode('UTF-8')
            io_string = io.StringIO(data_set)
            next(io_string)  # Skip the header row

            for row in csv.reader(io_string, delimiter=',', quotechar='"'):
                _, created = Recipient.objects.update_or_create(
                    email=row[3],
                    defaults={
                        'first_name': row[0],
                        'last_name': row[1],
                        'company': row[2],
                        'country': row[4],
                        'city': row[5],
                        'free_field1': row[6],
                        'free_field2': row[7],
                        'free_field3': row[8],
                    }
                )
            messages.success(request, 'Recipients imported successfully')
            return redirect('recipient_list')
    else:
        form = RecipientUploadForm()
    return render(request, 'recipient_upload.html', {'form': form})

def recipient_list(request):
    recipients = Recipient.objects.all()
    return render(request, 'recipient_list.html', {'recipients': recipients})



def email_list(request):
    emails = EmailSendCandidate.objects.filter(sent=False)
    return render(request, 'email_list.html', {'emails': emails})

def email_create(request):
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('email_list')
    else:
        form = EmailForm()
    return render(request, 'email_form.html', {'form': form})


def campaign_create(request):
    if request.method == 'POST':
        form = EmailCampaignForm(request.POST)
        filter_form = RecipientFilterForm(request.POST)
        if form.is_valid():
            campaign = form.save()
            recipient_ids = request.POST.get('recipients', '')
            recipient_ids_list = recipient_ids.split(',')
            recipients = Recipient.objects.filter(id__in=recipient_ids_list)
            email_send_candidates = [
                EmailSendCandidate(
                    campaign=campaign,
                    recipient=recipient,
                    scheduled_time=campaign.scheduled_time,
                )
                for recipient in recipients
            ]
            EmailSendCandidate.objects.bulk_create(email_send_candidates)
            return redirect('campaign_list')
    else:
        form = EmailCampaignForm()
        filter_form = RecipientFilterForm()
        recipients = Recipient.objects.all()

    # Handle filtering
    if request.method == 'GET' and 'filter' in request.GET:
        filter_form = RecipientFilterForm(request.GET)
        if filter_form.is_valid():
            recipients = filter_recipients(filter_form.cleaned_data)
    else:
        recipients = Recipient.objects.all()

    # Implement pagination
    paginator = Paginator(recipients, 25)  # Show 25 recipients per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'campaign_form.html', {
        'form': form,
        'filter_form': filter_form,
        'recipients': page_obj.object_list,
        'page_obj': page_obj,
    })

def filter_recipients(filters):
    qs = Recipient.objects.all()
    if filters.get('first_name'):
        qs = qs.filter(first_name__icontains=filters['first_name'])
    if filters.get('last_name'):
        qs = qs.filter(last_name__icontains=filters['last_name'])
    if filters.get('company'):
        qs = qs.filter(company__icontains=filters['company'])
    if filters.get('email'):
        qs = qs.filter(email__icontains=filters['email'])
    if filters.get('country'):
        qs = qs.filter(country__icontains=filters['country'])
    if filters.get('city'):
        qs = qs.filter(city__icontains=filters['city'])
    if filters.get('free_field1'):
        qs = qs.filter(free_field1__icontains=filters['free_field1'])
    if filters.get('free_field2'):
        qs = qs.filter(free_field2__icontains=filters['free_field2'])
    if filters.get('free_field3'):
        qs = qs.filter(free_field3__icontains=filters['free_field3'])
    return qs

def campaign_list(request):
    campaigns = EmailCampaign.objects.all()
    return render(request, 'campaign_list.html', {'campaigns': campaigns})

