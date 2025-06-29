# Deployment Guide: MyBookshelf Affiliate System

## Recommended Hosting: Vercel

### Why Vercel?

- ✅ Free tier includes custom domains
- ✅ Instant GitHub deployment
- ✅ Global CDN for fast loading
- ✅ Perfect for static HTML/CSS/JS sites
- ✅ Easy OAuth callback handling
- ✅ SSL certificates included
- ✅ $0 cost for current needs

### Alternative: Firebase Hosting

- ✅ Google-owned, reliable
- ❌ Custom domains require paid plan
- ❌ More complex setup for static sites

## Domain Name Recommendations

### Suggested Domains (~$12/year)

1. `mybookshelf-app.com` - Clear, professional
2. `leadershiplibrary.app` - Focused on niche
3. `christianbookshelf.com` - Explicit Christian focus
4. `wisdomshelf.com` - Broader appeal
5. `proverbs16bookshelf.com` - Scripture reference

### Where to Register

- **Namecheap** - User-friendly, good support
- **Google Domains** - Simple integration
- **Cloudflare** - Cheapest, great performance

## Vercel Deployment Steps

### 1. Prepare Repository

```bash
# Ensure your mini-app is in the root or specify build directory
git add .
git commit -m "Prepare for Vercel deployment"
git push origin main
```

### 2. Deploy to Vercel

1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub
3. Click "Import Project"
4. Select your `mybookshelf-affiliate-system` repo
5. Configure build settings:
   - **Build Command**: Leave empty (static site)
   - **Output Directory**: `frontend/mini-app`
   - **Install Command**: Leave empty

### 3. Configure Custom Domain

1. Buy domain from Namecheap/Google Domains
2. In Vercel dashboard → Settings → Domains
3. Add your domain (e.g., `mybookshelf-app.com`)
4. Update DNS records as instructed by Vercel
5. SSL certificate auto-generated

### 4. Update LinkedIn OAuth

After domain is live, update LinkedIn app:

1. Go to LinkedIn Developer Portal
2. Add production redirect URI:
   - `https://yourdomain.com/auth/linkedin/callback`
3. Keep localhost for development

### 5. Environment Variables

In Vercel dashboard → Settings → Environment Variables:

```
SUPABASE_URL=https://ackcgrnizuhauccnbiml.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
LINKEDIN_CLIENT_ID=78wmrhdd99ssbi
LINKEDIN_CLIENT_SECRET=WPL_AP1.hCyy0nkGz9y5i1tP.ExgKnQ==
```

## Post-Deployment Configuration

### Update Frontend for Production

```javascript
// In frontend/mini-app/index.html
const SUPABASE_URL =
  process.env.SUPABASE_URL || "https://ackcgrnizuhauccnbiml.supabase.co";
const SUPABASE_ANON_KEY = process.env.SUPABASE_ANON_KEY || "eyJ...";
```

### LinkedIn OAuth Callback Handler

Create `frontend/mini-app/auth/linkedin/callback.html`:

```html
<!DOCTYPE html>
<html>
  <head>
    <title>LinkedIn Authentication</title>
  </head>
  <body>
    <script>
      // Extract code from URL and handle OAuth
      const urlParams = new URLSearchParams(window.location.search);
      const code = urlParams.get("code");
      const state = urlParams.get("state");

      if (code) {
        // Success - redirect to main app
        window.location.href = "/";
      } else {
        // Error handling
        document.body.innerHTML = "<h1>Authentication failed</h1>";
      }
    </script>
  </body>
</html>
```

## Cost Breakdown

### Monthly Costs

- **Vercel**: $0 (free tier sufficient)
- **Domain**: $1/month ($12/year)
- **Supabase**: $0 (free tier)
- **Total**: ~$1/month

### Upgrade Path

When you exceed free tiers:

- **Vercel Pro**: $20/month (much later)
- **Supabase Pro**: $25/month (much later)

## Performance Optimizations

### Vercel Automatic Optimizations

- Global CDN (280+ locations)
- Image optimization
- Static asset caching
- Gzip compression

### Manual Optimizations

- Minimize CSS/JS files
- Optimize images before upload
- Use Supabase edge functions for dynamic content

## Security Considerations

### Automatic Security Features

- SSL/TLS certificates
- DDoS protection
- Edge security rules

### Manual Security Setup

- Environment variables for secrets
- CORS configuration in Supabase
- Content Security Policy headers

## Monitoring & Analytics

### Built-in Vercel Analytics

- Page views and performance
- Geographic distribution
- Core Web Vitals

### Optional Integrations

- Google Analytics
- Mixpanel for conversion tracking
- Sentry for error tracking

## Rollback & Backup Strategy

### Automatic Backups

- Vercel maintains deployment history
- Supabase automated backups
- Git version control

### Quick Rollback

```bash
# Rollback to previous deployment
vercel --prod --confirm
```

## Next Steps After Deployment

1. ✅ Deploy to Vercel
2. ✅ Configure custom domain
3. ✅ Update LinkedIn OAuth settings
4. ✅ Test production environment
5. ✅ Set up monitoring
6. ✅ Plan Pipedream automation integration

---

**Estimated Setup Time**: 2-3 hours
**Monthly Cost**: ~$1 (domain only)
**Scalability**: Handles thousands of users on free tier
