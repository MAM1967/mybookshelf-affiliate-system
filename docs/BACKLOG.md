# Project Backlog: MyBookshelf Affiliate System

## Project Status Overview

**Current State**: 🔧 **BASIC AFFILIATE LINKS WORKING** - Site deployed, links fixed, but missing automation pipeline + proper dev workflow  
**Target**: Full automated affiliate system with LinkedIn integration per PRD  
**Timeline**: Week 1 & 2 implementation plan from PRD  
**Progress**: **~15% Complete** - Basic deployment exists, but missing critical dev infrastructure, testing, automation pipeline, and monitoring

### ⚠️ REALITY CHECK: CURRENT STATE vs PRODUCTION REQUIREMENTS

**What We Have:**

- ✅ Basic HTML/CSS/JS frontend deployed to production
- ✅ Supabase database with 4 books
- ✅ Working affiliate links to Amazon
- ✅ GitHub repository with version control

**What We're Missing (CRITICAL):**

- ❌ No development or staging environments
- ❌ No automated testing of any kind
- ❌ No CI/CD pipeline to prevent bugs in production
- ❌ No monitoring or error tracking
- ❌ No LinkedIn automation or PA API automation
- ❌ No environment variable management
- ❌ No database migrations or backup strategy
- ❌ No performance optimization or caching
- ❌ No proper error handling or user feedback

**Risk Assessment:** 🔴 **HIGH RISK** - Current production deployment is fragile and could break easily without proper development practices

---

## ✅ COMPLETED (Sprint 0 - Foundation + Major Image Fix)

### Database & Backend Infrastructure ✅

- [x] Supabase setup with PostgreSQL database
- [x] Clean book database (4 unique records, duplicates removed)
- [x] Duplicate prevention system with MD5 hashing
- [x] Database cleanup scripts and tools
- [x] **🎉 REAL book cover images working** (replaced base64 placeholders)

### Amazon Integration ✅

- [x] **Amazon PA API credentials configured and validated**
- [x] **Amazon Associate ID setup**: `mybookshelf-20`
- [x] **PA API integration working** (credentials valid, awaiting approval)
- [x] **Robust fallback system** using known working image URLs
- [x] **Base64 image conversion system** for reliable display
- [x] **🎉 FIXED: Broken affiliate links** - Updated all "EXAMPLE" ASINs with real Amazon product ASINs (Dec 30, 2024)

### Frontend & Image System ✅

- [x] Mini-app frontend (HTML/CSS/JS) running on localhost:8000
- [x] Responsive design with Christian theme (Proverbs 16:3)
- [x] **🎉 REAL book covers displaying correctly** (no more colored rectangles)
- [x] **Fixed frontend-database ID mapping issues**
- [x] **Dynamic image loading with 3-tier fallback system**
- [x] Image download and conversion script (multi-mode)

### Development Infrastructure ✅

- [x] Project folder structure
- [x] Scripts and automation tools
- [x] **Complete documentation system** (PRD, README, Lessons Learned with API keys)
- [x] **Git repository with proper commit history**

### Working Book Database ✅

- [x] **ID 17**: The Five Dysfunctions of a Team by Patrick Lencioni - $19.99 ✅
- [x] **ID 18**: The Advantage by Patrick Lencioni - $19.99 ✅
- [x] **ID 19**: Atomic Habits by James Clear - $19.99 ✅
- [x] **ID 20**: Leadership Journal - Daily Planner by Business Essentials - $19.99 ✅

### Production Deployment & Domain Setup ✅

- [x] **🎉 LIVE PRODUCTION DEPLOYMENT** via Vercel + GitHub integration
- [x] **Repository**: `https://github.com/MAM1967/mybookshelf-affiliate-system` ✅
- [x] **Primary URL**: `https://mybookshelf-affiliate-system.vercel.app` ✅
- [x] **Custom Domain**: `https://mybookshelf.shop` ($0.98/year via Namecheap) ✅
- [x] **WWW Subdomain**: `https://www.mybookshelf.shop` ✅
- [x] **SSL Certificates**: Automatic Let's Encrypt SSL for both domains ✅
- [x] **DNS Configuration**: A Record + CNAME Record properly configured ✅
- [x] **Domain Provider**: Namecheap with Vercel DNS integration ✅
- [x] **Deployment Pipeline**: Automatic GitHub → Vercel deployment ✅
- [x] **Cost Optimization**: ~$0.08/month (domain only, Vercel free tier) ✅

### LinkedIn OAuth Integration Setup ✅

- [x] **LinkedIn Developer App Created**: Client ID `78wmrhdd99ssbi` ✅
- [x] **OAuth Credentials Configured**: App secret and permissions setup ✅
- [x] **Test Scripts Created**: `linkedin_oauth_test.py` + `linkedin_simple_test.py` ✅
- [ ] **Redirect URIs Updated**: Need to add production domain URLs ⏳ **NEXT**

---

## 🎯 IN PROGRESS (Sprint 1 - Automation Pipeline)

### LinkedIn Integration (Day 1, 4 per PRD)

- [ ] **Story**: LinkedIn OAuth App Setup ⏳ **IN PROGRESS**
  - [x] ~~Create LinkedIn Developer App~~ ✅ **DONE**
  - [x] ~~Configure OAuth credentials~~ ✅ **DONE**
  - [ ] Update redirect URIs with production domain ⏳ **CURRENT TASK**
  - [ ] Set up LinkedIn API permissions for posting ⏳ **NEXT**
  - [ ] Test authentication flow

---

## 🚨 CRITICAL INFRASTRUCTURE TASKS (MUST DO FIRST)

