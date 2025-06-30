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
  - Generate 200-word posts with practical examples and biblical wisdom alignment for each book/accessory
  - **Tuesday/Wednesday/Thursday Publication Schedule**:
    - **Tuesday**: 1-2 books with leadership principles and biblical alignment
    - **Wednesday**: 1-2 books with practical application examples
    - **Thursday**: 1-2 books + 1 accessory with comprehensive recommendations
  - **Sunday Approval Workflow**: Email admin with approval link, schedule posts for upcoming Tue/Wed/Thu after approval
  - Use Pipedream to email post for approval (yes/no), then schedule posts via LinkedIn OAuth app.
- **Mini-App & Community Platform**:
  - Supabase-hosted webpage (Next.js or HTML) to browse recommendations (title, author, link).
  - **Prayer/Community Page**: Platform for prayer requests and work/faith discussions among Christian professionals.
  - **Sunday Encouragement Emails**: Weekly inspirational content (non-book related) for community building.
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

- **Frontend**: Mini-app + Community Platform + Admin Dashboard (Supabase API, Next.js/HTML, hosted on Vercel).
- **Backend**: Supabase Postgres (tables: `books_accessories`, `scraping_queue`, `admin_sessions`, `prayer_requests`, `community_posts`), Python SDK for CRUD.
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
  status VARCHAR(20) DEFAULT 'pending', -- pending, approved, rejected, scheduled
  admin_notes TEXT,
  reviewed_date TIMESTAMP,
  reviewed_by VARCHAR(100) DEFAULT 'admin',
  scheduled_post_date DATE, -- Tuesday, Wednesday, or Thursday assignment
  post_content TEXT, -- Generated post with practical examples + biblical wisdom
  practical_examples TEXT, -- How this book helps in real scenarios
  biblical_alignment TEXT -- Scripture references and wisdom principles
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

-- Prayer requests for community page
CREATE TABLE prayer_requests (
  id SERIAL PRIMARY KEY,
  user_name VARCHAR(100) NOT NULL,
  user_email VARCHAR(200),
  request_text TEXT NOT NULL,
  category VARCHAR(50), -- work, personal, leadership, business, etc.
  is_anonymous BOOLEAN DEFAULT FALSE,
  status VARCHAR(20) DEFAULT 'active', -- active, answered, archived
  created_at TIMESTAMP DEFAULT NOW(),
  admin_response TEXT,
  admin_responded_at TIMESTAMP,
  prayer_count INTEGER DEFAULT 0 -- community engagement tracking
);

-- Community discussions for work/faith integration
CREATE TABLE community_posts (
  id SERIAL PRIMARY KEY,
  user_name VARCHAR(100) NOT NULL,
  user_email VARCHAR(200),
  title VARCHAR(300) NOT NULL,
  content TEXT NOT NULL,
  category VARCHAR(50), -- leadership, faith-at-work, biblical-business, etc.
  is_anonymous BOOLEAN DEFAULT FALSE,
  status VARCHAR(20) DEFAULT 'active', -- active, archived, featured
  created_at TIMESTAMP DEFAULT NOW(),
  admin_featured BOOLEAN DEFAULT FALSE,
  engagement_count INTEGER DEFAULT 0
);

