# Product Requirements Document: MyBookshelf Automated Affiliate System

## 1. Overview

**Product Name**: MyBookshelf Affiliate System  
**Objective**: Automate Amazon affiliate revenue ($1-$5 in two weeks) by scraping 3 leadership/productivity/AI books (e.g., Patrick Lencioni) + 1 accessory weekly, storing data in Supabase, and posting 200-word updates with images to LinkedIn via a custom OAuth app, with manual post approval. Include a mini-app for browsing recommendations. Build 2-5 LinkedIn followers. Align with Christian values (e.g., Proverbs 16:3).  
**Target Audience**: LinkedIn professionals seeking career-focused books/accessories.  
**Success Metrics**:

- Revenue: $1-$5 (1-2 Amazon affiliate sales, 4% book/3% accessory commissions).
- Followers: 2-5 via organic LinkedIn growth.
- Uptime: 99% system reliability.
- Setup Time: <10 hours.

## 2. Requirements

### 2.1 Functional Requirements

- **Amazon Data Fetching & Scraping**:
  - **Weekly Scraping Process**: Conduct up to 10 non-duplicative scrapes from Amazon website each week to identify potential books and accessories.
  - **Content Curation**: Diversify beyond Patrick Lencioni (who serves as one example of Christian leadership authors) to include various leadership/productivity/AI authors who align with Christian principles.
  - **Content Filtering Criteria**: Exclude items that violate Christian principles:
    - No blasphemy or profanity
    - No denial of Jesus Christ
    - No explicit or implicit embrace of other world religions (Hinduism, Buddhism, Islam) as business principles
    - Focus on leadership, productivity, and business books that align with biblical values
  - **API Integration**: Use Amazon Product Advertising API (PA API) to fetch detailed product information and embed Amazon Associate ID in affiliate links.
  - **Fallback**: ScrapingBee ($1/1,000 requests) if PA API limits hit.
- **Supabase Backend**:
  - Store data in Postgres table: title, author, price, affiliate link, image URL, category, timestamp.
  - Provide API endpoint for mini-app and Pipedream.
  - Free tier (500MB, 10,000 requests/month).
- **Python Script**:
  - Run weekly (Sunday, 8 AM) via Pipedream.
  - Query PA API, store in Supabase using Python SDK.
  - Developed with Cursor/Zed (AI-assisted coding).
- **Admin Approval Workflow**:
  - **Weekly Approval Process**: Each week's scraped items (up to 10) are presented on an admin approval page for review.
  - **Approval Interface**: Admin can approve/reject each item individually before database ingestion.
  - **Email Notifications**: Sunday approvals sent to mcddsl@icloud.com for final review.
  - **Database Promotion**: Only approved items are promoted from scraping queue to live database.
- **LinkedIn Automation**:
  - Generate 200-word post (e.g., "This week's top leadership books + recommendations [affiliate links]") with Canva image (navy-orange, free tier).
  - **Sunday Publication**: Automated LinkedIn posts go out on Sundays after admin approval.
  - Use Pipedream to email post for approval (yes/no), then post to MyBookshelf via LinkedIn OAuth app.
- **Mini-App**:
  - Supabase-hosted webpage (Next.js or HTML) to browse recommendations (title, author, link).
  - Accessible via LinkedIn bio/post links.
- **Organic Growth**:
  - Manual daily posts (100-200 words), 5 Group comments/day, 20 invites/day to gain 2-5 followers.

### 2.2 Non-Functional Requirements

- **Cost**: $0-$5/month (Supabase free, Pipedream free, Canva free, ScrapingBee $1 if needed).
- **Performance**: Script runs in <5 minutes; API latency <2 seconds; admin dashboard loads <3 seconds.
- **Scalability**: Handle 1,000 items in Supabase; scale to 10 books/week; support up to 50 pending approval items.
- **Security**:
  - Secure PA API keys, Supabase keys, and LinkedIn OAuth tokens (environment variables)
  - Admin authentication limited to mcddsl@icloud.com
  - Session-based authentication with automatic timeout (2 hours)
  - Rate limiting on admin login attempts (5 attempts per minute)
  - HTTPS-only admin access via admin.mybookshelf.shop
  - SQL injection prevention and input sanitization
