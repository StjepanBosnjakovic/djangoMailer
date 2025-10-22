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

### Current Configuration (Development)
- `DEBUG = True` - Should be `False` in production
- `ALLOWED_HOSTS = ['*']` - Should be restricted to your domain
- `SECRET_KEY` in code - Should be in environment variable

### Best Practices
1. **Password Security**: SMTP passwords are stored encrypted in database
2. **CSRF Protection**: Enabled with trusted origins configuration
3. **Authentication**: All views require login via `@login_required`
4. **Multi-tenancy**: Users can only access their own data
5. **Rate Limiting**: Configurable per-user email sending limits

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

### Future Enhancements

Potential improvements and features:
- [ ] Comprehensive unit tests
- [ ] Email template editor UI
- [ ] Email preview before sending
- [ ] Pagination for recipient lists
- [ ] Email attachment support
- [ ] Webhook support for bounce/complaint handling
- [ ] Retry logic for failed emails
- [ ] Email scheduling UI calendar
- [ ] Dark mode support
- [ ] Multi-language support
- [ ] Export email logs to CSV
- [ ] Advanced analytics and reporting
- [ ] A/B testing for campaigns

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
