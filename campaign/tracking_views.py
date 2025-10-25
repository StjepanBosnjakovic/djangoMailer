"""
Views for handling email tracking events: opens, clicks, and bounces.
"""
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from django.utils import timezone
from campaign.models import EmailSendCandidate, EmailEvent
import base64


def get_client_ip(request):
    """Extract client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@require_http_methods(["GET"])
def tracking_pixel(request, tracking_id):
    """
    Serve a 1x1 transparent pixel and record email open event.

    Args:
        request: Django request object
        tracking_id: UUID tracking ID of the email

    Returns:
        1x1 transparent GIF image
    """
    try:
        email_candidate = get_object_or_404(EmailSendCandidate, tracking_id=tracking_id)

        # Check if this email was already opened (for unique open tracking)
        already_opened = EmailEvent.objects.filter(
            email_candidate=email_candidate,
            event_type='opened'
        ).exists()

        # Record the open event
        EmailEvent.objects.create(
            email_candidate=email_candidate,
            event_type='opened',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            metadata={
                'first_open': not already_opened,
                'timestamp': timezone.now().isoformat()
            }
        )
    except Exception as e:
        # Silently fail - don't break the email viewing experience
        pass

    # Return a 1x1 transparent GIF
    # Base64 encoded 1x1 transparent GIF
    pixel = base64.b64decode(
        'R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7'
    )
    return HttpResponse(pixel, content_type='image/gif')


@require_http_methods(["GET"])
def tracking_click(request, tracking_id):
    """
    Track link clicks and redirect to the original URL.

    Args:
        request: Django request object
        tracking_id: UUID tracking ID of the email

    Returns:
        Redirect to the original URL
    """
    original_url = request.GET.get('url', '/')

    try:
        email_candidate = get_object_or_404(EmailSendCandidate, tracking_id=tracking_id)

        # Record the click event
        EmailEvent.objects.create(
            email_candidate=email_candidate,
            event_type='clicked',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            metadata={
                'url': original_url,
                'timestamp': timezone.now().isoformat()
            }
        )
    except Exception as e:
        # Silently fail and still redirect
        pass

    return HttpResponseRedirect(original_url)


@csrf_exempt
@require_http_methods(["POST"])
def bounce_webhook(request):
    """
    Handle bounce notifications from email service providers.

    This endpoint can receive bounce notifications from various ESP webhooks
    (SendGrid, Mailgun, AWS SES, etc.). The format varies by provider.

    Expected JSON payload (example):
    {
        "tracking_id": "uuid-here",
        "event": "bounced",
        "bounce_type": "hard|soft",
        "reason": "mailbox does not exist",
        "email": "recipient@example.com"
    }

    Returns:
        JSON response with status
    """
    import json

    try:
        data = json.loads(request.body)

        # Try to get tracking_id or email to identify the EmailSendCandidate
        tracking_id = data.get('tracking_id')
        recipient_email = data.get('email')

        email_candidate = None
        if tracking_id:
            try:
                email_candidate = EmailSendCandidate.objects.get(tracking_id=tracking_id)
            except EmailSendCandidate.DoesNotExist:
                pass

        if not email_candidate and recipient_email:
            # Try to find by recipient email (get the most recent one)
            email_candidate = EmailSendCandidate.objects.filter(
                recipient__email=recipient_email,
                sent=True
            ).order_by('-sent_time').first()

        if email_candidate:
            # Determine event type
            event_type = data.get('event', 'bounced')
            if event_type not in ['bounced', 'complained', 'failed']:
                event_type = 'bounced'

            # Record the event
            EmailEvent.objects.create(
                email_candidate=email_candidate,
                event_type=event_type,
                metadata={
                    'bounce_type': data.get('bounce_type', 'unknown'),
                    'reason': data.get('reason', ''),
                    'raw_data': data,
                    'timestamp': timezone.now().isoformat()
                }
            )

            return JsonResponse({'status': 'success', 'message': 'Event recorded'})
        else:
            return JsonResponse(
                {'status': 'error', 'message': 'Email candidate not found'},
                status=404
            )

    except Exception as e:
        return JsonResponse(
            {'status': 'error', 'message': str(e)},
            status=400
        )


@csrf_exempt
@require_http_methods(["POST"])
def delivery_webhook(request):
    """
    Handle delivery confirmation from email service providers.

    Expected JSON payload:
    {
        "tracking_id": "uuid-here",
        "event": "delivered",
        "email": "recipient@example.com",
        "timestamp": "2024-01-01T12:00:00Z"
    }

    Returns:
        JSON response with status
    """
    import json

    try:
        data = json.loads(request.body)

        tracking_id = data.get('tracking_id')
        recipient_email = data.get('email')

        email_candidate = None
        if tracking_id:
            try:
                email_candidate = EmailSendCandidate.objects.get(tracking_id=tracking_id)
            except EmailSendCandidate.DoesNotExist:
                pass

        if not email_candidate and recipient_email:
            email_candidate = EmailSendCandidate.objects.filter(
                recipient__email=recipient_email,
                sent=True
            ).order_by('-sent_time').first()

        if email_candidate:
            # Check if not already recorded
            if not EmailEvent.objects.filter(
                email_candidate=email_candidate,
                event_type='delivered'
            ).exists():
                EmailEvent.objects.create(
                    email_candidate=email_candidate,
                    event_type='delivered',
                    metadata={
                        'raw_data': data,
                        'timestamp': timezone.now().isoformat()
                    }
                )

            return JsonResponse({'status': 'success', 'message': 'Delivery recorded'})
        else:
            return JsonResponse(
                {'status': 'error', 'message': 'Email candidate not found'},
                status=404
            )

    except Exception as e:
        return JsonResponse(
            {'status': 'error', 'message': str(e)},
            status=400
        )