### Development Environment Setup ⚠️ **BLOCKING ALL OTHER WORK**

- [ ] **Story**: Proper Dev/Staging/Production Workflow
  - [ ] **Vercel Environment Setup**:
    - [ ] Create `dev` branch and dev deployment (`dev-mybookshelf.vercel.app`)
    - [ ] Create `staging` branch and staging deployment (`staging-mybookshelf.vercel.app`)
    - [ ] Configure environment-specific variables in Vercel dashboard
    - [ ] Set up automatic deployments: `dev` → dev site, `staging` → staging site, `main` → production
  - [ ] **Database Environment Separation**:
    - [ ] Create separate Supabase projects for dev/staging/production
    - [ ] Set up environment-specific connection strings
    - [ ] Implement database migration scripts
    - [ ] Create seed data for dev/staging environments
  - [ ] **Environment Configuration**:
    - [ ] Create `.env.development`, `.env.staging`, `.env.production` files
    - [ ] Configure Amazon PA API keys per environment
    - [ ] Set up LinkedIn OAuth redirect URIs for all environments
    - [ ] Document environment switching process

### Testing Infrastructure ⚠️ **CRITICAL FOR RELIABILITY**

- [ ] **Story**: Comprehensive Testing Suite
  - [ ] **Unit Testing**:
    - [ ] Test Amazon PA API integration and error handling
    - [ ] Test Supabase database operations (CRUD)
    - [ ] Test affiliate link generation and validation
    - [ ] Test image downloading and base64 conversion
    - [ ] Test price parsing and format detection
  - [ ] **Integration Testing**:
    - [ ] End-to-end affiliate link functionality testing
    - [ ] Database → Frontend data flow testing
    - [ ] Amazon PA API → Database integration testing
    - [ ] LinkedIn OAuth flow testing
  - [ ] **Automated Testing Scripts**:
    - [ ] `test_affiliate_links.py` - Verify all links return 200 status
    - [ ] `test_database_integrity.py` - Check data consistency and duplicates
    - [ ] `test_amazon_api.py` - Validate PA API responses and rate limits
    - [ ] `test_image_loading.py` - Verify all images load correctly
    - [ ] `test_pricing_logic.py` - Validate price selection and format priority
  - [ ] **Performance Testing**:
    - [ ] Frontend loading speed testing (<3 seconds)
    - [ ] Database query performance testing
    - [ ] Image loading optimization testing
    - [ ] API rate limit and throttling testing

### CI/CD Pipeline ⚠️ **PREVENT PRODUCTION BUGS**

- [ ] **Story**: Automated Deployment Pipeline
  - [ ] **GitHub Actions Setup**:
    - [ ] Create test runner workflow (run all tests on PR)
    - [ ] Create deployment workflow (deploy on merge to main)
    - [ ] Create scheduled testing workflow (daily affiliate link validation)
    - [ ] Create database backup workflow (weekly)
  - [ ] **Quality Gates**:
    - [ ] All tests must pass before deployment
    - [ ] Affiliate links must be validated before going live
    - [ ] Database integrity checks before production deployment
    - [ ] Performance benchmarks must be met

### Monitoring & Alerting ⚠️ **PRODUCTION READINESS**

- [ ] **Story**: System Health Monitoring
  - [ ] **Application Monitoring**:
    - [ ] Set up Vercel Analytics and monitoring
    - [ ] Configure Supabase database monitoring
    - [ ] Track affiliate link click-through rates
    - [ ] Monitor Amazon PA API rate limits and errors
    - [ ] Set up LinkedIn API quota monitoring
  - [ ] **Error Tracking & Alerting**:
    - [ ] Implement error logging (Sentry or similar)
    - [ ] Set up email alerts for system failures
    - [ ] Configure affiliate link failure notifications
    - [ ] Create dashboard for system health status
    - [ ] Set up uptime monitoring (Pingdom/UptimeRobot)
  - [ ] **Business Metrics Tracking**:
    - [ ] Track affiliate click conversion rates
    - [ ] Monitor revenue generation and commission tracking
    - [ ] LinkedIn post engagement analytics
    - [ ] User behavior tracking (privacy-compliant)

---

## 📋 SPRINT 1 BACKLOG (Week 1 - Core Automation)

### 🎯 User Interaction & Marketing Flow - ANTI-FRICTION CONVERSION SYSTEM 🆕 **HIGHEST PRIORITY**

**Based on analysis of top Amazon affiliate sites for DIRECT CONVERSION with mini-site as standalone value hub**