-- Community engagement tracking
CREATE TABLE community_engagement (
  id SERIAL PRIMARY KEY,
  post_id INTEGER REFERENCES community_posts(id),
  prayer_id INTEGER REFERENCES prayer_requests(id),
  user_email VARCHAR(200),
  engagement_type VARCHAR(20), -- prayer, comment, support, amen
  created_at TIMESTAMP DEFAULT NOW()
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
POST /api/admin/approve/:id        - Approve single item with date assignment
POST /api/admin/reject/:id         - Reject single item
POST /api/admin/batch-action       - Bulk approve/reject with date assignments
GET  /api/admin/calendar           - View upcoming posting calendar
POST /api/admin/schedule-posts     - Schedule approved items for Tue/Wed/Thu
GET  /api/admin/history           - Approval history
POST /api/admin/promote-approved   - Move approved items to live database
GET  /api/admin/generate-content   - Generate post content with examples + biblical wisdom
POST /api/admin/encouragement      - Send weekly Sunday encouragement email
GET  /api/admin/prayer-requests    - View and respond to community prayer requests
POST /api/admin/feature-post       - Feature community discussion posts
GET  /api/community/prayers        - Public prayer request feed
POST /api/community/submit-prayer  - Submit new prayer request
GET  /api/community/discussions    - Community work/faith discussion feed
POST /api/community/submit-post    - Submit new community discussion
POST /api/community/engage         - Record prayer/support engagement
```

## 3.2 Publishing Calendar & Content Generation System

**Calendar Management Requirements:**

- **Sunday Workflow**: Items scraped → Email sent to admin → Admin reviews items on approval site
- **Date Assignment**: Admin assigns each approved item to specific Tuesday, Wednesday, or Thursday post slots
- **Content Requirements**: Each item must include:
  - Practical examples of how the book helps in real scenarios
  - Biblical wisdom principles that the book's concepts align with
  - Scripture references relevant to leadership principles
  - Integration with existing business/leadership practices

**Calendar Interface Features:**

- **Weekly View**: Visual calendar showing Tuesday/Wednesday/Thursday slots
- **Drag & Drop**: Easy assignment of approved items to posting dates
- **Content Preview**: Generated post content with practical examples + biblical alignment
- **Scheduling Logic**:
  - Tuesday: 1-2 leadership foundation books
  - Wednesday: 1-2 practical application books
  - Thursday: 1-2 books + 1 accessory (comprehensive week wrap-up)

**Content Generation Templates:**

```sql
-- Add content fields to scraping_queue table
ALTER TABLE scraping_queue ADD COLUMN practical_example_1 TEXT;
ALTER TABLE scraping_queue ADD COLUMN practical_example_2 TEXT;
ALTER TABLE scraping_queue ADD COLUMN biblical_principle TEXT;
ALTER TABLE scraping_queue ADD COLUMN scripture_reference VARCHAR(100);
ALTER TABLE scraping_queue ADD COLUMN leadership_application TEXT;
```

## 3.3 Community Platform Integration - Discourse Implementation 🆕

**Phase 2 Community Development: Discourse Integration Strategy**

Based on analysis of existing community platforms, we will implement **Discourse** as our community/prayer platform to accelerate development while providing enterprise-grade community features.

### Implementation Architecture

```
Main Site (mybookshelf.shop)
├── Book recommendations & affiliate links
├── Sunday encouragement emails
├── Community highlights from Discourse API
└── Prayer request highlights on homepage

Community Platform (community.mybookshelf.shop)
├── Prayer Requests category
├── Work & Faith Discussions
├── Book Discussion threads
├── Leadership Challenges forum
└── Admin moderation tools for mcddsl@icloud.com
```

### Technical Implementation Plan

**Phase 2A: Discourse Setup (Week 1)**

- Deploy Discourse via Docker on subdomain `community.mybookshelf.shop`
- Configure SSL certificates and domain routing
- Set up PostgreSQL database for Discourse (separate from main Supabase)
- Configure email integration for notifications

**Phase 2B: Community Configuration (Week 1-2)**

- Create categories: Prayer Requests, Work & Faith, Book Discussions, Leadership Challenges
- Configure moderation settings for admin approval workflow
- Set up user authentication and registration system
- Configure privacy settings and content guidelines

**Phase 2C: API Integration (Week 2)**

- Implement Discourse API integration for main site
- Display recent prayer requests on main site homepage
- Show community highlights and engagement metrics
- Cross-platform user authentication and session management

### API Integration Specifications

```javascript
// Display recent prayer requests on main site
async function getPrayerRequests() {
  const response = await fetch(
    "https://community.mybookshelf.shop/latest.json"
  );
  const data = await response.json();
  return data.topic_list.topics.filter(
    (topic) => topic.category_id === PRAYER_CATEGORY_ID
  );
}

// Display community engagement stats
async function getCommunityStats() {
  const response = await fetch(
    "https://community.mybookshelf.shop/site/statistics.json"
  );
  return {
    active_prayers: response.data.prayer_count,
    community_members: response.data.users_count,
    discussions_this_week: response.data.topics_7_days,
  };
}
```

### Database Schema Extensions

```sql
-- Add community integration tracking to main database
ALTER TABLE books_accessories ADD COLUMN discourse_topic_id INTEGER;
ALTER TABLE prayer_requests ADD COLUMN discourse_topic_id INTEGER;

-- Track cross-platform engagement
CREATE TABLE community_integration (
  id SERIAL PRIMARY KEY,
  main_site_user_id INTEGER,
  discourse_user_id INTEGER,
  discourse_username VARCHAR(100),
  created_at TIMESTAMP DEFAULT NOW(),
  last_sync TIMESTAMP DEFAULT NOW()
);
```

### Discourse Configuration for Christian Community

**Categories Structure:**

- 🙏 **Prayer Requests** (moderated, admin approval required)
- 💼 **Work & Faith Integration** (open discussion)
- 📚 **Book Discussions** (auto-created from book recommendations)
- 👑 **Leadership Challenges** (practical workplace scenarios)
- 📢 **Community Announcements** (admin only posting)

**Moderation Settings:**

- All prayer requests require admin approval before publication
- Anonymous posting option for sensitive prayer requests
- Content filtering for Christian values alignment
- Email notifications to mcddsl@icloud.com for new submissions

### Integration Benefits

**Immediate Value:**

- Professional community platform without custom development
- Battle-tested moderation and user management
- Mobile-responsive design optimized for engagement
- Rich text editor with image support for discussions

**Long-term Scalability:**

- Plugin ecosystem for additional Christian-focused features
- Advanced search and organization of prayer requests and discussions
- Email digest and notification systems
- API-driven integration with main platform growth

**Timeline:** 1-2 weeks to full community functionality

## 4. User Interaction & Marketing Flow: Virtuous Conversion Cycle

### 4.1 Complete User Journey: LinkedIn → Mini-Site → Amazon

**Based on analysis of top Amazon affiliate sites including The Wirecutter, OutdoorGearLab, and Pack Hacker**

#### Phase 1: LinkedIn Direct Conversion (Tuesday/Wednesday/Thursday Posts) - PRIMARY PATH

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
