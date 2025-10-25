# Email Delivery Tracking System

This guide explains the comprehensive email delivery tracking system implemented in djangoMailer. The system allows you to track sent, delivered, opened, clicked, and bounced emails to get detailed statistics and insights about your email campaigns.

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Architecture](#architecture)
4. [Configuration](#configuration)
5. [Usage](#usage)
6. [API Endpoints](#api-endpoints)
7. [Statistics](#statistics)
8. [Webhooks](#webhooks)

## Overview

The email tracking system provides comprehensive analytics for email campaigns by tracking various events throughout the email delivery lifecycle:

- **Sent**: Email was successfully sent from the server
- **Delivered**: Email was delivered to the recipient's mail server (via webhook)
- **Opened**: Recipient opened the email (tracked via pixel)
- **Clicked**: Recipient clicked a link in the email (tracked via redirect)
- **Bounced**: Email bounced (hard or soft bounce via webhook)
- **Failed**: Email sending failed
- **Complained**: Recipient marked email as spam (via webhook)

## Features

### 1. Automatic Tracking Pixel

Every email sent includes a 1x1 transparent tracking pixel that records when the email is opened. The pixel is automatically embedded in the HTML version of the email.

**How it works:**
- A unique tracking ID (UUID) is generated for each email
- The tracking pixel is embedded: `<img src="https://yourdomain.com/track/pixel/{tracking_id}/" />`
- When the recipient opens the email, the pixel is loaded and the open event is recorded

### 2. Click Tracking

All links in your emails are automatically replaced with tracking URLs that log the click event before redirecting to the original destination.

**How it works:**
- Original link: `https://example.com/page`
- Tracking link: `https://yourdomain.com/track/click/{tracking_id}/?url=https://example.com/page`
- The system logs the click and redirects the user to the original URL

### 3. Event Tracking

The `EmailEvent` model tracks all email-related events with detailed metadata:

```python
class EmailEvent(models.Model):
    email_candidate = ForeignKey(EmailSendCandidate)
    event_type = CharField(choices=['sent', 'delivered', 'opened', 'clicked', 'bounced', 'failed', 'complained'])
    timestamp = DateTimeField(auto_now_add=True)
    user_agent = TextField()  # Browser/email client information
    ip_address = GenericIPAddressField()  # Recipient IP address
    metadata = JSONField()  # Additional event-specific data
```

### 4. Campaign Statistics

The `CampaignStatistics` model provides aggregated statistics for each campaign:

- Total recipients
- Sent/delivered/bounced counts
- Unique opens and total opens
- Unique clicks and total clicks
- Delivery rate (delivered/sent × 100)
- Open rate (unique opens/delivered × 100)
- Click rate (unique clicks/delivered × 100)
- Bounce rate (bounced/sent × 100)

## Architecture

### Database Models

#### 1. EmailSendCandidate (Enhanced)
```python
class EmailSendCandidate(models.Model):
    # ... existing fields ...
    tracking_id = models.UUIDField(default=uuid.uuid4, editable=False, db_index=True)
```

Each email candidate now has a unique tracking ID used in all tracking URLs.

#### 2. EmailEvent (New)
```python
class EmailEvent(models.Model):
    email_candidate = ForeignKey(EmailSendCandidate)
    event_type = CharField(max_length=20)
    timestamp = DateTimeField(auto_now_add=True)
    user_agent = TextField(blank=True, null=True)
    ip_address = GenericIPAddressField(blank=True, null=True)
    metadata = JSONField(default=dict, blank=True)
```

Stores all tracking events with detailed context.

#### 3. CampaignStatistics (New)
```python
class CampaignStatistics(models.Model):
    campaign = OneToOneField(EmailCampaign)
    # Counts
    total_recipients = IntegerField(default=0)
    sent_count = IntegerField(default=0)
    delivered_count = IntegerField(default=0)
    opened_count = IntegerField(default=0)
    clicked_count = IntegerField(default=0)
    bounced_count = IntegerField(default=0)
    # Rates
    delivery_rate = DecimalField(max_digits=5, decimal_places=2)
    open_rate = DecimalField(max_digits=5, decimal_places=2)
    click_rate = DecimalField(max_digits=5, decimal_places=2)
    bounce_rate = DecimalField(max_digits=5, decimal_places=2)
```

Aggregated statistics for performance optimization.

### Tracking Flow

```
1. Email Created → tracking_id generated (UUID)
2. Email Sent → 'sent' event created
                ↓
3. Email Delivered → 'delivered' event (via webhook)
                ↓
4. Email Opened → 'opened' event (via tracking pixel)
                ↓
5. Link Clicked → 'clicked' event (via tracking redirect)
```

## Configuration

### 1. Set SITE_URL

In your `.env` file or environment variables:

```bash
SITE_URL=https://yourdomain.com
```

This URL is used to generate tracking pixel and click tracking URLs. For development:

```bash
SITE_URL=http://localhost:8000
```

### 2. Database Migration

Run migrations to create the new tracking tables:

```bash
python manage.py migrate
```

### 3. Email Template Format

Your email templates should be in HTML or will be automatically converted. Plain text emails are converted to HTML with `<br>` tags for line breaks.

## Usage

### Viewing Campaign Statistics

1. Navigate to the **Campaigns** page
2. Click **"View Statistics"** for any campaign
3. The statistics page shows:
   - Key metrics (sent, delivered, opened, clicked, bounced)
   - Delivery, open, click, and bounce rates
   - Top clicked links
   - Opens over time
   - Recent events timeline

### Refreshing Statistics

Statistics are calculated on-demand. To refresh:

1. On the campaign statistics page, click **"Refresh Statistics"**
2. Or add `?refresh=true` to the URL
3. Statistics are recalculated from all EmailEvent records

### Admin Interface

Access detailed tracking data via Django admin:

1. **EmailEvent**: View all tracking events with filters by type and date
2. **CampaignStatistics**: View and manually refresh campaign statistics
3. Action available: "Refresh selected campaign statistics"

## API Endpoints

### 1. Tracking Pixel

**Endpoint**: `GET /track/pixel/<uuid:tracking_id>/`

**Purpose**: Records email open events

**Response**: 1x1 transparent GIF image

**Automatically embedded in all sent emails**

### 2. Click Tracking

**Endpoint**: `GET /track/click/<uuid:tracking_id>/?url=<original_url>`

**Purpose**: Records link click events and redirects

**Parameters**:
- `tracking_id`: UUID of the email
- `url`: Original destination URL (query parameter)

**Response**: HTTP 302 redirect to original URL

**Automatically applied to all links in emails**

### 3. Bounce Webhook

**Endpoint**: `POST /track/bounce/`

**Purpose**: Receives bounce notifications from email service providers

**Request Body**:
```json
{
  "tracking_id": "uuid-here",
  "event": "bounced",
  "bounce_type": "hard|soft",
  "reason": "mailbox does not exist",
  "email": "recipient@example.com"
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Event recorded"
}
```

**CSRF Exempt**: Yes (for external webhooks)

### 4. Delivery Webhook

**Endpoint**: `POST /track/delivery/`

**Purpose**: Receives delivery confirmation from email service providers

**Request Body**:
```json
{
  "tracking_id": "uuid-here",
  "event": "delivered",
  "email": "recipient@example.com",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Delivery recorded"
}
```

**CSRF Exempt**: Yes (for external webhooks)

## Statistics

### Campaign Statistics View

Access via: `/campaigns/<campaign_id>/statistics/`

**Displays**:

1. **Key Metrics Cards**:
   - Total Recipients
   - Sent Count
   - Delivered Count (with delivery rate)
   - Bounced Count (with bounce rate)
   - Unique Opens (with open rate)
   - Total Opens
   - Unique Clicks (with click rate)
   - Total Clicks

2. **Top Clicked Links Table**:
   - URL
   - Total clicks

3. **Opens Over Time Table**:
   - Date
   - Number of opens

4. **Recent Events Timeline**:
   - Event type with color coding

### Calculating Statistics

Statistics are calculated using the `CampaignStatistics.update_statistics()` method:

```python
stats = CampaignStatistics.objects.get(campaign=campaign)
stats.update_statistics()
```

**Calculations**:
- Delivery Rate = (delivered / sent) × 100
- Open Rate = (unique opens / delivered) × 100
- Click Rate = (unique clicks / delivered) × 100
- Bounce Rate = (bounced / sent) × 100

## Webhooks

### Configuring Email Service Provider Webhooks

If you're using an external SMTP relay service (e.g., SendGrid, Mailgun, AWS SES), configure their webhooks to point to your tracking endpoints.

#### SendGrid Configuration

1. Go to Settings → Mail Settings → Event Webhook
2. Set HTTP Post URL: `https://yourdomain.com/track/delivery/` (for delivered events)
3. Set HTTP Post URL: `https://yourdomain.com/track/bounce/` (for bounce events)
4. Select events: Delivered, Bounced, Spam Report
5. In webhook data, include the `tracking_id` in the custom arguments

#### Mailgun Configuration

1. Go to Sending → Webhooks
2. Add webhook URL: `https://yourdomain.com/track/delivery/`
3. Add webhook URL: `https://yourdomain.com/track/bounce/`
4. The tracking_id can be passed in custom variables

#### AWS SES Configuration

1. Configure SNS topics for bounce and delivery notifications
2. Create Lambda function to transform SNS to HTTP POST
3. POST to tracking endpoints with tracking_id

### Webhook Payload Format

Your webhook payload should include either:

1. `tracking_id`: The UUID from the email
2. `email`: The recipient email address (will find most recent sent email)

**Example**:
```json
{
  "tracking_id": "550e8400-e29b-41d4-a716-446655440000",
  "event": "bounced",
  "bounce_type": "hard",
  "reason": "Mailbox does not exist",
  "email": "recipient@example.com"
}
```

## Privacy Considerations

### GDPR Compliance

The tracking system collects:
- Email open events (IP address, user agent)
- Click events (IP address, user agent, clicked URL)

**Recommendations**:
1. Update your privacy policy to disclose email tracking
2. Provide opt-out mechanism in emails
3. Honor unsubscribe requests by stopping email sends
4. Consider anonymizing IP addresses after collection

### Disabling Tracking

To disable tracking for specific campaigns or users, you can:

1. Modify `campaign/tracking.py` to check for a flag
2. Add a `tracking_enabled` boolean to UserProfile
3. Skip pixel/link insertion when disabled

**Example**:
```python
# In send_emails.py
if user_profile.tracking_enabled:
    html_message = add_tracking_pixel(html_message, email_candidate.tracking_id)
    html_message = replace_links_with_tracking(html_message, email_candidate.tracking_id)
```

## Troubleshooting

### Tracking Pixel Not Recording Opens

**Possible causes**:
1. Email client blocks images by default
2. SITE_URL is incorrect
3. Tracking endpoint is not accessible

**Solutions**:
- Check that SITE_URL matches your domain
- Test the pixel URL directly in browser
- Check server logs for errors

### Click Tracking Not Working

**Possible causes**:
1. Links are not being replaced
2. Tracking endpoint returns error
3. Original URL is malformed

**Solutions**:
- Check HTML email source for tracking URLs
- Test tracking endpoint manually
- Verify link format in email template

### Statistics Not Updating

**Possible causes**:
1. Statistics not refreshed
2. No events recorded
3. Database query issue

**Solutions**:
- Click "Refresh Statistics" button
- Check EmailEvent table for events
- Run `update_statistics()` in Django shell

## Performance Optimization

### Database Indexes

The following indexes are automatically created:

```python
# EmailEvent indexes
- email_candidate + event_type
- event_type + timestamp
- tracking_id (on EmailSendCandidate)
```

### Caching Statistics

For large campaigns, consider caching statistics:

```python
from django.core.cache import cache

stats_key = f'campaign_stats_{campaign.id}'
stats = cache.get(stats_key)

if not stats:
    stats = CampaignStatistics.objects.get(campaign=campaign)
    stats.update_statistics()
    cache.set(stats_key, stats, 3600)  # Cache for 1 hour
```

### Batch Processing

For very high volume, process events asynchronously:

1. Use Celery for background tasks
2. Queue events and process in batches
3. Update statistics periodically (e.g., every hour)

## Future Enhancements

Potential improvements to the tracking system:

1. **Geographic Tracking**: Map IP addresses to locations
2. **Device Detection**: Parse user agent for device type
3. **Heatmaps**: Visual click heatmaps for emails
4. **A/B Testing**: Compare different email versions
5. **Engagement Scoring**: Score recipients by engagement level
6. **Automated Follow-ups**: Trigger emails based on events
7. **Real-time Dashboard**: WebSocket updates for live stats
8. **Export Reports**: PDF/Excel export of statistics

## Support

For issues or questions about the email tracking system:

1. Check the Django admin for raw event data
2. Review server logs for errors
3. Test tracking endpoints manually
4. Verify database migrations are applied

## Credits

Developed as part of the djangoMailer email marketing platform.

---

**Last Updated**: October 2024