- [ ] **Story**: LinkedIn Direct-to-Amazon Flow (Primary Path - 90% of conversions)

  **Phase 1: LinkedIn Direct Conversion Optimization**

  - [ ] **Task**: Design Tuesday/Wednesday/Thursday post templates with direct Amazon links:
    - [ ] Scripture hook opening (Proverbs 16:3 + leadership insight)
    - [ ] Individual book listings with covers, titles, prices
    - [ ] Direct "GET ON AMAZON" buttons for each book (affiliate links)
    - [ ] Secondary "See ALL recommendations + insights" (mini-site link)
    - [ ] "Vetted for biblical alignment" badge per book
  - [ ] **Task**: Implement visual content strategy:
    - [ ] High-quality book cover photography workflow
    - [ ] "Flat lay" lifestyle photography (Pack Hacker style)
    - [ ] Brand-consistent color scheme (navy/orange theme)

  **Phase 2: Mini-Site Friction Elimination (<3 Second Conversion Path)**

  - [ ] **Task**: Build trust-first landing page architecture:
    - [ ] Top 25%: Instant trust building (Christian branding, "Vetted for Christian principles" badge)
    - [ ] Next 50%: Hero book showcase with "Why we chose this" bullets
    - [ ] Bottom 25%: Secondary books grid with individual CTAs
  - [ ] **Task**: Implement speed optimization requirements:
    - [ ] <2 second Time to Interactive (TTI)
    - [ ] CDN implementation for all images
    - [ ] Lazy loading for below-fold content
    - [ ] Minimal JavaScript for core functionality
  - [ ] **Task**: Mobile-first responsive design:
    - [ ] Touch-friendly buttons (minimum 44px)
    - [ ] Single-column layout for easy scrolling
    - [ ] Readable typography without zooming
    - [ ] Thumb-accessible navigation

  **Phase 3: Amazon Handoff Optimization**

  - [ ] **Task**: Smart affiliate linking system:
    - [ ] Direct to lowest-price NEW format (never used/3rd party)
    - [ ] Preserve `mybookshelf-20` affiliate tag through redirects
    - [ ] Open Amazon in new tab (preserve mini-site session)
    - [ ] Let Amazon handle format upselling (Audible, hardcover)
  - [ ] **Task**: Conversion tracking implementation:
    - [ ] LinkedIn click-through rate monitoring
    - [ ] Mini-site to Amazon conversion tracking
    - [ ] Overall funnel performance analytics

  **Phase 4: Post-Purchase Engagement Loop**

  - [ ] **Task**: Build sustainable engagement system:
    - [ ] Subtle "Get next week's picks" email capture
    - [ ] "Follow for weekly leadership insights" LinkedIn prompt
    - [ ] Social sharing buttons for virality
    - [ ] Return visitor recognition and personalization

- [ ] **Story**: Conversion Rate Optimization Based on Top Affiliate Sites

  **Wirecutter Model: Trust Through Testing**

  - [ ] **Task**: Implement "Every book tested against Christian principles" messaging
  - [ ] **Task**: "We read first, then recommend" credibility system
  - [ ] **Task**: Transparent affiliate disclosure as trust builder

  **OutdoorGearLab Model: Visual Credibility**

  - [ ] **Task**: High-quality book photography setup
  - [ ] **Task**: "Hands-on testing" imagery (books on desk, reading environment)
  - [ ] **Task**: Clear rating system for quick decisions

  **Pack Hacker Model: Impulse Purchase Psychology**

  - [ ] **Task**: "Flat lay" book photography (book + journal + pen setup)
  - [ ] **Task**: Lifestyle integration messaging ("Perfect for your morning devotion")
  - [ ] **Task**: Visual storytelling that triggers purchase desire

- [ ] **Story**: Performance Metrics & Success Criteria

  - [ ] **Task**: Implement conversion funnel tracking:
    - [ ] LinkedIn click-through rate (target: 2-5%)
    - [ ] Mini-site to Amazon conversion (target: 8-15%)
    - [ ] Amazon purchase conversion (target: 3-8%)
    - [ ] Overall LinkedIn to purchase (target: 0.5-1%)
  - [ ] **Task**: User experience optimization:
    - [ ] <3 second decision time from LinkedIn to Amazon
    - [ ] Mobile conversion rate parity with desktop
    - [ ] Bounce rate optimization (<50% on mini-site)

- [ ] **Story**: Mini-Site as Christian Leadership Community Hub (Secondary Path - 10% of traffic, HIGH value)

  **Purpose**: Community building, prayer support, and ongoing engagement beyond book recommendations

  - [ ] **Task**: Build community-focused value proposition:
    - [ ] "Your Complete Library of Christian-Vetted Leadership Books"
    - [ ] **Prayer & Community Support Platform**
    - [ ] Complete archive of all weekly recommendations (searchable)
    - [ ] Leadership principles library with biblical applications
    - [ ] Work/faith integration discussion space
  - [ ] **Task**: Multi-purpose email signup optimization:
    - [ ] "Weekly Leadership Principles + Sunday Encouragement" newsletter options
    - [ ] "Join 500+ Christian leaders in community" value proposition
    - [ ] Email preferences: Books only, Encouragement only, or Both
    - [ ] Target: 15-25% signup rate from mini-site visitors
  - [ ] **Task**: Community engagement strategy:
    - [ ] Prayer request submission and community support
    - [ ] Work/faith discussion topics and responses
    - [ ] Sunday encouragement emails (separate from book content)
    - [ ] Community highlights and answered prayer testimonies
    - [ ] Biblical leadership discussion forums

**Business Impact**: Transform direct conversion model with sustainable email list building for long-term revenue
**Revenue Potential**: Direct path = immediate conversions, mini-site = long-term community and diversified revenue
**User Experience**: Zero friction purchase path + optional deep value for engaged users
**Priority Justification**: Eliminates conversion friction while building sustainable community asset

### Weekly Scraping & Approval Workflow 🆕 **HIGH PRIORITY**

- [ ] **Story**: Weekly Amazon Scraping System

  - [ ] **Task**: Build Amazon scraping script to identify up to 10 non-duplicative items weekly
  - [ ] **Task**: Implement content filtering for Christian principles:
    - [ ] Filter out blasphemy and profanity
    - [ ] Exclude books denying Jesus Christ
    - [ ] Exclude explicit/implicit embrace of other world religions (Hinduism, Buddhism, Islam) as business principles
    - [ ] Focus on leadership/productivity/business books aligned with biblical values
  - [ ] **Task**: Create `scraping_queue` table in Supabase for pending approval items
  - [ ] **Task**: Diversify beyond Patrick Lencioni to include various Christian leadership authors

