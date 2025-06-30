# MyBookshelf Email Workflow Setup with Resend

## Overview

This guide covers the complete setup of the MyBookshelf email workflow using Resend for the Sunday admin approval system and ongoing email communications.

## 🚀 Email Workflow Architecture

### **Components**

1. **Sunday Approval Emails** - Weekly admin approval workflow trigger
2. **Approval Notifications** - Real-time approval status updates
3. **Encouragement Emails** - Sunday subscriber engagement (future)
4. **Subscription Management** - User preference handling (future)

### **Email Types**

- **Admin Approval Request** - Sunday morning trigger to start approval workflow
- **Approval Session Reminders** - If admin hasn't completed approval by Tuesday
- **Weekly Content Summary** - What was published this week
- **System Alerts** - Technical issues requiring attention

## 📋 Resend Setup

### **1. Account Setup**

```bash
# Sign up at https://resend.com
# Verify your domain for sending
# Get your API key from dashboard
```

### **2. Domain Configuration**

```bash
# Add these DNS records to your domain (mybookshelf.shop)
# Replace YOUR_DOMAIN with mybookshelf.shop

# DKIM Record
TXT record: resend._domainkey.YOUR_DOMAIN
Value: [Provided by Resend]

# Return-Path Record
CNAME record: rp.YOUR_DOMAIN
Value: rp.resend.com

# Tracking Domain (optional)
CNAME record: track.YOUR_DOMAIN
Value: track.resend.com
```

### **3. Environment Variables**

Add to your environment configuration:

```bash
# Resend Configuration
RESEND_API_KEY=your_resend_api_key_here
RESEND_FROM_EMAIL=admin@mybookshelf.shop
RESEND_FROM_NAME=MyBookshelf Admin

# Admin Configuration
ADMIN_EMAIL=mcddsl@icloud.com
ADMIN_NAME=Michael McDermott

# Frontend URLs
ADMIN_DASHBOARD_URL=https://admin.mybookshelf.shop
PUBLIC_SITE_URL=https://mybookshelf.shop
```

## 📧 Email Templates

### **Sunday Approval Email Template**

```html
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Weekly Book Approval Required - MyBookshelf</title>
    <style>
      body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
          sans-serif;
        line-height: 1.6;
        color: #333;
      }
      .container {
        max-width: 600px;
        margin: 0 auto;
        padding: 20px;
      }
      .header {
        background: #2563eb;
        color: white;
        padding: 20px;
        border-radius: 8px 8px 0 0;
      }
      .content {
        background: #f8fafc;
        padding: 30px;
        border-radius: 0 0 8px 8px;
      }
      .button {
        display: inline-block;
        background: #16a34a;
        color: white;
        padding: 12px 24px;
        text-decoration: none;
        border-radius: 6px;
        font-weight: 600;
      }
      .stats {
        background: white;
        padding: 20px;
        border-radius: 6px;
        margin: 20px 0;
      }
      .book-item {
        background: white;
        padding: 15px;
        margin: 10px 0;
        border-radius: 6px;
        border-left: 4px solid #2563eb;
      }
    </style>
  </head>
  <body>
    <div class="container">
      <div class="header">
        <h1>📚 Weekly Book Approval Required</h1>
        <p>Sunday, {{current_date}} - MyBookshelf Admin</p>
      </div>

      <div class="content">
        <p>Good morning! Your weekly book approval session is ready.</p>

        <div class="stats">
          <h3>📊 This Week's Summary</h3>
          <ul>
            <li>
              <strong>{{pending_count}} books</strong> awaiting your approval
            </li>
            <li>
              <strong>{{filtered_count}} books</strong> passed content filtering
            </li>
            <li>
              <strong>{{needs_review_count}} books</strong> need special review
            </li>
          </ul>
        </div>

        <h3>📖 Books & Accessories Pending Your Approval:</h3>
        <p>
          <em
            >Review each item for Christian leadership relevance and business
            alignment. Email content and LinkedIn posts will be automatically
            generated from your approved selections.</em
          >
        </p>
        {{#pending_books}}
        <div class="book-item">
          <strong>{{title}}</strong> by {{author}}<br />
          <small
            >Category: {{category}} | Price: ${{price}} | Content Score:
            {{content_filter_score}}/10</small
          >
          {{#christian_themes}}
          <br />📖 Themes: {{christian_themes}} {{/christian_themes}}
          {{#content_filter_notes}} <br /><em
            >⚠️ Review needed: {{content_filter_notes}}</em
          >
          {{/content_filter_notes}}
        </div>
        {{/pending_books}}

        <div style="text-align: center; margin: 30px 0;">
          <a
            href="{{approval_dashboard_url}}?token={{session_token}}"
            class="button"
          >
            🚀 Start Approval Session
          </a>
        </div>

        <div
          style="background: #fef3c7; padding: 15px; border-radius: 6px; margin: 20px 0;"
        >
          <strong>⏰ Important:</strong> Please complete your approval by
          Tuesday to ensure timely content scheduling. This session expires in 7
          days.
        </div>

        <hr
          style="margin: 30px 0; border: none; border-top: 1px solid #e5e7eb;"
        />

        <h3>🎯 Business Context</h3>
        <p>
          <strong>Goal:</strong> Curate 3 books + 1 accessory for this week's
          automated posting
        </p>
        <p>
          <strong>Your Role:</strong> Approve content selections - posts and
          emails are auto-generated
        </p>
        <p>
          <strong>Posting Schedule:</strong> Tuesday, Wednesday, Thursday
          (automatic)
        </p>
        <p><strong>Revenue Target:</strong> $1-$5 commission this month</p>

        <p style="color: #6b7280; font-size: 14px; margin-top: 30px;">
          This email was automatically generated by the MyBookshelf admin
          system.<br />
          Questions? Reply to this email or check the
          <a href="{{public_site_url}}">main site</a>.
        </p>
      </div>
    </div>
  </body>
</html>
```

