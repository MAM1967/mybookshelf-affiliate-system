# MyBookshelf Project Context & Status

## Current Project State (Last Updated: 2025-06-30)

### ✅ COMPLETED & WORKING

- **LinkedIn OAuth Integration**: Fully functional, stores tokens in Supabase
- **LinkedIn Posting Automation**: Ready for production use
- **Database Schema**: All tables created and working
- **Vercel Deployment**: API endpoints working, package.json deployed
- **Token Storage**: Uses Supabase `linkedin_tokens` table (not local files)

### 🚀 READY FOR SOFT LAUNCH (July 1st, 2025)

- **Scheduled Books**: 3 books approved and scheduled for July 1-3
  - July 1 (Tue): Atomic Habits by James Clear
  - July 2 (Wed): The Five Dysfunctions of a Team by Patrick Lencioni
  - July 3 (Thu): The Advantage by Patrick Lencioni
- **Posting Script**: `backend/scripts/scheduled_linkedin_poster_simple.py` tested and working
- **Content Generation**: Templates ready for Tue/Wed/Thu posting themes

## Key Files & Components

### Critical Working Files

- `api/linkedin-callback.js` - OAuth callback handler (fixed redirect loop)
- `backend/scripts/scheduled_linkedin_poster_simple.py` - Main posting script
- `vercel.json` - Deployment config (removed builds property for auto-detection)
- `package.json` - Node.js dependencies for Vercel API endpoints

### Database Tables

- `pending_books` - Books with approval/scheduling status
- `linkedin_tokens` - OAuth tokens with expiration tracking
- `admin_users` - Admin access (for future passwordless login)

### Environment Variables (Vercel Secrets)

- `SUPABASE_URL`, `SUPABASE_ANON_KEY` - Database access
- `LINKEDIN_CLIENT_ID`, `LINKEDIN_CLIENT_SECRET` - OAuth credentials
- `RESEND_API_KEY`, `ADMIN_EMAIL` - Email functionality

## How to Execute Tomorrow's Launch

### Manual Launch Command

```bash
cd backend/scripts
python3 scheduled_linkedin_poster_simple.py
```

### Testing Commands

```bash
# Test LinkedIn connection
python3 scheduled_linkedin_poster_simple.py --test

# Check what's scheduled
python3 scheduled_linkedin_poster_simple.py --check-scheduled

# Dry run (preview content)
python3 scheduled_linkedin_poster_simple.py --dry-run
```

## Immediate Backlog (Priority Order)

### 1. **TOMORROW**: Fix Email Test Suite Issues 🚨

- GitHub test suite failing due to email configuration
- Investigate email service integration errors
- Files to check: `backend/scripts/email_service.py`, test reports

### 2. **Future High Priority**: Amazon Integration 📚

- Match 75 books + 25 accessories with Amazon ASINs
- Generate affiliate links with your affiliate code
- Significant effort - postponed after launch
- Data prepared in: `books_and_accessories_2025.json`

## Notes for Assistant

- Always check this file first when resuming work
- Run test commands to verify current state
- Check git log for recent changes: `git log --oneline -5`
- Update this file at end of each session with new status

---

_Last successful test: June 30, 2025 - LinkedIn connection successful_
_Next milestone: July 1, 2025 soft launch_
