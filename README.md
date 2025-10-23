# djangoMailer

A multi-user email campaign management and bulk email sending platform built with Django. djangoMailer allows organizations to manage email campaigns, send personalized bulk emails with rate limiting, and track delivery with comprehensive logging.

## Features

### Core Functionality
- **Multi-User Support**: Each user has their own SMTP configuration and isolated recipient lists
- **Recipient Management**: Upload and manage bulk recipient lists via CSV import
- **Email Templates**: Create reusable email templates with personalization placeholders
- **Campaign Management**: Schedule and manage email campaigns with multiple recipients
- **Batch Email Sending**: Automated email processing with configurable rate limiting
- **Delivery Tracking**: Complete audit trail with email logs for sent and failed messages
- **Modern UI**: Responsive interface built with Tailwind CSS and Flowbite components

### Advanced Features
- **Template Personalization**: Support for dynamic fields including first name, last name, company, and custom fields
- **Rate Limiting**: Configurable maximum emails per hour per user
- **CSV Bulk Import**: Import recipients with support for custom fields
- **Recipient Filtering**: Advanced filtering by multiple criteria
- **Scheduled Sending**: Queue emails for future delivery
- **Dashboard Analytics**: Real-time statistics on recipients, campaigns, and email status
- **SMTP Configuration**: User-specific SMTP settings for flexible email provider integration

## Technologies Used

### Backend
- **Django 5.1.2** - Python web framework
- **Python 3.11** - Language runtime
- **PostgreSQL** - Primary database
- **Gunicorn** - WSGI HTTP server
- **django-crontab** - Scheduled task execution (5-minute intervals)

### Frontend
- **Tailwind CSS** - Utility-first CSS framework (CDN)
- **Flowbite** - UI component library (CDN)
- **Django Crispy Forms** - Enhanced form rendering
- **crispy-tailwind** - Tailwind template pack

### Deployment
- **Docker** - Containerization with Python 3.11-slim-bullseye base
- **psycopg2** - PostgreSQL database adapter

## Prerequisites

- Python 3.11 or higher
- PostgreSQL database
- Docker (optional, for containerized deployment)
- SMTP server credentials for sending emails

## Installation

### Option 1: Docker Deployment (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd djangoMailer
   ```

2. **Configure environment variables**

   Create a `.env` file based on `.sample_env`:
   ```bash
   cp djangoMailer/.sample_env .env
   ```

   Edit `.env` with your PostgreSQL credentials:
   ```env
   POSTGRES_DB=your_database_name
   POSTGRES_USER=your_database_user
   POSTGRES_PASSWORD=your_database_password
   POSTGRES_HOST=your_database_host_or_ip
   POSTGRES_PORT=5432
   ```

3. **Build and run with Docker**
   ```bash
   docker build -t djangomailer .
   docker run -p 8000:8000 --env-file .env djangomailer
   ```

4. **Access the application**

   Open your browser to `http://localhost:8000`

### Option 2: Manual Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd djangoMailer
   ```

2. **Create virtual environment**
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   Set the following environment variables or create a `.env` file:
   ```bash
   export POSTGRES_DB=your_database_name
   export POSTGRES_USER=your_database_user
   export POSTGRES_PASSWORD=your_database_password
   export POSTGRES_HOST=localhost
   export POSTGRES_PORT=5432
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Configure cron jobs**
   ```bash
   python manage.py crontab add
   ```

8. **Run development server**
   ```bash
   python manage.py runserver
   ```

## Configuration

### SMTP Settings

Each user can configure their own SMTP settings through the web interface:

1. Log in to your account
2. Navigate to **Edit Profile** in the sidebar
3. Configure the following settings:
   - **SMTP Host**: Your email server hostname (e.g., smtp.gmail.com)
   - **SMTP Port**: Server port (typically 587 for TLS or 465 for SSL)
   - **SMTP Username**: Your email account username
   - **SMTP Password**: Your email account password
   - **Use TLS**: Enable for secure connection (recommended)
   - **Use SSL**: Alternative to TLS
   - **From Email**: Email address to send from
   - **Max Emails Per Hour**: Rate limit for email sending

### Database Configuration

Edit `djangoMailer/settings.py` to modify database settings or use environment variables as shown above.

### Production Settings