- **Usability**:
  - Intuitive admin dashboard for item review and approval
  - Mobile-responsive admin interface
  - Bulk operations for efficiency
  - Email notifications with one-click approval links

## 3. Technical Architecture

- **Frontend**: Mini-app + Admin Dashboard (Supabase API, Next.js/HTML, hosted on Vercel).
- **Backend**: Supabase Postgres (tables: `books_accessories`, `scraping_queue`, `admin_sessions`), Python SDK for CRUD.
- **Script**: Python (PA API/ScrapingBee), hosted on Pipedream.
- **Automation**: Pipedream workflow (data fetch → post generation → approval → LinkedIn).
- **APIs**: Amazon PA API, Canva API, LinkedIn API, Supabase API.
- **Admin System**: Secure admin dashboard for approval workflow with session management.

### 3.1 Admin Approval System Architecture

**Database Schema:**

```sql
-- Scraping queue for pending approval items
CREATE TABLE scraping_queue (
  id SERIAL PRIMARY KEY,
  title VARCHAR(500) NOT NULL,
  author VARCHAR(200),
  description TEXT,
  price DECIMAL(10,2),
  amazon_asin VARCHAR(20),
  image_url TEXT,
  affiliate_link TEXT,
  category VARCHAR(100),
  scraped_date TIMESTAMP DEFAULT NOW(),
  content_score INTEGER DEFAULT 0, -- Christian content alignment score
  filter_flags TEXT[], -- Array of any content warnings
  status VARCHAR(20) DEFAULT 'pending', -- pending, approved, rejected
  admin_notes TEXT,
  reviewed_date TIMESTAMP,
  reviewed_by VARCHAR(100) DEFAULT 'admin'
);

-- Admin session management
CREATE TABLE admin_sessions (
  id SERIAL PRIMARY KEY,
  session_token VARCHAR(255) UNIQUE NOT NULL,
  email VARCHAR(100) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  expires_at TIMESTAMP NOT NULL,
  last_activity TIMESTAMP DEFAULT NOW()
);

-- Approval audit log
CREATE TABLE approval_log (
  id SERIAL PRIMARY KEY,
  item_id INTEGER REFERENCES scraping_queue(id),
  action VARCHAR(20) NOT NULL, -- approved, rejected, promoted
  reason TEXT,
  admin_email VARCHAR(100),
  timestamp TIMESTAMP DEFAULT NOW()
);
```

**Admin Dashboard Components:**

1. **Authentication Module**: Simple email-based login for mcddsl@icloud.com
2. **Review Interface**: Card-based layout for item review
3. **Batch Operations**: Approve/reject multiple items
4. **Content Analysis**: Display content filtering scores and flags
5. **History View**: Track approval decisions and patterns

**API Endpoints:**

```
GET  /api/admin/login              - Admin authentication
POST /api/admin/logout             - Session termination
GET  /api/admin/pending            - Fetch pending approval items
POST /api/admin/approve/:id        - Approve single item
POST /api/admin/reject/:id         - Reject single item
POST /api/admin/batch-action       - Bulk approve/reject
GET  /api/admin/history           - Approval history
POST /api/admin/promote-approved   - Move approved items to live database
```

## 4. User Interaction & Marketing Flow: Virtuous Conversion Cycle

### 4.1 Complete User Journey: LinkedIn → Mini-Site → Amazon

**Based on analysis of top Amazon affiliate sites including The Wirecutter, OutdoorGearLab, and Pack Hacker**

#### Phase 1: LinkedIn Direct Conversion (Sunday Posts) - PRIMARY PATH

**User Story**: "As a Christian professional on LinkedIn, I want to discover leadership books that align with my values and buy them immediately without extra steps."

**Interaction Design:**

- **Hook**: Scripture + Insight opening (Proverbs 16:3 + leadership principle)
- **Book Listings**: Individual book entries with covers, titles, and prices
- **Direct CTAs**: "GET ON AMAZON" button for each book (direct affiliate links)
- **Secondary CTA**: "See ALL recommendations + leadership insights" (mini-site link)
- **Trust Signal**: "Vetted for biblical alignment" badge on each book