### **Approval Session Reminder Template**

```html
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>Reminder: Book Approval Needed - MyBookshelf</title>
    <style>
      body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
          sans-serif;
        line-height: 1.6;
        color: #333;
      }
      .container {
        max-width: 600px;
        margin: 0 auto;
        padding: 20px;
      }
      .header {
        background: #f59e0b;
        color: white;
        padding: 20px;
        border-radius: 8px 8px 0 0;
      }
      .content {
        background: #fffbeb;
        padding: 30px;
        border-radius: 0 0 8px 8px;
      }
      .button {
        display: inline-block;
        background: #dc2626;
        color: white;
        padding: 12px 24px;
        text-decoration: none;
        border-radius: 6px;
        font-weight: 600;
      }
    </style>
  </head>
  <body>
    <div class="container">
      <div class="header">
        <h1>⚠️ Approval Session Reminder</h1>
        <p>Tuesday - Action Required</p>
      </div>

      <div class="content">
        <p>Hi Michael,</p>

        <p>
          You have <strong>{{pending_count}} books</strong> still awaiting
          approval from Sunday's session.
        </p>

        <div
          style="background: #fecaca; padding: 15px; border-radius: 6px; margin: 20px 0;"
        >
          <strong>⏰ Time Sensitive:</strong> Content needs to be approved today
          for this week's posting schedule (Tue/Wed/Thu).
        </div>

        <div style="text-align: center; margin: 30px 0;">
          <a
            href="{{approval_dashboard_url}}?token={{session_token}}"
            class="button"
          >
            Complete Approval Now
          </a>
        </div>

        <p>
          <strong>Business Impact:</strong> Delayed approval means no affiliate
          revenue this week.
        </p>

        <p style="color: #6b7280; font-size: 14px;">
          Session expires: {{expires_at}}<br />
          Auto-generated reminder from MyBookshelf system.
        </p>
      </div>
    </div>
  </body>
</html>
```

## 🔧 Integration Points

### **Backend API Integration**

```python
# Add to backend/requirements.txt
resend==0.7.0

# Environment configuration
RESEND_API_KEY=your_api_key
RESEND_FROM_EMAIL=admin@mybookshelf.shop
```

