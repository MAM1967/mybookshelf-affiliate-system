# Scheduled LinkedIn Posting System

This system automatically posts approved books to LinkedIn on their scheduled dates.

## Overview

The scheduled posting system consists of:

1. **Auto-scheduling**: When books are approved in the admin dashboard, they are automatically assigned to available posting days (Tuesday/Wednesday/Thursday)
2. **Scheduled posting script**: A Python script that checks for books scheduled for today and posts them to LinkedIn
3. **Cron job**: A shell script that can be run automatically to execute the posting script

## Files

- `scheduled_linkedin_poster_simple.py` - Main Python script for scheduled posting
- `cron_linkedin_poster.sh` - Shell script for cron job automation
- `add_posting_columns.sql` - Database migration to add posting tracking columns

## Usage

### Manual Execution

Check what books are scheduled for today:

```bash
python3 scripts/scheduled_linkedin_poster_simple.py --check-scheduled
```

Run a dry run (generate content but don't post):

```bash
python3 scripts/scheduled_linkedin_poster_simple.py --dry-run
```

Test LinkedIn connection:

```bash
python3 scripts/scheduled_linkedin_poster_simple.py --test
```

Execute actual posting:

```bash
python3 scripts/scheduled_linkedin_poster_simple.py
```

### Automated Execution

Set up a cron job to run daily:

```bash
# Edit crontab
crontab -e

# Add this line to run at 9 AM daily
0 9 * * * /path/to/backend/scripts/cron_linkedin_poster.sh
```

## How It Works

1. **Scheduling**: When a book is approved in the admin dashboard, it's automatically assigned a `scheduled_post_at` time on the next available posting day
2. **Daily Check**: The script runs daily and checks for books with `scheduled_post_at <= now` and `status = 'approved'`
3. **Content Generation**: For each scheduled book, it generates LinkedIn-optimized content based on the day of the week
4. **Posting**: Posts are made to LinkedIn using the stored access token
5. **Tracking**: Books are marked as posted with timestamps and status updates

## Content Templates

The system uses different content templates for each posting day:

- **Tuesday**: Leadership insights and biblical principles
- **Wednesday**: Practical strategies and implementation focus
- **Thursday**: Comprehensive recommendations and complete toolkits

## Database Schema

The system uses these columns in the `pending_books` table:

- `scheduled_post_at`: When the book should be posted
- `posted_at`: When the book was actually posted (added by migration)
- `post_status`: Status of the posting attempt (added by migration)
- `post_content`: The actual content that was posted (added by migration)

## Setup Requirements

1. **LinkedIn Token**: A valid LinkedIn access token must be stored in `linkedin_token.json`
2. **Database Migration**: Run the migration script to add posting tracking columns
3. **Environment Variables**: Ensure all required environment variables are set in `config.py`

## Error Handling

The script handles various error conditions:

- Missing LinkedIn credentials
- Invalid or expired tokens
- Database connection issues
- LinkedIn API rate limiting
- Content generation failures

## Logging

All activities are logged to:

- Console output
- `scheduled_linkedin_poster.log` file
- Database tracking columns

## Monitoring

To monitor the system:

1. Check the log files for errors
2. Review the database for posting status
3. Monitor LinkedIn for actual posts
4. Use the `--check-scheduled` flag to see what's queued

## Troubleshooting

**No books scheduled**: This is normal if no books were approved for today
**LinkedIn token issues**: Regenerate the LinkedIn token and update `linkedin_token.json`
**Database errors**: Check the migration script and ensure all columns exist
**Posting failures**: Check LinkedIn API limits and token validity