For production deployment, update the following in `settings.py`:

```python
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
SECRET_KEY = os.environ.get('SECRET_KEY')  # Move to environment variable
```

## Usage

### 1. Upload Recipients

**Via CSV Import:**
1. Navigate to **Recipients > Upload Recipients**
2. Prepare a CSV file with the following columns:
   - `first_name`
   - `last_name`
   - `company`
   - `email` (required)
   - `country`
   - `city`
   - `free_field1`
   - `free_field2`
   - `free_field3`
3. Upload the CSV file
4. Recipients will be imported and associated with your account

**Example CSV:**
```csv
first_name,last_name,company,email,country,city,free_field1,free_field2,free_field3
John,Doe,Acme Corp,john@example.com,USA,New York,VIP,Premium,Q1-2025
Jane,Smith,Tech Inc,jane@example.com,UK,London,Standard,Basic,Q2-2025
```

### 2. Create Email Templates

1. Navigate to **Email Templates > Create Template**
2. Enter a template name
3. Write your email subject
4. Compose your email body with personalization placeholders:
   - `{first_name}` - Recipient's first name
   - `{last_name}` - Recipient's last name
   - `{company}` - Recipient's company
   - `{free_field1}` - Custom field 1
   - `{free_field2}` - Custom field 2
   - `{free_field3}` - Custom field 3

**Example Template:**
```
Subject: Special Offer for {company}

Dear {first_name} {last_name},

We have a special offer for {company} this month...

Best regards,
Your Team
```

### 3. Create Email Campaigns

1. Navigate to **Email Campaigns > Create Campaign**
2. Enter campaign name
3. Select an email template
4. Use the recipient selector to choose recipients:
   - Filter by name, company, email, country, city, or custom fields
   - Select individual recipients or all matching filters
5. Set scheduled time (optional - leave blank for immediate processing)
6. Click **Create Campaign**

### 4. Monitor Email Sending

- **Dashboard**: View statistics on total recipients, templates, campaigns, and email status
- **Emails Queue**: See all queued emails and their status
- **Email Logs**: View detailed delivery history including timestamps and error messages
- **Send Now**: Manually trigger immediate sending for specific queued emails

### 5. Email Processing Workflow

The system automatically processes emails every 5 minutes via cron job:

```
1. User creates campaign → EmailSendCandidate records created for each recipient
2. Cron job runs send_emails command every 5 minutes
3. System fetches unsent emails where scheduled_time has passed
4. Respects user's rate limit (max_emails_per_hour)
5. Personalizes email body with recipient data
6. Sends via user's SMTP configuration
7. Logs success or failure with error details
8. Updates email status and timestamp
```

## Project Structure

```
djangoMailer/
├── manage.py                          # Django management utility
├── requirements.txt                   # Python dependencies
├── Dockerfile                         # Docker containerization
├── LICENSE                            # GPL v3 license
├── djangoMailer/                      # Project configuration
│   ├── settings.py                    # Django settings
│   ├── urls.py                        # Main URL routing
│   ├── wsgi.py                        # WSGI entry point
│   ├── asgi.py                        # ASGI entry point
│   └── .sample_env                    # Environment template
└── campaign/                          # Main Django app
    ├── migrations/                    # Database migrations
    ├── management/
    │   └── commands/
    │       └── send_emails.py         # Scheduled email processor
    ├── templates/                     # HTML templates (13 files)
    │   ├── base.html                  # Base template with navigation
    │   ├── home.html                  # Dashboard
    │   ├── campaign_*.html            # Campaign management
    │   ├── email_*.html               # Email queue management
    │   ├── recipient_*.html           # Recipient management
    │   ├── template_*.html            # Template CRUD
    │   ├── log_list.html              # Email logs
    │   ├── edit_profile.html          # SMTP configuration
    │   └── registration/
    │       └── login.html             # Login page
    ├── templatetags/
    │   └── form_tags.py               # Custom template filters
    ├── models.py                      # Database models (6 models)
    ├── views.py                       # View handlers (14+ views)
    ├── urls.py                        # App URL routing
    ├── forms.py                       # Form classes (6 forms)
    ├── admin.py                       # Django admin configuration
    └── context_processors.py          # Global template context
```

## Database Models

### Core Models

