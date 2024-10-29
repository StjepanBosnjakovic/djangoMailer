from django.shortcuts import render, redirect
from .models import EmailTemplate, EmailSendCandidate, EmailLog, Recipient
from .forms import EmailTemplateForm, EmailForm
import csv, io
from django.contrib import messages
from django.utils.encoding import smart_str
from .forms import RecipientUploadForm


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