#### Phase 2: Mini-Site as Value Hub (Secondary Path) - STANDALONE PURPOSE

**User Story**: "As someone interested in ongoing Christian leadership development, I want a central place to see all book recommendations, get leadership insights, and join a community."

**Critical Design Elements:**

1. **Instant Trust Building** (Top 25% of page):

   - Professional Christian branding (navy/orange theme)
   - "Vetted for Christian principles" badge
   - Scripture reference integration
   - Clear author expertise statement

2. **Hero Book Showcase** (Next 50% of page):

   - Large book cover image (Pack Hacker "flat lay" style)
   - "Why we chose this book" - 2-3 bullet points
   - Price transparency: "Starting at $X.XX Kindle" with format badge
   - Primary CTA: "Get This Book on Amazon" (contrasting color)

3. **Secondary Books Grid** (Bottom 25%):

   - Smaller book covers with ratings
   - Quick value propositions
   - Individual "View on Amazon" buttons

4. **Friction Elimination**:
   - Mobile-first responsive design
   - <2 second page load time
   - No pop-ups or newsletter signups blocking content
   - All affiliate links open in new tabs (preserves session)

#### Phase 3: Amazon Handoff (Zero friction transition)

**User Story**: "As someone ready to buy, I want to get to the exact Amazon product page quickly and let Amazon handle the purchase process."

**Technical Implementation:**

- **Smart Linking**: Direct to lowest-price NEW format (never used/3rd party)
- **Affiliate Tracking**: Preserve `mybookshelf-20` tag through redirect
- **Format Flexibility**: Let Amazon upsell to other formats (Audible, hardcover)
- **Session Preservation**: Mini-site stays open in original tab

#### Phase 4: Post-Purchase Engagement (Long-term value)

**User Story**: "As someone who bought a recommended book, I want to stay connected for future recommendations and feel part of a community."

**Conversion Optimization:**

- **Email Capture**: Subtle "Get next week's picks" signup (post-purchase timing)
- **LinkedIn Follow**: "Follow for weekly leadership insights" prompt
- **Social Sharing**: "Share this recommendation" buttons for virality

### 4.2 Conversion Optimization Based on Top Affiliate Site Analysis

#### The Wirecutter Model: Trust Through Testing

**Applied to MyBookshelf:**

- "Every book tested against Christian principles"
- "We read first, then recommend"
- Transparent affiliate disclosure builds trust

#### OutdoorGearLab Model: Visual Credibility

**Applied to MyBookshelf:**

- High-quality book cover photography
- "Hands-on testing" imagery (books on desk, reading environment)
- Clear rating system for quick decisions

#### Pack Hacker Model: Impulse Purchase Psychology

**Applied to MyBookshelf:**

- "Flat lay" book photography showing book + journal + pen setup
- Lifestyle integration ("Perfect for your morning devotion")
- Visual storytelling that triggers purchase desire

### 4.3 Anti-Friction Design Principles

#### Speed Optimization:

- CDN for all images
- Lazy loading for below-fold content
- Minimal JavaScript for core functionality
- <2 second Time to Interactive (TTI)

#### Mobile-First Experience:

- Touch-friendly buttons (minimum 44px)
- Readable typography without zooming
- Thumb-accessible navigation
- Single-column layout for easy scrolling

#### Clear Value Hierarchy:

1. **Primary**: Main book recommendation with large CTA
2. **Secondary**: Additional book choices
3. **Tertiary**: Newsletter signup and social follow

#### Trust Signal Implementation:

- SSL certificate badge
- "Christian-vetted" content guarantee
- Transparent affiliate relationship disclosure
- Professional photography and design

### 4.4 Revenue Optimization Strategy

#### Primary Revenue: Amazon Affiliate Commissions

- Focus on NEW book sales (4% commission rate)
- Optimize for Kindle + Paperback cross-selling
- Track conversion rates by traffic source

#### Secondary Revenue Streams (Future):