**UserProfile**
- Extends Django User model (1:1 relationship)
- Stores SMTP configuration and rate limiting settings
- Auto-created when user registers

**Recipient**
- Email recipient information
- Fields: first_name, last_name, company, email, country, city, free_field1/2/3
- User-specific (multi-tenant isolation)
- Unique constraint on email per user

**EmailTemplate**
- Reusable email message templates
- Fields: name, subject, body
- Supports personalization placeholders

**EmailCampaign**
- Groups recipients and template for scheduled sending
- Many-to-Many relationship with Recipients
- Foreign Key to EmailTemplate
- Tracks campaign creation and scheduling

**EmailSendCandidate**
- Queue item representing a single email to be sent
- Links recipient, template, and campaign
- Tracks sent status and timestamp
- Central to email processing workflow

**EmailLog**
- Audit trail for all email sending attempts
- Records status (Sent/Failed), error messages, timestamps
- Used for monitoring and troubleshooting

### Relationships

```
User → UserProfile (1:1)
UserProfile → Recipient (1:Many)
UserProfile → EmailTemplate (1:Many)
UserProfile → EmailCampaign (1:Many)
EmailCampaign → Recipient (Many:Many)
EmailCampaign → EmailTemplate (Foreign Key)
EmailCampaign → EmailSendCandidate (1:Many)
Recipient → EmailSendCandidate (1:Many)
EmailTemplate → EmailSendCandidate (1:Many)
EmailSendCandidate → EmailLog (1:Many)
```

## API Reference

### Management Commands

**send_emails**
```bash
python manage.py send_emails
```
Processes queued emails respecting rate limits and schedules. Automatically runs every 5 minutes via cron.

**crontab**
```bash
python manage.py crontab add      # Add cron jobs
python manage.py crontab show     # Show active jobs
python manage.py crontab remove   # Remove cron jobs
```

### URL Endpoints

| URL | View | Description |
|-----|------|-------------|
| `/` | home | Dashboard with statistics |
| `/recipients/` | recipient_list | List all recipients |
| `/recipients/upload/` | recipient_upload | CSV upload interface |
| `/templates/` | template_list | List email templates |
| `/templates/create/` | template_create | Create new template |
| `/emails/` | email_list | View email queue |
| `/emails/create/` | email_create | Queue single email |
| `/campaigns/` | campaign_list | List campaigns |
| `/campaigns/create/` | campaign_create | Create campaign |
| `/logs/` | log_list | View email logs |
| `/profile/edit/` | edit_profile | Configure SMTP settings |
| `/email_send_candidate/<pk>/send_now/` | send_email_now | Send email immediately |
| `/accounts/login/` | login | User authentication |
| `/accounts/logout/` | logout | User logout |

## Deployment

### Docker Production Deployment

The included Dockerfile uses the following configuration:
- Base image: `python:3.11-slim-bullseye`
- Exposes port: `8000`
- Web server: Gunicorn with 4 workers
- Auto-runs migrations on startup
- Auto-creates superuser (if credentials provided)

**Production checklist:**
1. Set `DEBUG = False` in settings.py
2. Configure proper `ALLOWED_HOSTS`
3. Move `SECRET_KEY` to environment variable
4. Set up PostgreSQL with proper credentials
5. Configure proper CSRF trusted origins
6. Enable HTTPS and set secure cookie flags
7. Set up regular database backups
8. Configure cron jobs for email processing
9. Monitor email logs regularly

### Environment Variables

Required environment variables:
- `POSTGRES_DB` - Database name
- `POSTGRES_USER` - Database user
- `POSTGRES_PASSWORD` - Database password
- `POSTGRES_HOST` - Database host
- `POSTGRES_PORT` - Database port (default: 5432)

Optional environment variables:
- `SECRET_KEY` - Django secret key (recommended for production)
- `DEBUG` - Debug mode (default: True)

## Security Considerations

### Production Security Features ✅

This application now includes comprehensive security features:

#### 1. Encrypted SMTP Passwords
- **Implementation**: Uses `django-encrypted-model-fields` with `EncryptedCharField`
- **Location**: `campaign/models.py:13`
- **Encryption Key**: Stored in `FIELD_ENCRYPTION_KEY` environment variable
- **Benefit**: SMTP passwords are encrypted at rest in the database

