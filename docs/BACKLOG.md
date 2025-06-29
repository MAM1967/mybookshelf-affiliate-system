# Project Backlog: MyBookshelf Affiliate System

## Project Status Overview

**Current State**: Foundation complete with clean database, duplicate prevention, and basic mini-app  
**Target**: Full automated affiliate system with LinkedIn integration per PRD  
**Timeline**: Week 1 & 2 implementation plan from PRD

---

## ✅ COMPLETED (Sprint 0 - Foundation)

### Database & Backend Infrastructure

- [x] Supabase setup with PostgreSQL database
- [x] Clean book database (4 unique records, duplicates removed)
- [x] Duplicate prevention system with MD5 hashing
- [x] Database cleanup scripts and tools
- [x] Base64 image system (placeholder images)

### Frontend & Tools

- [x] Mini-app frontend (HTML/CSS/JS) running on localhost:8000
- [x] Responsive design with Christian theme (Proverbs 16:3)
- [x] Image download and conversion script (multi-mode)
- [x] Project documentation (PRD, README, Lessons Learned)

### Development Infrastructure

- [x] Project folder structure
- [x] Scripts and automation tools
- [x] Documentation system

---

## 🎯 IN PROGRESS (Sprint 1 - Core Features)

### Image System Enhancement

- [ ] **Priority: HIGH** - Replace placeholder images with real book covers
  - [ ] Find approved book cover URLs for 4 current books
  - [ ] Use image_downloader.py to convert to base64
  - [ ] Update database with real book cover data
  - [ ] Verify images display correctly in mini-app

---

## 📋 SPRINT 1 BACKLOG (Week 1 - Core Automation)

### Amazon Integration (Day 2-3 per PRD)

- [ ] **Story**: Amazon Product Advertising API Setup

  - [ ] Register for Amazon PA API access
  - [ ] Set up Amazon Associate ID for affiliate links
  - [ ] Create PA API credentials and environment variables
  - [ ] Test PA API connectivity and rate limits

- [ ] **Story**: Book Fetching Logic
  - [ ] Implement PA API search for leadership/productivity books
  - [ ] Add Patrick Lencioni author prioritization
  - [ ] Implement Christian content filtering (exclude anti-Christian keywords)
  - [ ] Add accessory search functionality (journals, pens)
  - [ ] Create weekly batch fetching (3 books + 1 accessory)

### LinkedIn Integration (Day 1, 4 per PRD)

- [ ] **Story**: LinkedIn OAuth App Setup

  - [ ] Create LinkedIn Developer App
  - [ ] Configure OAuth credentials
  - [ ] Set up LinkedIn API permissions for posting
  - [ ] Test authentication flow

- [ ] **Story**: LinkedIn Posting Automation
  - [ ] Create post generation template (200 words)
  - [ ] Implement affiliate link embedding
  - [ ] Add Proverbs 16:3 scripture integration
  - [ ] Create approval email workflow

### Pipedream Automation (Day 4 per PRD)

- [ ] **Story**: Pipedream Workflow Setup
  - [ ] Create Pipedream account and workspace
  - [ ] Build data fetch workflow (Supabase → Pipedream)
  - [ ] Implement post generation workflow
  - [ ] Set up email approval system
  - [ ] Configure LinkedIn posting workflow
  - [ ] Schedule weekly automation (Sunday 8 AM)

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

  - [ ] Implement comprehensive logging for all scripts
  - [ ] Add error handling for PA API failures
  - [ ] Set up ScrapingBee fallback ($1 backup)
  - [ ] Create system health monitoring

- [ ] **Story**: Performance Optimization
  - [ ] Optimize database queries
  - [ ] Implement caching for frequently accessed data
  - [ ] Reduce API latency to <2 seconds
  - [ ] Ensure script runs complete in <5 minutes

### Mini-App Enhancements (Day 12-14 per PRD)

- [ ] **Story**: UI/UX Improvements

  - [ ] Add book filtering by category/author
  - [ ] Implement search functionality
  - [ ] Improve mobile responsiveness
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
- [ ] System: 100% uptime for core components
- [ ] Content: 1 automated post approved and published

### Week 2 Targets

- [ ] Revenue: $1-$5 (1-2 Amazon affiliate sales)
- [ ] Followers: 2-5 via organic LinkedIn growth
- [ ] System: 99% reliability across all components
- [ ] Content: 2 successful automated posts + manual growth

---

## 🚨 RISKS & BLOCKERS

### High Priority Risks

- **PA API Throttling**: Limit to 4 items/week, ScrapingBee fallback ready
- **LinkedIn API Changes**: Monitor API documentation for policy changes
- **Low Engagement**: Backup manual posting strategy prepared

### Current Blockers

- Need Amazon PA API approval (can take 1-2 weeks)
- LinkedIn OAuth app approval process
- Real book cover image collection pending user approval

---

## 📊 DEFINITION OF DONE

### Story Completion Criteria

- [ ] Feature implemented and tested
- [ ] Documentation updated
- [ ] Error handling implemented
- [ ] Integration tests passing
- [ ] User acceptance criteria met
- [ ] Performance requirements satisfied

### Sprint Completion Criteria

- [ ] All high-priority stories completed
- [ ] System integration tested end-to-end
- [ ] Metrics collection implemented
- [ ] Deployment to production environment
- [ ] User acceptance testing passed