- Gumroad leadership guides ($5-15 products)
- Christian leadership course affiliates
- Book summary subscription service

#### Performance Metrics:

- LinkedIn direct-to-Amazon conversion (target: 3-7%) - Primary path
- LinkedIn to mini-site traffic (target: 1-3%) - Secondary path
- Mini-site email signup rate (target: 15-25%) - List building goal
- Overall LinkedIn to purchase (target: 0.5-1%)

### 4.5 Weekly Content Cycle Integration

#### Sunday: Primary Posting Day

- **Morning**: LinkedIn post with week's recommendations
- **Afternoon**: Email to subscribers with same content
- **Evening**: Monitor engagement and respond to comments

#### Monday-Saturday: Engagement Strategy

- **Daily**: 5 LinkedIn group comments on leadership topics
- **Daily**: 20 connection requests to Christian business leaders
- **Wednesday**: Mid-week leadership insight post (non-promotional)

#### Monthly: Content Optimization

- **Week 1**: A/B test LinkedIn post formats
- **Week 2**: Optimize mini-site conversion elements
- **Week 3**: Analyze Amazon conversion patterns
- **Week 4**: Plan next month's book selection strategy

## 5. Implementation Plan

### Week 1: Setup and Initial Automation

- **Day 1**: Set up Supabase (free), create complete database schema (`books_accessories`, `scraping_queue`, `admin_sessions`, `approval_log`). Create LinkedIn OAuth app.
- **Day 2**: Build Python scraping script with Christian content filtering and scoring system. Implement scraping queue population.
- **Day 3**: Develop admin authentication system and basic dashboard UI with secure login for mcddsl@icloud.com.
- **Day 4**: Set up Pipedream: Weekly scraping automation, admin approval workflow, Sunday email notifications to mcddsl@icloud.com.
- **Day 5**: Deploy mini-app (Supabase API endpoint, basic HTML) with approved items only. Add link to LinkedIn bio.
- **Day 6-7**: Test first weekly scraping cycle, admin approval process, and LinkedIn automation. Prepare for Sunday publication cycle.

### Week 2: Refine and Scale

- **Day 8-9**: Refine scraping filters and approval workflow based on first week results. Fix any issues with Christian content filtering. Gain 2-5 followers via 5 Group comments, 10 invites/day.
- **Day 10-11**: Run second weekly scraping cycle and Sunday publication. Monitor approval process efficiency and content quality.
- **Day 12-14**: Enhance mini-app UI (add categories, author diversity beyond Lencioni). Analyze scraped content diversity and engagement. Total: $1-$5, 2-5 followers.

## 6. Risks and Mitigations

- **Risk**: PA API throttling (1-2 requests/day).
  - **Mitigation**: Limit to 4 items/week; use ScrapingBee ($1).
- **Risk**: Low follower growth (2-5).
  - **Mitigation**: Increase Group comments to 10/day, invites to 20/day.
- **Risk**: Low revenue ($1-$5).
  - **Mitigation**: Add manual Gumroad $5 PDF (2-5 sales = $10-$25).
- **Risk**: Anti-Christian content slipping through filters.
  - **Mitigation**: Multi-layer filtering system: automated keyword filtering + human admin approval + Sunday email review to mcddsl@icloud.com.
- **Risk**: Over-dependence on Patrick Lencioni books.
  - **Mitigation**: Diversify to include various Christian leadership authors while maintaining content quality standards.

## 7. Success Metrics

- **Revenue**: $1-$5 (1-2 Amazon sales).
- **Followers**: 2-5 via organic growth.
- **Automation**: 100% uptime for script, Pipedream, Supabase.
- **Christian Alignment**: Include 1-2 Christian books (e.g., Lencioni); cite Proverbs 16:3 in posts.
- **User Experience**: <3 second decision time from LinkedIn to Amazon purchase intent.
- **Conversion Metrics**: 0.5-1% overall LinkedIn to purchase conversion rate.

## 8. Future Enhancements

- Add Gumroad automation (Zapier, $14/month).
- Scale to 10 books/week, 50-200 followers.
- Enhance mini-app with user login (Supabase auth).