#### 2. Environment-Based Configuration
- **SECRET_KEY**: Loaded from environment variable with secure fallback
- **DEBUG**: Defaults to `False` for production safety
- **ALLOWED_HOSTS**: Configurable via environment variable (comma-separated)
- **Configuration File**: Use `.env.example` as template

#### 3. Rate Limiting Protection
- **Login**: Limited to 5 attempts per minute per IP address
- **Registration**: Limited to 3 attempts per hour per IP address
- **Implementation**: Custom views in `campaign/auth_views.py`
- **Library**: `django-ratelimit` with in-memory caching

#### 4. Input Sanitization
- **Email Subjects**: Strip newlines to prevent header injection
- **Email Bodies**: HTML sanitization using `bleach` library
- **Allowed Tags**: Safe HTML tags only (p, br, strong, em, u, a, lists, headings)
- **Location**: `campaign/forms.py` clean methods

#### 5. CSRF Protection
- **Status**: Enabled by default in Django middleware
- **Validation**: All POST forms include `{% csrf_token %}`
- **Cookies**: Secure flag enabled in production

#### 6. Production Security Headers
When `DEBUG=False`, the following are automatically enabled:
- `SECURE_SSL_REDIRECT = True` - Force HTTPS
- `SESSION_COOKIE_SECURE = True` - Secure session cookies
- `CSRF_COOKIE_SECURE = True` - Secure CSRF cookies
- `SECURE_BROWSER_XSS_FILTER = True` - XSS protection
- `SECURE_CONTENT_TYPE_NOSNIFF = True` - Prevent MIME sniffing
- `X_FRAME_OPTIONS = DENY` - Clickjacking protection
- `SECURE_HSTS_SECONDS = 31536000` - HTTP Strict Transport Security (1 year)
- `SECURE_HSTS_INCLUDE_SUBDOMAINS = True` - HSTS for subdomains
- `SECURE_HSTS_PRELOAD = True` - HSTS preload ready

### Environment Variables

Required for production deployment:

