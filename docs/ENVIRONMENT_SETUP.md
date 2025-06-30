# Environment Setup Guide

# MyBookshelf Affiliate System - Multi-Environment Configuration

## Overview

This project uses a three-environment setup for safe development and deployment:

- **Development**: Local development and testing
- **Staging**: Pre-production testing with production-like data
- **Production**: Live system serving real users

## Environment Structure

```
Branches & Deployments:
├── main → Production (mybookshelf.shop)
├── staging → Staging (staging-mybookshelf.vercel.app)
└── dev → Development (dev-mybookshelf.vercel.app)

Supabase Projects:
└── Single Project (mybookshelf) - Free tier, single environment
```

## 1. Vercel Environment Setup

### Step 1: Connect Branches to Vercel

1. **Log into Vercel Dashboard**

   - Go to [vercel.com](https://vercel.com)
   - Navigate to your `mybookshelf-affiliate-system` project

2. **Configure Git Branches**

   ```
   Settings > Git > Production Branch: main
   Settings > Git > Preview Branches: staging, dev
   ```

3. **Verify Automatic Deployments**
   ```
   main branch → mybookshelf.shop (Production)
   staging branch → staging-mybookshelf.vercel.app (Preview)
   dev branch → dev-mybookshelf.vercel.app (Preview)
   ```

### Step 2: Environment Variables in Vercel

For each environment (Production, Preview - staging, Preview - dev), configure these variables:

## 2. Environment Variables Configuration

### 🔴 Production Environment Variables

Set these in **Vercel > Settings > Environment Variables > Production**:

```bash
# Environment
NODE_ENV=production
ENVIRONMENT=production

# Supabase (Production Project)
NEXT_PUBLIC_SUPABASE_URL=https://[PROD_PROJECT_ID].supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=[PROD_ANON_KEY]
SUPABASE_SERVICE_ROLE_KEY=[PROD_SERVICE_ROLE_KEY]

# Amazon PA API (Production)
AMAZON_ACCESS_KEY=[PROD_AMAZON_ACCESS_KEY]
AMAZON_SECRET_KEY=[PROD_AMAZON_SECRET_KEY]
AMAZON_ASSOCIATE_TAG=mybookshelf-20
AMAZON_REGION=us-east-1

# LinkedIn API (Production)
LINKEDIN_CLIENT_ID=78wmrhdd99ssbi
LINKEDIN_CLIENT_SECRET=[PROD_LINKEDIN_SECRET]
LINKEDIN_REDIRECT_URI=https://mybookshelf.shop/auth/linkedin/callback

# Admin Configuration
ADMIN_EMAIL=mcddsl@icloud.com
SESSION_SECRET=[PROD_SESSION_SECRET]

# Domain Configuration
BASE_URL=https://mybookshelf.shop
DOMAIN=mybookshelf.shop

# Security
CORS_ORIGIN=https://mybookshelf.shop,https://www.mybookshelf.shop
JWT_SECRET=[PROD_JWT_SECRET]
ENCRYPTION_KEY=[PROD_ENCRYPTION_KEY]

# Features (Production)
ENABLE_DEBUG_LOGGING=false
ENABLE_TEST_MODE=false
RATE_LIMIT_REQUESTS=true
ANALYTICS_ENABLED=true
```

### 🟡 Staging Environment Variables

Set these in **Vercel > Settings > Environment Variables > Preview (staging branch)**:

```bash
# Environment
NODE_ENV=production
ENVIRONMENT=staging

# Supabase (Staging Project)
NEXT_PUBLIC_SUPABASE_URL=https://[STAGING_PROJECT_ID].supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=[STAGING_ANON_KEY]
SUPABASE_SERVICE_ROLE_KEY=[STAGING_SERVICE_ROLE_KEY]

# Amazon PA API (Staging - can use production keys)
AMAZON_ACCESS_KEY=[STAGING_AMAZON_ACCESS_KEY]
AMAZON_SECRET_KEY=[STAGING_AMAZON_SECRET_KEY]
AMAZON_ASSOCIATE_TAG=mybookshelf-staging-20
AMAZON_REGION=us-east-1

# LinkedIn API (Staging)
LINKEDIN_CLIENT_ID=78wmrhdd99ssbi
LINKEDIN_CLIENT_SECRET=[STAGING_LINKEDIN_SECRET]
LINKEDIN_REDIRECT_URI=https://staging-mybookshelf.vercel.app/auth/linkedin/callback

# Admin Configuration
ADMIN_EMAIL=mcddsl@icloud.com
SESSION_SECRET=[STAGING_SESSION_SECRET]

# Domain Configuration
BASE_URL=https://staging-mybookshelf.vercel.app
DOMAIN=staging-mybookshelf.shop

# Security
CORS_ORIGIN=https://staging-mybookshelf.vercel.app
JWT_SECRET=[STAGING_JWT_SECRET]
ENCRYPTION_KEY=[STAGING_ENCRYPTION_KEY]

# Features (Staging - Production-like)
ENABLE_DEBUG_LOGGING=false
ENABLE_TEST_MODE=false
RATE_LIMIT_REQUESTS=true
ANALYTICS_ENABLED=true
```

### 🟢 Development Environment Variables

Set these in **Vercel > Settings > Environment Variables > Preview (dev branch)**:

```bash
# Environment
NODE_ENV=development
ENVIRONMENT=development

# Supabase (Development Project)
NEXT_PUBLIC_SUPABASE_URL=https://[DEV_PROJECT_ID].supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=[DEV_ANON_KEY]
SUPABASE_SERVICE_ROLE_KEY=[DEV_SERVICE_ROLE_KEY]

# Amazon PA API (Development - can use sandbox or production)
AMAZON_ACCESS_KEY=[DEV_AMAZON_ACCESS_KEY]
AMAZON_SECRET_KEY=[DEV_AMAZON_SECRET_KEY]
AMAZON_ASSOCIATE_TAG=mybookshelf-dev-20
AMAZON_REGION=us-east-1

# LinkedIn API (Development)
LINKEDIN_CLIENT_ID=78wmrhdd99ssbi
LINKEDIN_CLIENT_SECRET=[DEV_LINKEDIN_SECRET]
LINKEDIN_REDIRECT_URI=https://dev-mybookshelf.vercel.app/auth/linkedin/callback

# Admin Configuration
ADMIN_EMAIL=mcddsl@icloud.com
SESSION_SECRET=[DEV_SESSION_SECRET]

# Domain Configuration
BASE_URL=https://dev-mybookshelf.vercel.app
DOMAIN=dev-mybookshelf.shop

# Security (Development - Relaxed)
CORS_ORIGIN=http://localhost:3000,https://dev-mybookshelf.vercel.app
JWT_SECRET=[DEV_JWT_SECRET]
ENCRYPTION_KEY=[DEV_ENCRYPTION_KEY]

# Features (Development)
ENABLE_DEBUG_LOGGING=true
ENABLE_TEST_MODE=true
RATE_LIMIT_REQUESTS=false
ANALYTICS_ENABLED=false
```

## 3. Supabase Multi-Environment Setup

### Step 1: Create Separate Supabase Projects

1. **Development Project**

   ```
   Name: mybookshelf-dev
   Region: us-east-1
   Plan: Free tier
   ```

2. **Staging Project**

   ```
   Name: mybookshelf-staging
   Region: us-east-1
   Plan: Free tier (upgrade if needed)
   ```

3. **Single Project** (Current)
   ```
   Name: mybookshelf
   Region: us-east-1
   Plan: Free tier
   ```

### Step 2: Database Schema Migration

For each new project (dev, staging), run the schema setup:

```sql
-- Copy schema from backend/supabase/schema.sql
-- Plus any new tables from admin system development

-- Basic tables
CREATE TABLE books_accessories (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    price NUMERIC NOT NULL,
    affiliate_link TEXT NOT NULL,
    image_url TEXT NOT NULL,
    category TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Admin system tables (when implemented)
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
  content_score INTEGER DEFAULT 0,
  filter_flags TEXT[],
  status VARCHAR(20) DEFAULT 'pending',
  admin_notes TEXT,
  reviewed_date TIMESTAMP,
  reviewed_by VARCHAR(100) DEFAULT 'admin',
  scheduled_post_date DATE,
  post_content TEXT,
  practical_examples TEXT,
  biblical_alignment TEXT
);

CREATE TABLE admin_sessions (
  id SERIAL PRIMARY KEY,
  session_token VARCHAR(255) UNIQUE NOT NULL,
  email VARCHAR(100) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  expires_at TIMESTAMP NOT NULL,
  last_activity TIMESTAMP DEFAULT NOW()
);
```

### Step 3: Seed Data for Development/Staging

**Development**: Create test data with obvious test markers
**Staging**: Copy production data for realistic testing

## 4. Amazon Associate Tag Setup

### Register Additional Associate Tags

1. **Log into Amazon Associates**
2. **Create Additional Tracking IDs**:
   ```
   Production: mybookshelf-20 (existing)
   Staging: mybookshelf-staging-20
   Development: mybookshelf-dev-20
   ```

## 5. LinkedIn OAuth Configuration

### Update Redirect URIs

In LinkedIn Developer Console for App ID `78wmrhdd99ssbi`:

```
Redirect URLs:
- https://mybookshelf.shop/auth/linkedin/callback (Production)
- https://staging-mybookshelf.vercel.app/auth/linkedin/callback (Staging)
- https://dev-mybookshelf.vercel.app/auth/linkedin/callback (Development)
- http://localhost:3000/auth/linkedin/callback (Local Development)
```

## 6. Deployment Workflow

### Branch-Based Deployment

```bash
# Development workflow
git checkout dev
# Make changes, test locally
git push origin dev  # Triggers dev-mybookshelf.vercel.app deployment

# Staging workflow
git checkout staging
git merge dev  # Merge tested dev changes
git push origin staging  # Triggers staging-mybookshelf.vercel.app deployment

# Production workflow
git checkout main
git merge staging  # Merge tested staging changes
git push origin main  # Triggers mybookshelf.shop deployment
```

### Environment Testing Checklist

**Before promoting dev → staging:**

- [ ] All features work in dev environment
- [ ] No console errors or warnings
- [ ] Database operations work correctly
- [ ] API integrations tested

**Before promoting staging → production:**

- [ ] Staging environment matches production configuration
- [ ] Load testing completed (if applicable)
- [ ] Admin approval workflow tested
- [ ] Backup procedures verified
- [ ] Monitoring/alerting configured

## 7. Local Development Setup

### Environment File for Local Development

Create `.env.local` (not tracked in git):

```bash
# Local Development Environment
NODE_ENV=development
ENVIRONMENT=local

# Use development Supabase project
NEXT_PUBLIC_SUPABASE_URL=https://[DEV_PROJECT_ID].supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=[DEV_ANON_KEY]
SUPABASE_SERVICE_ROLE_KEY=[DEV_SERVICE_ROLE_KEY]

# Local development settings
BASE_URL=http://localhost:3000
LINKEDIN_REDIRECT_URI=http://localhost:3000/auth/linkedin/callback

# Enable debugging
ENABLE_DEBUG_LOGGING=true
ENABLE_TEST_MODE=true
RATE_LIMIT_REQUESTS=false
```

## 8. Security Considerations

### Secret Management

- **Never commit secrets to git**
- **Use different secrets for each environment**
- **Rotate secrets regularly (quarterly)**
- **Use strong, randomly generated secrets**

### Access Control

- **Limit Supabase access to necessary team members**
- **Use service role keys only in backend/server contexts**
- **Monitor API usage and access logs**

### Environment Isolation

- **No production data in development/staging**
- **Separate API keys and credentials per environment**
- **Test data clearly marked as test data**

## 9. Monitoring & Maintenance

### Health Checks

- **Verify each environment after deployment**
- **Monitor API quotas and limits**
- **Regular database backup verification**
- **SSL certificate monitoring**

### Maintenance Schedule

- **Weekly**: Review environment health and performance
- **Monthly**: Update dependencies and security patches
- **Quarterly**: Rotate secrets and review access permissions
- **Annually**: Review architecture and optimization opportunities

## 10. Troubleshooting

### Common Issues

**Environment variables not updating:**

- Check Vercel dashboard for correct environment assignment
- Redeploy the affected branch to pick up new variables
- Verify variable names match exactly (case-sensitive)

**Database connection issues:**

- Verify Supabase project URLs and keys
- Check network connectivity and firewall settings
- Review Supabase dashboard for connection limits

**LinkedIn OAuth failures:**

- Ensure redirect URIs match exactly (including protocol)
- Verify client secret is correct for environment
- Check LinkedIn app permissions and status

**Amazon PA API errors:**

- Verify associate tags are registered and approved
- Check API key permissions and quotas
- Ensure region settings match your account region

This multi-environment setup provides safe development practices, proper testing workflows, and production reliability for the MyBookshelf affiliate system.