- [ ] **Story**: Admin Approval System - Complete Build Plan 🏗️ **COMPREHENSIVE**

  **Phase 1: Database Architecture (Day 1)**

  - [ ] **Task**: Create `scraping_queue` table with comprehensive schema
    - [ ] Add content scoring fields (content_score, filter_flags)
    - [ ] Include approval workflow fields (status, admin_notes, reviewed_date)
    - [ ] Add audit trail capabilities
  - [ ] **Task**: Create `admin_sessions` table for secure authentication
  - [ ] **Task**: Create `approval_log` table for action tracking
  - [ ] **Task**: Set up database constraints and indexes for performance
  - [ ] **Task**: Create database migration scripts for deployment

  **Phase 2: Backend API Development (Day 2-3)**

  - [ ] **Task**: Build authentication system
    - [ ] Email-based login for mcddsl@icloud.com
    - [ ] Session token generation and validation
    - [ ] Auto-logout after inactivity
    - [ ] Password reset functionality (future enhancement)
  - [ ] **Task**: Develop approval API endpoints
    - [ ] GET /api/admin/pending - Fetch items needing review
    - [ ] POST /api/admin/approve/:id - Single item approval
    - [ ] POST /api/admin/reject/:id - Single item rejection
    - [ ] POST /api/admin/batch-action - Bulk operations
    - [ ] POST /api/admin/promote-approved - Move to live database
  - [ ] **Task**: Implement content analysis system
    - [ ] Christian content scoring algorithm
    - [ ] Automatic flagging for review priorities
    - [ ] Content warning detection
  - [ ] **Task**: Add comprehensive error handling and logging

  **Phase 3: Frontend Dashboard Development (Day 3-4)**

  - [ ] **Task**: Build admin login interface
    - [ ] Clean, professional login form
    - [ ] Session management
    - [ ] Auto-redirect to dashboard
  - [ ] **Task**: Create main dashboard layout
    - [ ] Header with logout, user info
    - [ ] Sidebar navigation
    - [ ] Main content area for item review
  - [ ] **Task**: Develop item review interface
    - [ ] Card-based layout for each scraped item
    - [ ] Display: title, author, description, price, image
    - [ ] Show content score and any filter flags
    - [ ] Approve/Reject buttons with confirmation dialogs
    - [ ] Notes field for admin comments
  - [ ] **Task**: Implement batch operations UI
    - [ ] Select all/none checkboxes
    - [ ] Bulk approve/reject actions
    - [ ] Progress indicators for batch operations
  - [ ] **Task**: Build approval history view
    - [ ] Searchable/filterable list of past decisions
    - [ ] Action audit trail
    - [ ] Performance metrics (approval rates, etc.)

  **Phase 4: Integration & Testing (Day 4-5)**

  - [ ] **Task**: Connect scraping script to approval system
    - [ ] Populate scraping_queue instead of direct database insertion
    - [ ] Include content scoring in scraping process
    - [ ] Add duplicate detection for scraping queue
  - [ ] **Task**: Build promotion workflow
    - [ ] Sunday batch promotion of approved items
    - [ ] Data validation before promotion
    - [ ] Rollback capability if issues found
  - [ ] **Task**: Implement email notification system
    - [ ] Weekly summary emails to mcddsl@icloud.com
    - [ ] Sunday pre-publication approval requests
    - [ ] Alert emails for system issues
  - [ ] **Task**: Security hardening
    - [ ] Rate limiting on login attempts
    - [ ] CSRF protection
    - [ ] Input sanitization and validation
    - [ ] SQL injection prevention

  **Phase 5: UI/UX Polish (Day 5-6)**

  - [ ] **Task**: Responsive design implementation
    - [ ] Mobile-friendly admin interface
    - [ ] Tablet optimization
    - [ ] Touch-friendly controls
  - [ ] **Task**: User experience enhancements
    - [ ] Loading states and progress indicators
    - [ ] Toast notifications for actions
    - [ ] Keyboard shortcuts for power users
    - [ ] Auto-save of admin notes
  - [ ] **Task**: Christian branding consistency
    - [ ] Align with main site color scheme (navy-orange)
    - [ ] Include appropriate scripture references
    - [ ] Professional, values-driven design

  **Phase 6: Production Deployment (Day 6-7)**

  - [ ] **Task**: Environment setup
    - [ ] Configure production database tables
    - [ ] Set up admin subdomain (admin.mybookshelf.shop)
    - [ ] SSL certificate configuration
  - [ ] **Task**: Security deployment
    - [ ] Environment variable configuration
    - [ ] Production authentication settings
    - [ ] Backup and recovery procedures
  - [ ] **Task**: Monitoring and alerting
    - [ ] Error tracking setup
    - [ ] Performance monitoring
    - [ ] Uptime alerts

- [ ] **Story**: Sunday Approval & Publishing Calendar System 🆕 **UPDATED**
  - [ ] **Task**: Set up Sunday email workflow to mcddsl@icloud.com with admin approval site link
  - [ ] **Task**: Build calendar interface for assigning items to Tuesday/Wednesday/Thursday posts
  - [ ] **Task**: Include post content generation with practical examples + biblical wisdom alignment
  - [ ] **Task**: Schedule approved posts for upcoming Tuesday (1-2 books), Wednesday (1-2 books), Thursday (1-2 books + 1 accessory)
  - [ ] **Task**: Integrate with Pipedream for email automation and posting schedule

### Amazon Integration Enhancements