```bash
# Security
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Encryption key for SMTP passwords (must be a Fernet key)
# Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
FIELD_ENCRYPTION_KEY=your-fernet-key-here

# Database
POSTGRES_DB=your_database_name
POSTGRES_USER=your_database_user
POSTGRES_PASSWORD=your_database_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

**Generating the FIELD_ENCRYPTION_KEY:**

The `FIELD_ENCRYPTION_KEY` must be a valid Fernet key (32 url-safe base64-encoded bytes). Generate one with:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

This will output something like: `RKJw8xGzJoaVKMhJzGQrNqP0YXx0K8vZ9tC7BnMxQWE=`

Copy `.env.example` to `.env` and update with your values.

### Best Practices
1. **Password Security**: SMTP passwords are stored encrypted in database ✅
2. **CSRF Protection**: Enabled with trusted origins configuration ✅
3. **Authentication**: All views require login via `@login_required` ✅
4. **Multi-tenancy**: Complete data isolation between users ✅
5. **Rate Limiting**: Login and registration protected from brute force ✅
6. **Input Sanitization**: Email content sanitized to prevent injection ✅
7. **Environment Variables**: All secrets moved to environment variables ✅

## Multi-Tenancy Data Isolation

This application implements **complete multi-tenancy data isolation** to ensure users can only access their own data.

### Implemented Protections

**All List Views Filter by User Profile:**
- `recipient_list` - Shows only user's recipients
- `template_list` - Shows only user's email templates
- `email_list` - Shows only user's queued emails
- `campaign_list` - Shows only user's campaigns
- `log_list` - Shows only user's email logs
- `queue_list` - Shows only user's queued emails
- `home` dashboard - Shows counts only for user's data

**All Create Views Assign User Profile:**
- `template_create` - Automatically assigns user_profile to new templates
- `email_create` - Assigns user_profile and filters form choices to user's data
- `queue_create` - Assigns user_profile and filters form choices to user's data
- `campaign_create` - Assigns user_profile and filters templates/recipients by user
- `recipient_upload` - Assigns user_profile when importing via CSV

**Form Security:**
- All dropdown fields (recipients, templates) are filtered to show only user-owned resources
- Users cannot select or reference other users' data through form manipulation

**Access Control:**
- Direct URL access to other users' resources returns 404 (e.g., `/email_send_candidate/<other_user_id>/send_now/`)
- All queries filter by `user_profile=request.user.profile`
- Helper functions like `filter_recipients()` enforce user isolation

### Testing

The multi-tenancy implementation includes comprehensive test coverage in `campaign/tests/test_multitenancy.py`:
- 16 dedicated tests verifying data isolation
- Tests for cross-user access denial
- Tests for form queryset filtering
- Tests for correct user_profile assignment
- All multi-tenancy tests passing ✓

### Security Guarantees

With this implementation:
1. ✅ Users cannot view other users' recipients, templates, campaigns, or logs
2. ✅ Users cannot create data assigned to other users
3. ✅ Users cannot access other users' data via direct URLs
4. ✅ Form dropdowns only show user-owned options
5. ✅ Dashboard statistics reflect only user-specific data
6. ✅ CSV imports automatically assign to the uploading user

### Production Recommendations
1. Enable HTTPS only
2. Use environment variables for all secrets
3. Restrict `ALLOWED_HOSTS` to your domain
4. Set `DEBUG = False`
5. Configure proper database backups
6. Implement monitoring and alerting
7. Use strong passwords for admin accounts
8. Regular security updates

## Troubleshooting

### Common Issues

**Emails not sending:**
1. Check SMTP settings in user profile
2. Verify cron job is running: `python manage.py crontab show`
3. Check email logs for error messages
4. Verify rate limit hasn't been exceeded
5. Test SMTP connection manually

**CSV upload fails:**
1. Ensure CSV has required columns (especially `email`)
2. Check for proper UTF-8 encoding
3. Verify no duplicate emails for your account
4. Check file size limits

**Database connection errors:**
1. Verify PostgreSQL is running
2. Check environment variables are set correctly
3. Ensure database user has proper permissions
4. Test connection: `psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB`

**Cron job not running:**
1. Add cron jobs: `python manage.py crontab add`
2. Check cron service is running
3. Review cron logs for errors
4. Manually test: `python manage.py send_emails`

## Contributing

Contributions are welcome! This project uses:
- **Django 5.1.2** coding standards
- **PEP 8** Python style guide
- **Git Flow** branching model

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Run tests: `python manage.py test campaign`
5. Commit your changes: `git commit -m 'Add some feature'`
6. Push to the branch: `git push origin feature/your-feature`
7. Submit a pull request

## TODO: Project Roadmap

### 🔴 CRITICAL: Security & Bug Fixes (Priority 1)

These issues **must be fixed** before production deployment:

#### Multi-Tenancy Data Isolation Bug ✅ COMPLETED
- [x] **FIX: recipient_list view** - ✅ Now filters by `request.user.profile`
- [x] **FIX: template_list view** - ✅ Now filters by `request.user.profile`
- [x] **FIX: email_list view** - ✅ Now filters by user profile
- [x] **FIX: campaign_list view** - ✅ Now has user-specific filtering
- [x] **FIX: log_list view** - ✅ Now filters by user profile
- [x] **FIX: home view** - ✅ Dashboard counts now filter by user profile
- [x] **FIX: queue_list view** - ✅ Now filters by user profile
- [x] **FIX: template_create view** - ✅ Now assigns user_profile on creation
- [x] **FIX: email_create view** - ✅ Now assigns user_profile and filters form choices
- [x] **FIX: campaign_create view** - ✅ Now assigns user_profile and filters recipients/templates
- [x] **FIX: recipient_upload** - ✅ Now assigns user_profile during CSV import
- [x] **FIX: filter_recipients helper** - ✅ Now filters by user profile
- [x] **TEST: Verify multi-tenancy** - ✅ 16 comprehensive tests added and passing

**Status:** All multi-tenancy data isolation issues have been resolved. See the Multi-Tenancy Data Isolation section for full details.

#### Security Vulnerabilities ✅ COMPLETED
- [x] **ENCRYPT SMTP passwords** - ✅ Now using django-encrypted-model-fields with EncryptedCharField
- [x] **Move SECRET_KEY to environment variable** - ✅ SECRET_KEY now reads from environment with fallback
- [x] **Set DEBUG = False** - ✅ DEBUG now reads from environment variable, defaults to False
- [x] **Restrict ALLOWED_HOSTS** - ✅ ALLOWED_HOSTS now reads from environment variable
- [x] **Add rate limiting** - ✅ Login limited to 5/min, registration to 3/hour using django-ratelimit
- [x] **Add CSRF validation** - ✅ CSRF tokens verified on all forms (already implemented)
- [x] **Sanitize email inputs** - ✅ Email subjects and bodies sanitized using bleach library

**Status:** All security vulnerabilities have been addressed. See the Security Enhancements section for full details.

#### Data Integrity Issues
- [ ] **Fix form user assignment** - EmailTemplateForm, EmailForm, etc. need to assign `user_profile` on save
- [ ] **Add email validation** - Ensure valid email format before saving recipients
- [ ] **Prevent duplicate recipients** - Handle unique constraint violations gracefully
- [ ] **Add null checks in send_emails.py** - Handle missing recipient fields without crashing

### 🟡 High Priority: Missing Core Features (Priority 2)

#### CRUD Operations
- [ ] **Add Edit Recipient** - Currently can only upload, no edit functionality
- [ ] **Add Delete Recipient** - No way to remove individual recipients
- [ ] **Add Edit Template** - Template update view missing
- [ ] **Add Delete Template** - No template deletion interface
- [ ] **Add Edit Campaign** - Cannot modify campaigns after creation
- [ ] **Add Delete Campaign** - Campaign deletion view needed
- [ ] **Add Manual Recipient Creation** - Form to add recipients without CSV

#### Email Functionality
- [ ] **Email preview** - Preview personalized email before sending
- [ ] **Email attachment support** - Allow attaching files to campaigns
- [ ] **HTML email support** - Rich text editor for email bodies
- [ ] **Retry logic for failed emails** - Automatic retry with exponential backoff
- [ ] **Bounce/complaint handling** - Webhook support for email provider feedback
- [ ] **Email validation before sending** - Test SMTP connection before queuing
- [ ] **Unsubscribe links** - Add opt-out functionality with tracking

#### Testing Infrastructure (0% Coverage)
- [ ] **Unit tests for models** - Test all model methods and validation
- [ ] **Unit tests for views** - Test all view logic and permissions
- [ ] **Unit tests for forms** - Test form validation and cleaning
- [ ] **Integration tests for email sending** - Mock SMTP and test workflow
- [ ] **Test fixtures** - Create sample data for testing
- [ ] **Test multi-tenancy isolation** - Verify users can't access other users' data
- [ ] **CI/CD pipeline** - Set up GitHub Actions for automated testing
- [ ] **Coverage reporting** - Aim for >80% code coverage

### 🟢 Medium Priority: UX & Performance (Priority 3)

#### Pagination & Performance
- [ ] **Paginate recipient_list** - Currently shows all recipients on one page
- [ ] **Paginate template_list** - Add pagination for large template lists
- [ ] **Paginate email_list** - Queue view needs pagination
- [ ] **Paginate campaign_list** - Campaign list pagination
- [ ] **Paginate log_list** - Email logs pagination
- [ ] **Add database indexes** - Index email, scheduled_time, sent fields for performance
- [ ] **Optimize queries** - Use select_related() and prefetch_related() to avoid N+1 queries
- [ ] **Add caching** - Cache dashboard statistics and frequently accessed data

#### UI/UX Improvements
- [ ] **Rich text editor** - WYSIWYG editor for email templates (TinyMCE, CKEditor, or Quill)
- [ ] **Drag-and-drop CSV upload** - Improve file upload UX
- [ ] **Calendar UI for scheduling** - Visual date picker for campaign scheduling
- [ ] **Campaign progress tracking** - Real-time progress bar for sending campaigns
- [ ] **Dashboard charts** - Add graphs for email statistics (sent, failed, pending)
- [ ] **Search functionality** - Search recipients, templates, campaigns
- [ ] **Bulk actions** - Select multiple items for bulk delete/edit
- [ ] **Export to CSV** - Export recipient lists and email logs
- [ ] **Dark mode toggle** - Implement dark theme (CSS framework supports it)
- [ ] **Mobile responsive improvements** - Optimize for smaller screens

### 🔵 Low Priority: Advanced Features (Priority 4)

#### Analytics & Reporting
- [ ] **Advanced analytics dashboard** - Campaign performance metrics
- [ ] **Email open tracking** - Track email opens with pixel tracking
- [ ] **Link click tracking** - Track link clicks in emails
- [ ] **Campaign comparison** - Compare performance across campaigns
- [ ] **Export reports to PDF** - Generate campaign performance reports
- [ ] **A/B testing** - Test multiple email variants
- [ ] **Delivery rate monitoring** - Alert on low delivery rates

#### Integration & Extensibility
- [ ] **REST API** - Build API for external integrations
- [ ] **API authentication** - Token-based auth for API
- [ ] **Webhook endpoints** - Receive bounce/complaint notifications from email providers
- [ ] **OAuth SMTP** - Support Gmail/Outlook OAuth instead of passwords
- [ ] **Multiple email providers** - Support SendGrid, AWS SES, Mailgun APIs
- [ ] **Import from external sources** - Google Contacts, Mailchimp, etc.
- [ ] **Custom field definitions** - Allow users to define their own recipient fields

#### User Experience
- [ ] **Multi-language support (i18n)** - Internationalization for UI
- [ ] **Email template gallery** - Pre-built templates for common use cases
- [ ] **Template variables autocomplete** - Suggest available placeholders in editor
- [ ] **Email validation service** - Verify email deliverability before sending
- [ ] **Recipient segmentation** - Advanced filtering and tagging
- [ ] **Campaign scheduling calendar** - Month view for scheduled campaigns
- [ ] **Notification system** - In-app notifications for campaign completion
- [ ] **User roles & permissions** - Admin/sender/viewer roles

### 🔧 DevOps & Production Readiness

- [ ] **Environment-based settings** - Separate dev/staging/prod configurations
- [ ] **Database connection pooling** - Configure pgBouncer or similar
- [ ] **Redis caching** - Add Redis for session storage and caching
- [ ] **Celery for background tasks** - Replace cron with Celery for email sending
- [ ] **Docker Compose for development** - Include PostgreSQL in docker-compose.yml
- [ ] **Logging configuration** - Structured logging with log rotation
- [ ] **Monitoring setup** - Sentry for error tracking, Prometheus for metrics
- [ ] **Database backup automation** - Automated PostgreSQL backups
- [ ] **Health check endpoints** - /health and /ready endpoints for load balancers
- [ ] **Static file optimization** - Minification and CDN setup
- [ ] **SSL/TLS configuration** - Force HTTPS in production

### 📚 Documentation

- [ ] **API documentation** - Auto-generated API docs (if API is built)
- [ ] **Code comments** - Add docstrings to all functions/classes
- [ ] **Architecture diagram** - Visual diagram of system components
- [ ] **Deployment guide** - Step-by-step production deployment
- [ ] **User manual** - End-user documentation with screenshots
- [ ] **Developer setup guide** - Contributing documentation
- [ ] **Changelog** - Track version changes and releases

---

### Priority Summary

**✅ Completed:** 13 multi-tenancy data isolation fixes
**Must fix before production (P1):** 7 critical security vulnerabilities + 4 data integrity issues
**Should implement soon (P2):** 24 core features and testing
**Nice to have (P3):** 17 UX and performance improvements
**Future roadmap (P4):** 20 advanced features
**Infrastructure:** 11 DevOps improvements
**Documentation:** 7 documentation tasks

**Total Remaining:** 90 tasks across 6 categories
**Total Completed:** 13 critical multi-tenancy fixes ✅

## License

This project is licensed under the **GNU General Public License v3.0** (GPL-3.0).

See the [LICENSE](LICENSE) file for the full license text.

### Key Points
- You can freely use, modify, and distribute this software
- Any modifications must also be released under GPL-3.0
- Source code must be made available when distributing
- No warranty is provided

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Submit a pull request
- Contact the maintainers

## Acknowledgments

Built with:
- [Django](https://www.djangoproject.com/) - The web framework for perfectionists with deadlines
- [Tailwind CSS](https://tailwindcss.com/) - A utility-first CSS framework
- [Flowbite](https://flowbite.com/) - Tailwind CSS component library
- [PostgreSQL](https://www.postgresql.org/) - The world's most advanced open source database
- [Gunicorn](https://gunicorn.org/) - Python WSGI HTTP Server for UNIX

---

**djangoMailer** - Professional email campaign management made simple.