### **Email Service Functions**

```python
# backend/services/email_service.py
import resend
import os
from datetime import datetime
from typing import List, Dict

class EmailService:
    def __init__(self):
        resend.api_key = os.getenv('RESEND_API_KEY')
        self.from_email = os.getenv('RESEND_FROM_EMAIL', 'admin@mybookshelf.shop')
        self.admin_email = os.getenv('ADMIN_EMAIL', 'mcddsl@icloud.com')

    def send_sunday_approval_email(self, pending_books: List[Dict], session_token: str):
        """Send weekly approval email to admin"""

    def send_approval_reminder(self, session_token: str, pending_count: int):
        """Send reminder if approval not completed by Tuesday"""

    def send_approval_completion_summary(self, session_stats: Dict):
        """Send summary after approval session completed"""
```

### **Scheduled Email Workflow**

```yaml
# .github/workflows/weekly-email-workflow.yml
name: Weekly Email Workflow

on:
  schedule:
    # Every Sunday at 8 AM EST
    - cron: "0 13 * * 0"
  workflow_dispatch:

jobs:
  send-approval-email:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Sunday approval email
        run: |
          curl -X POST "${{ secrets.BACKEND_API_URL }}/admin/trigger-weekly-approval" \
            -H "Authorization: Bearer ${{ secrets.API_SECRET_KEY }}"
```

## 📊 Email Analytics & Tracking

### **Key Metrics to Track**

- Email delivery rates
- Open rates for approval emails
- Click-through rates to dashboard
- Time from email sent to approval completion
- Weekly approval completion rates

### **Resend Dashboard Monitoring**

- Bounce rates (should be <2%)
- Spam complaints (should be <0.1%)
- Domain reputation score
- Delivery speed metrics

## 🚨 Error Handling & Fallbacks

### **Email Delivery Failures**

```python
# Backup notification methods
def notify_admin_fallback(message: str):
    # 1. Try Resend
    # 2. Fall back to system notifications
    # 3. Create GitHub issue as last resort
    # 4. Log to monitoring system
```

### **Domain Issues**

- Monitor DNS record health
- Backup sending domain configuration
- Alert on domain reputation issues
- Automatic retry with delays

## 🔒 Security & Compliance

### **Data Protection**

- No sensitive data in email content
- Secure session tokens with expiration
- GDPR-compliant unsubscribe handling
- Audit trail of all email communications

### **Best Practices**

- SPF, DKIM, DMARC records configured
- Rate limiting on email sends
- Bounce handling and list hygiene
- Regular security audits

## 📈 Future Email Features

### **Phase 2: Subscriber Emails**

- Sunday encouragement emails
- Weekly book recommendations
- Personalized content based on preferences
- A/B testing for subject lines and content

### **Phase 3: Advanced Automation**

- Dynamic content based on user behavior
- Automated follow-up sequences
- Integration with LinkedIn posting schedule
- Advanced segmentation and targeting

## 🛠️ Development & Testing

### **Local Testing**

```bash
# Use Resend test mode for development
RESEND_API_KEY=test_your_test_api_key
RESEND_TEST_MODE=true

# Send test emails to yourself
ADMIN_EMAIL=your-test-email@example.com
```

### **Production Deployment**

```bash
# Environment variables for production
RESEND_API_KEY=your_production_api_key
RESEND_FROM_EMAIL=admin@mybookshelf.shop
ADMIN_EMAIL=mcddsl@icloud.com

# Domain verification required before production use
```

## 📚 Resources

### **Resend Documentation**

- [Getting Started Guide](https://resend.com/docs/getting-started)
- [Domain Setup](https://resend.com/docs/domain-verification)
- [Email Templates](https://resend.com/docs/email-templates)
- [API Reference](https://resend.com/docs/api-reference)

### **MyBookshelf Integration**

- Admin Dashboard: `https://admin.mybookshelf.shop`
- API Endpoints: `/admin/email/*` routes
- Testing Environment: `https://staging.mybookshelf.shop`

---

_Updated: 2025-06-30 - Resend email workflow integration_