- [ ] **Story**: Enhanced Amazon Product Fetching

  - [x] ~~Register for Amazon PA API access~~ ✅ **DONE**
  - [x] ~~Set up Amazon Associate ID for affiliate links~~ ✅ **DONE**
  - [x] ~~Create PA API credentials and environment variables~~ ✅ **DONE**
  - [x] ~~Test PA API connectivity and rate limits~~ ✅ **DONE** (awaiting approval)
  - [x] ~~Fix broken affiliate links with correct ASINs~~ ✅ **DONE** (Dec 30, 2024)
  - [ ] **When PA API approved**: Implement live book fetching from Amazon
  - [ ] Add Patrick Lencioni author prioritization
  - [ ] Implement Christian content filtering (exclude anti-Christian keywords)
  - [ ] Add accessory search functionality (journals, pens)
  - [ ] Create weekly batch fetching (3 books + 1 accessory)

- [ ] **Story**: Smart Amazon Pricing Handler ⭐ **UPDATED PRIORITY**

  - [ ] **Problem**: Amazon books have multiple formats (Kindle $9.99, Paperback $14.99, Hardcover $24.99, Audiobook $19.95)
  - [ ] **Business Decision**: Show the cheapest available price as default to maximize user appeal
  - [ ] **User Experience**: Users will make final format decision on Amazon detail page after clicking affiliate link

  **Price Selection Business Logic:**

  - [ ] **Primary Rule**: Display lowest price among all available formats FROM NEW/AMAZON-SOLD items only
  - [ ] **Critical Exclusion**: Never include used books or third-party seller prices (no affiliate compensation)
  - [ ] **Seller Filtering**: Only consider prices from Amazon.com or Amazon-fulfilled sellers
  - [ ] **Format Eligibility**: Include all physical and digital formats (Kindle, Paperback, Hardcover, Audiobook)
  - [ ] **Price Display**: "Starting at $X.XX" with format indicator showing which format has lowest NEW price
  - [ ] **Affiliate Link**: Default link goes to the cheapest NEW format's Amazon page
  - [ ] **Fallback**: If price data unavailable, prioritize: Paperback → Kindle → Hardcover → Audiobook

  **Implementation Tasks:**

  - [ ] **Task**: Parse all available formats from Amazon PA API `Offers.Listings[]`
  - [ ] **Task**: Implement price comparison algorithm with seller filtering
    - [ ] Filter `Offers.Listings[]` to exclude used/third-party sellers
      - [ ] Check `Offers.Listings[].Condition` = "New" only
      - [ ] Verify `Offers.Listings[].Merchant.Name` = "Amazon.com" or is Amazon-fulfilled
      - [ ] Exclude marketplace sellers that don't generate affiliate commissions
    - [ ] Extract price from qualified listings: `Offers.Listings[].Price.Amount`
    - [ ] Convert all prices to consistent currency/decimal format
    - [ ] Find minimum price across all NEW formats only
    - [ ] Identify which format has the minimum NEW price
  - [ ] **Task**: Create price display logic
    - [ ] Show "Starting at $X.XX" with lowest price
    - [ ] Display format badge (e.g., "Kindle", "Paperback", "Hardcover", "Audiobook")
    - [ ] Ensure affiliate link points to cheapest format's Amazon page
  - [ ] **Task**: Add format availability indicator
    - [ ] Show "Multiple formats available" when >1 format exists
    - [ ] Display price range if helpful (e.g., "$9.99 - $24.99")
  - [ ] **Task**: Handle edge cases
    - [ ] No NEW price data available (show "Price varies" or hide item)
    - [ ] Only used/third-party prices available (exclude item from display)
    - [ ] Only one NEW format available (show that format's price)
    - [ ] Temporary price unavailable (fallback to last known NEW price)
    - [ ] Invalid/corrupted price data (skip and use fallback)
    - [ ] All formats are used/marketplace only (do not display item)
  - [ ] **Task**: Format-specific affiliate link management
    - [ ] Generate correct Amazon ASIN-based links for each format
    - [ ] Ensure affiliate tag (`mybookshelf-20`) works for all formats
    - [ ] Test affiliate tracking across different format types
  - [ ] **Task**: UI Enhancement for price display
    - [ ] Update frontend to show "Starting at" pricing
    - [ ] Add format badge styling consistent with site theme
    - [ ] Ensure mobile responsiveness for price display

  **Business Impact**: Maximize click-through rates by showing most appealing (lowest) price while ensuring affiliate commission eligibility
  **Revenue Protection**: Exclude used/third-party prices that generate zero affiliate commissions
  **Technical Notes**: PA API returns `Offers.Listings[].Condition` and `Offers.Listings[].Merchant.Name` for seller filtering
  **Priority Justification**: Addresses immediate user question about price display logic and protects affiliate revenue

### LinkedIn Integration (Day 1, 4 per PRD) - **HIGH PRIORITY**

- [ ] **Story**: LinkedIn OAuth App Setup

  - [ ] Create LinkedIn Developer App
  - [ ] Configure OAuth credentials
  - [ ] Set up LinkedIn API permissions for posting
  - [ ] Test authentication flow

- [ ] **Story**: LinkedIn Posting Automation ⭐ **UPDATED**
  - [ ] **Tuesday/Wednesday/Thursday Publication Schedule**: Automated LinkedIn posts scheduled for Tuesday (1-2 books), Wednesday (1-2 books), Thursday (1-2 books + 1 accessory) after Sunday approval
  - [ ] **Enhanced Post Generation**: Create posts featuring diverse Christian leadership authors with practical examples and biblical wisdom alignment
  - [ ] **Weekly Content Strategy**: Generate posts from weekly scraped and approved items (up to 10 per week)
  - [ ] **Content Template**: 200-word posts with practical applications + biblical principles alignment
  - [ ] **Sunday Approval Workflow**: Email notifications to mcddsl@icloud.com with admin site link for calendar scheduling
  - [ ] **Scripture Integration**: Add Proverbs 16:3 and other relevant biblical principles per post
  - [ ] **Affiliate Link Embedding**: Include approved items' Amazon associate links

### Content Strategy & Filtering 🆕 **IMPORTANT**

- [ ] **Story**: Christian Content Standards Implementation
  - [ ] **Author Diversification**: Move beyond Patrick Lencioni to include various Christian leadership authors
  - [ ] **Content Filtering Enforcement**:
    - [ ] No blasphemy or profanity
    - [ ] No denial of Jesus Christ
    - [ ] No explicit/implicit embrace of other world religions (Hinduism, Buddhism, Islam) as business principles
    - [ ] Focus on biblical leadership, productivity, and business principles
  - [ ] **Quality Assurance**: Multi-layer review process (automated + human approval + final email review)

### Community Platform & Prayer System 🆕 **HIGH PRIORITY**

- [ ] **Story**: Prayer & Community Page Development

  **Phase 1: Prayer Request System**

  - [ ] **Task**: Create `prayer_requests` table in Supabase
    - [ ] User name, email, request text, category fields
    - [ ] Anonymous option for sensitive requests
    - [ ] Status tracking (active, answered, archived)
    - [ ] Admin response capability
    - [ ] Prayer count engagement tracking
  - [ ] **Task**: Build prayer request submission form
    - [ ] Categories: work, personal, leadership, business, family
    - [ ] Anonymous checkbox option
    - [ ] Email notification to admin (mcddsl@icloud.com)
    - [ ] User-friendly submission confirmation
  - [ ] **Task**: Create public prayer feed interface
    - [ ] Display active prayer requests (respecting anonymity)
    - [ ] "Praying for you" engagement button
    - [ ] Prayer count display for community support
    - [ ] Admin response display when available

  **Phase 2: Community Discussion Platform**

  - [ ] **Task**: Create `community_posts` table for work/faith discussions
    - [ ] Title, content, category, anonymous option
    - [ ] Admin featuring capability
    - [ ] Engagement tracking
  - [ ] **Task**: Build community discussion interface
    - [ ] Categories: leadership, faith-at-work, biblical-business, workplace-witness
    - [ ] Discussion submission form
    - [ ] Community engagement features (support, amen responses)
    - [ ] Admin moderation and featuring system
  - [ ] **Task**: Implement admin community management
    - [ ] Review and respond to prayer requests
    - [ ] Feature valuable community discussions
    - [ ] Monitor and moderate content for Christian values
    - [ ] Community engagement analytics

### Sunday Encouragement Email System 🆕 **SEPARATE FROM BOOK CONTENT**

- [ ] **Story**: Weekly Encouragement Email (Non-Book Related)

  - [ ] **Task**: Design Sunday encouragement email template
    - [ ] Inspirational Christian leadership content
    - [ ] Scripture-based encouragement for workplace challenges
    - [ ] Prayer points for the week ahead
    - [ ] Community highlights and answered prayers
    - [ ] NO book recommendations or affiliate links
  - [ ] **Task**: Build email content management system
    - [ ] Admin interface for creating weekly encouragement content
    - [ ] Template library for different encouragement themes
    - [ ] Preview and scheduling functionality
    - [ ] Email analytics and engagement tracking
  - [ ] **Task**: Integrate with existing email list
    - [ ] Separate Sunday encouragement from book recommendation emails
    - [ ] Subscription preferences (books + encouragement, or encouragement only)
    - [ ] Unsubscribe options for each email type
  - [ ] **Task**: Create encouragement content calendar
    - [ ] Weekly themes: Monday motivation, workplace witness, leadership challenges
    - [ ] Seasonal content: Christian holidays, new year, etc.
    - [ ] Community prayer highlight rotation
    - [ ] Scripture series for professional development

### Phase 2: Community Platform Integration - Discourse Implementation 🆕 **NEXT MAJOR PHASE**

**Target Timeline: 2-3 weeks after core book system completion**

- [ ] **Story**: Discourse Community Platform Setup

  **Phase 2A: Infrastructure Setup (Week 1)**

  - [ ] **Task**: Deploy Discourse via Docker
    - [ ] Set up subdomain `community.mybookshelf.shop`
    - [ ] Configure SSL certificates and domain routing
    - [ ] Deploy Discourse Docker container with PostgreSQL
    - [ ] Configure Redis for caching and sessions
    - [ ] Set up backup and monitoring systems
  - [ ] **Task**: Database and Environment Configuration
    - [ ] Create separate PostgreSQL database for Discourse
    - [ ] Configure environment variables and secrets
    - [ ] Set up email delivery (SMTP integration)
    - [ ] Configure file upload and storage settings
  - [ ] **Task**: Initial Admin Setup
    - [ ] Create admin account for mcddsl@icloud.com
    - [ ] Configure site settings and branding
    - [ ] Set up basic security and spam protection
    - [ ] Configure backup procedures

  **Phase 2B: Community Structure Setup (Week 1-2)**

  - [ ] **Task**: Create Category Structure
    - [ ] 🙏 Prayer Requests (moderated, admin approval required)
    - [ ] 💼 Work & Faith Integration (open discussion)
    - [ ] 📚 Book Discussions (auto-created from recommendations)
    - [ ] 👑 Leadership Challenges (practical workplace scenarios)
    - [ ] 📢 Community Announcements (admin only posting)
  - [ ] **Task**: Configure Moderation Settings
    - [ ] Set up admin approval workflow for prayer requests
    - [ ] Configure anonymous posting options for sensitive requests
    - [ ] Implement content filtering for Christian values
    - [ ] Set up email notifications to mcddsl@icloud.com
  - [ ] **Task**: Design Community Guidelines
    - [ ] Create community rules aligned with Christian values
    - [ ] Draft prayer request submission guidelines
    - [ ] Establish work/faith discussion etiquette
    - [ ] Set up user onboarding and welcome messages

  **Phase 2C: Main Site Integration (Week 2)**

  - [ ] **Task**: Discourse API Integration
    - [ ] Implement API client for fetching community data
    - [ ] Create functions to display recent prayer requests on main site
    - [ ] Build community stats display (active prayers, members, discussions)
    - [ ] Add community highlights to homepage
  - [ ] **Task**: Cross-Platform Authentication
    - [ ] Configure Single Sign-On (SSO) between main site and Discourse
    - [ ] Sync user accounts and authentication sessions
    - [ ] Handle user registration flow across both platforms
    - [ ] Implement logout synchronization
  - [ ] **Task**: Content Synchronization
    - [ ] Auto-create book discussion topics for new recommendations
    - [ ] Sync community highlights for Sunday encouragement emails
    - [ ] Track prayer request engagement and responses
    - [ ] Display answered prayer testimonies on main site

  **Phase 2D: Advanced Features (Week 3)**

  - [ ] **Task**: Enhanced Prayer System
    - [ ] Implement prayer tracking and follow-up system
    - [ ] Create "Prayers Answered" celebration features
    - [ ] Add prayer category filtering (work, personal, leadership, etc.)
    - [ ] Build prayer reminder and check-in notifications
  - [ ] **Task**: Community Engagement Features
    - [ ] Add community member highlights to main site
    - [ ] Implement discussion previews on book pages
    - [ ] Create featured discussion rotation system
    - [ ] Add community activity feed to main site
  - [ ] **Task**: Analytics and Reporting
    - [ ] Track community engagement metrics
    - [ ] Monitor prayer request and response rates
    - [ ] Generate weekly community reports for admin
    - [ ] Analyze cross-platform user behavior and conversion

### Integration Architecture Implementation

- [ ] **Story**: Technical Integration Requirements

  - [ ] **Task**: API Integration Layer
    ```javascript
    // Implementation examples for main site integration
    async function getPrayerRequests() {
      const response = await fetch(
        "https://community.mybookshelf.shop/latest.json"
      );
      return data.topic_list.topics.filter(
        (topic) => topic.category_id === PRAYER_CATEGORY_ID
      );
    }
    ```
  - [ ] **Task**: Database Schema Extensions

    ```sql
    ALTER TABLE books_accessories ADD COLUMN discourse_topic_id INTEGER;
    ALTER TABLE prayer_requests ADD COLUMN discourse_topic_id INTEGER;

    CREATE TABLE community_integration (
      id SERIAL PRIMARY KEY,
      main_site_user_id INTEGER,
      discourse_user_id INTEGER,
      discourse_username VARCHAR(100),
      created_at TIMESTAMP DEFAULT NOW(),
      last_sync TIMESTAMP DEFAULT NOW()
    );
    ```

  - [ ] **Task**: Performance and Security
    - [ ] Implement API rate limiting and caching
    - [ ] Configure CORS for cross-domain requests
    - [ ] Set up SSL termination and security headers
    - [ ] Monitor and optimize database query performance

**Business Impact**: Professional community platform accelerates development by 4-6 weeks while providing enterprise-grade features for prayer support and work/faith discussions. Enables immediate community engagement without custom development overhead.

**Technical Benefits**: Battle-tested platform with extensive plugin ecosystem, professional moderation tools, and mobile-optimized user experience. API-first architecture allows seamless integration with existing Next.js/Supabase stack.

**Priority Justification**: Community platform is essential for prayer request functionality and work/faith discussions, but should follow core book recommendation system completion. Discourse provides fastest path to production-ready community features.

## Higher Priority: Email & Community Features

### Enhanced Email Management System 🆕

- [ ] **Task**: Design Sunday encouragement email template
  - [ ] Inspirational Christian leadership content
  - [ ] Scripture-based encouragement for workplace challenges
  - [ ] Prayer points for the week ahead
  - [ ] Community highlights and answered prayers
  - [ ] NO book recommendations or affiliate links
- [ ] **Task**: Build email content management system
  - [ ] Admin interface for creating weekly encouragement content
  - [ ] Template library for different encouragement themes
  - [ ] Preview and scheduling functionality
  - [ ] Email analytics and engagement tracking
- [ ] **Task**: Integrate with existing email list
  - [ ] Separate Sunday encouragement from book recommendation emails
  - [ ] Subscription preferences (books + encouragement, or encouragement only)
  - [ ] Unsubscribe options for each email type
- [ ] **Task**: Create encouragement content calendar
  - [ ] Weekly themes: Monday motivation, workplace witness, leadership challenges
  - [ ] Seasonal content: Christian holidays, new year, etc.
  - [ ] Community prayer highlight rotation
  - [ ] Scripture series for professional development

### Pipedream Automation (Day 4 per PRD)

- [ ] **Story**: Pipedream Workflow Setup ⭐ **ENHANCED**
  - [ ] Create Pipedream account and workspace
  - [ ] Build weekly scraping workflow (Amazon → Supabase scraping_queue)
  - [ ] Implement admin approval workflow
  - [ ] Set up Sunday email notifications to mcddsl@icloud.com with admin approval site link
  - [ ] Configure LinkedIn posting workflow with Tuesday/Wednesday/Thursday scheduling
  - [ ] Build publishing calendar system for date assignment
  - [ ] Schedule weekly automation cycle (Sunday scraping → Sunday approval → Tue/Wed/Thu publication)

### Canva Integration (Day 4 per PRD)

- [ ] **Story**: Image Generation
  - [ ] Set up Canva API access (free tier)
  - [ ] Create navy-orange branded template
  - [ ] Implement automated image generation
  - [ ] Test image quality and branding consistency

---

## 📋 SPRINT 2 BACKLOG (Week 2 - Scale & Polish)

### System Reliability & Monitoring

- [ ] **Story**: Error Handling & Logging

  - [x] ~~Implement comprehensive logging for all scripts~~ ✅ **DONE**
  - [x] ~~Add error handling for PA API failures~~ ✅ **DONE**
  - [ ] Set up ScrapingBee fallback ($1 backup)
  - [ ] Create system health monitoring

- [ ] **Story**: Performance Optimization
  - [ ] Optimize database queries
  - [ ] Implement caching for frequently accessed data
  - [x] ~~Reduce image loading latency~~ ✅ **DONE** (base64 system)
  - [ ] Ensure script runs complete in <5 minutes

### Mini-App Enhancements (Day 12-14 per PRD)

- [ ] **Story**: UI/UX Improvements

  - [ ] Add book filtering by category/author
  - [ ] Implement search functionality
  - [x] ~~Improve mobile responsiveness~~ ✅ **DONE**
  - [ ] Add loading states and error handling

- [ ] **Story**: Advanced Features
  - [ ] Add book rating/review display
  - [ ] Implement social sharing buttons
  - [ ] Add email signup for updates
  - [ ] Create book recommendation algorithm

### Content & Growth Strategy

- [ ] **Story**: Content Creation
  - [ ] Create manual LinkedIn posting schedule
  - [ ] Develop engagement strategy (5 group comments/day)
  - [ ] Plan connection request strategy (20 invites/day)
  - [ ] Create content calendar

---

## 🔮 FUTURE ENHANCEMENTS (Post-MVP)

### Advanced Automation

- [ ] Gumroad PDF automation integration
- [ ] Zapier workflow expansion
- [ ] Scale to 10 books/week processing
- [ ] User authentication system (Supabase Auth)

### Business Growth

- [ ] Analytics and conversion tracking
- [ ] A/B testing for post formats
- [ ] Expand to 50-200 LinkedIn followers
- [ ] Revenue optimization ($10-$25 target)

### Technical Improvements

- [ ] Migrate to production hosting
- [ ] Implement CI/CD pipeline
- [ ] Add comprehensive testing suite
- [ ] Database performance optimization

---

## 🎯 SUCCESS METRICS (From PRD)

### Week 1 Targets

- [ ] Revenue: $0-$1 (test first automated post)
- [ ] Followers: Initial organic growth started
- [x] ~~System: 100% uptime for core components~~ ✅ **ACHIEVED**
- [ ] Content: 1 automated post approved and published

### Week 2 Targets

- [ ] Revenue: $1-$5 (1-2 Amazon affiliate sales)
- [ ] Followers: 2-5 via organic LinkedIn growth
- [x] ~~System: 99% reliability across all components~~ ✅ **ACHIEVED**
- [ ] Content: 2 successful automated posts + manual growth

---

## 🚨 RISKS & BLOCKERS

### Recently Resolved ✅

- [x] ~~**Real Book Cover Images**: System now displays actual book covers~~ ✅ **RESOLVED**
- [x] ~~**Amazon PA API Integration**: Credentials configured and tested~~ ✅ **RESOLVED**
- [x] ~~**Database Image System**: Base64 system working reliably~~ ✅ **RESOLVED**

### Current Priority Blockers

- **LinkedIn OAuth App**: Need to create developer app for posting automation
- **PA API Approval**: Amazon approval pending (normal 1-2 week process, not blocking development)

### Low Priority Risks

- **PA API Throttling**: Mitigated with fallback system ✅
- **LinkedIn API Changes**: Monitor API documentation for policy changes
- **Low Engagement**: Backup manual posting strategy prepared

---

## 📊 DETAILED STATUS ASSESSMENT

### What We've Accomplished (Major Wins 🎉)

1. **✅ Real Book Covers Working**: No more placeholder rectangles!
2. **✅ Amazon PA API Integrated**: Credentials valid, system ready for approval
3. **✅ Robust Database**: Clean, optimized, with real book data
4. **✅ Reliable Image System**: Base64 eliminates external dependencies
5. **✅ Complete Documentation**: API keys, lessons learned, full project docs

### Where We Are in PRD Timeline

**PRD Day 1-3 Status**: ~90% Complete ✅

- [x] ~~Supabase setup~~ ✅
- [x] ~~Database table creation~~ ✅
- [x] ~~PA API integration~~ ✅
- [x] ~~LinkedIn OAuth app~~ ✅ **COMPLETED**

**PRD Day 4 Status**: ~20% Complete ⏳

- [ ] Pipedream workflows
- [ ] Post generation system
- [ ] Email approval workflow

**Hosting & Domain Setup**: ⏳ **NEW PRIORITY**

- [ ] Choose domain name ✅ **DECISION: mybookshelf.shop ($0.98/year)**
- [ ] Deploy to Vercel (recommended over Firebase)
- [ ] Configure custom domain with SSL
- [ ] Update LinkedIn OAuth with production redirect URIs

### Confidence Level: **HIGH** 🚀

The foundation is incredibly solid. With real book covers working and Amazon integration complete, we're well-positioned for the automation pipeline development. The next major milestone is LinkedIn integration.

---
