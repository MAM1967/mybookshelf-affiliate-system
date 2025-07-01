# MyBookshelf Affiliate System - Final Status Update (as of July 1, 2025)

## System Overview

- Automates LinkedIn posting of Christian leadership and business books with Amazon affiliate links.
- Uses Supabase for backend data and token storage.
- Uses Resend for email notifications.
- LinkedIn posting automation is scheduled and can be triggered manually.

## Current State

- **LinkedIn OAuth flow**: Working, new tokens are stored in Supabase.
- **Supabase integration**: Working, tokens and posting status update correctly.
- **Email notifications**: Working (emails may go to spam; SPF/DKIM/DMARC setup recommended for production).
- **Posting automation**: Script runs, finds scheduled books, and marks them as posted in Supabase.
- **LinkedIn API**: Returns 201 and post ID, but posts are not visible on the LinkedIn feed (likely due to LinkedIn-side restrictions or sandboxing).
- **Manual LinkedIn post**: Made to help establish account trust.
- As of now, LinkedIn organization posting is blocked pending approval for the Community Management API (which grants w_organization_social). A new LinkedIn developer app was created and a request for Community Management API access was submitted. Awaiting LinkedIn approval before further progress.

## Recent Troubleshooting

- Fixed Supabase environment variable issues in Vercel (set as plain values, not secrets).
- Added missing `refresh_token` column to `linkedin_tokens` table.
- Confirmed new tokens are being stored and used.
- Verified that posting automation completes successfully and sends email reports.
- Confirmed that LinkedIn posts are still not visible, despite API success.
- Manual post made to LinkedIn to help with account trust.
- Test suite: Most tests pass, Admin LinkedIn Integration has warnings (no failures).

## Remaining Issue

- **LinkedIn API posts are not visible on the feed, despite 201 Created responses and valid post IDs.**
- App is not in review, has correct permissions, and uses a valid, recently re-authenticated token.
- Manual posts appear on the feed, but API posts do not.
- This is likely a LinkedIn-side restriction or sandboxing issue.

## Next Steps

- Contact LinkedIn Developer Support with app ID, post IDs, and a description of the issue.
- Monitor for any changes after support intervention.

---

**Ready for support escalation.**

- The MyBookShelf LinkedIn company page was created in 2015 by the project owner, who is the sole admin and has verified admin status.
