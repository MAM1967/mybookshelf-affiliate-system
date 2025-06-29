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

- **Amazon Data Fetching**:
  - Use Amazon Product Advertising API (PA API) to fetch 3 books (leadership/productivity/AI, prioritize Christian authors like Lencioni) + 1 accessory (e.g., journals, pens) weekly.
  - Embed Amazon Associate ID in affiliate links.
  - Filter out anti-Christian content (keyword check: e.g., exclude "atheism").
  - Fallback: ScrapingBee ($1/1,000 requests) if PA API limits hit.
- **Supabase Backend**:
  - Store data in Postgres table: title, author, price, affiliate link, image URL, category, timestamp.
  - Provide API endpoint for mini-app and Pipedream.
  - Free tier (500MB, 10,000 requests/month).
- **Python Script**:
  - Run weekly (Sunday, 8 AM) via Pipedream.
  - Query PA API, store in Supabase using Python SDK.
  - Developed with Cursor/Zed (AI-assisted coding).
- **LinkedIn Automation**:
  - Generate 200-word post (e.g., "This week's top 3 leadership books + accessory [affiliate links]") with Canva image (navy-orange, free tier).
  - Use Pipedream to email post for approval (yes/no), then post to MyBookshelf via LinkedIn OAuth app.
- **Mini-App**:
  - Supabase-hosted webpage (Next.js or HTML) to browse recommendations (title, author, link).
  - Accessible via LinkedIn bio/post links.
- **Organic Growth**:
  - Manual daily posts (100-200 words), 5 Group comments/day, 20 invites/day to gain 2-5 followers.

### 2.2 Non-Functional Requirements

- **Cost**: $0-$5/month (Supabase free, Pipedream free, Canva free, ScrapingBee $1 if needed).
- **Performance**: Script runs in <5 minutes; API latency <2 seconds.
- **Scalability**: Handle 1,000 items in Supabase; scale to 10 books/week.
- **Security**: Secure PA API keys, Supabase keys, and LinkedIn OAuth tokens (environment variables).
- **Usability**: Post approval via email (1-click yes/no).

## 3. Technical Architecture

- **Frontend**: Mini-app (Supabase API, Next.js/HTML, hosted on Supabase edge functions).
- **Backend**: Supabase Postgres (table: `books_accessories`), Python SDK for CRUD.
- **Script**: Python (PA API/ScrapingBee), hosted on Pipedream.
- **Automation**: Pipedream workflow (data fetch → post generation → approval → LinkedIn).
- **APIs**: Amazon PA API, Canva API, LinkedIn API, Supabase API.

## 4. Implementation Plan

### Week 1: Setup and Initial Automation

- **Day 1**: Set up Supabase (free), create `books_accessories` table (columns: id, title, author, price, affiliate_link, image_url, category, timestamp). Create LinkedIn OAuth app.
- **Day 2-3**: Write Python script with Cursor/Zed to query PA API (3 books + 1 accessory, filter for Lencioni/Christian), store in Supabase. Test with 1 item.
- **Day 4**: Set up Pipedream: Fetch Supabase data, generate 200-word post, create Canva image, email for approval.
- **Day 5**: Deploy mini-app (Supabase API endpoint, basic HTML). Add link to LinkedIn bio.
- **Day 6-7**: Manual LinkedIn post (100 words), 5 Group comments, 10 invites/day. Test first automated post (0-1 sale, $0-$1).

### Week 2: Refine and Scale

- **Day 8-9**: Check Supabase/Pipedream logs. Fix script if PA API fails (use ScrapingBee). Gain 2-5 followers via 5 Group comments, 10 invites/day.
- **Day 10-11**: Run second automated post (1-2 sales, $1-$4).
- **Day 12-14**: Enhance mini-app UI (add filters). Post manually for growth. Total: $1-$5, 2-5 followers.

## 5. Risks and Mitigations

- **Risk**: PA API throttling (1-2 requests/day).
  - **Mitigation**: Limit to 4 items/week; use ScrapingBee ($1).
- **Risk**: Low follower growth (2-5).
  - **Mitigation**: Increase Group comments to 10/day, invites to 20/day.
- **Risk**: Low revenue ($1-$5).
  - **Mitigation**: Add manual Gumroad $5 PDF (2-5 sales = $10-$25).
- **Risk**: Anti-Christian content.
  - **Mitigation**: Script filters keywords; prioritize Lencioni.

## 6. Success Metrics

- **Revenue**: $1-$5 (1-2 Amazon sales).
- **Followers**: 2-5 via organic growth.
- **Automation**: 100% uptime for script, Pipedream, Supabase.
- **Christian Alignment**: Include 1-2 Christian books (e.g., Lencioni); cite Proverbs 16:3 in posts.

## 7. Future Enhancements

- Add Gumroad automation (Zapier, $14/month).
- Scale to 10 books/week, 50-200 followers.
- Enhance mini-app with user login (Supabase auth).
