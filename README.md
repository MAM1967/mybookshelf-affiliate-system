# MyBookshelf Affiliate System

A comprehensive affiliate marketing system for Christian leadership books and accessories, built with modern web technologies.

## 🏗️ Architecture Overview

### **Technology Stack**
- **Frontend**: HTML/CSS/JavaScript (responsive design)
- **Backend**: Node.js API endpoints with Supabase PostgreSQL
- **Hosting**: Vercel with automatic deployments
- **Database**: Supabase with real-time capabilities
- **Email**: Resend API for notifications
- **Social**: LinkedIn API integration
- **Testing**: Jest framework

### **Core Components**
- **Price Updater**: Single consolidated endpoint for Amazon price tracking
- **Admin Dashboard**: Visual interface for content approval
- **LinkedIn Automation**: Scheduled posting system
- **Email Notifications**: Automated reporting system

## 🚀 Quick Start

### **Prerequisites**
- Node.js 22.x
- Vercel CLI (optional)
- Supabase account
- Amazon Associates account

### **Installation**

1. **Clone the repository**
   ```bash
   git clone https://github.com/MAM1967/mybookshelf-affiliate-system.git
   cd mybookshelf-affiliate-system
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp env.example .env.local
   # Edit .env.local with your credentials
   ```

4. **Configure Vercel environment variables**
   ```bash
   vercel env add SUPABASE_URL
   vercel env add SUPABASE_ANON_KEY
   vercel env add AMAZON_ACCESS_KEY
   vercel env add AMAZON_SECRET_KEY
   vercel env add RESEND_API_KEY
   ```

5. **Deploy to Vercel**
   ```bash
   vercel --prod
   ```

## 📁 Project Structure

```
mybookshelf-affiliate-system/
├── api/                          # Vercel API endpoints
│   ├── price-updater.js          # Single price update endpoint
│   ├── price-approvals.js        # Price approval system
│   └── linkedin-callback.js      # LinkedIn OAuth
├── frontend/mini-app/            # Frontend application
│   ├── admin.html                # Admin dashboard
│   ├── index.html                # Main landing page
│   └── components/               # Frontend components
├── backend/scripts/              # Backend automation scripts
│   ├── database/                 # Database operations
│   ├── linkedin/                 # LinkedIn automation
│   ├── price-updates/            # Price update scripts
│   └── tests/                    # Test files
├── tests/                        # Test suite
│   └── price-updater.test.js     # Price updater tests
├── docs/                         # Documentation
└── .github/workflows/            # CI/CD automation
```

## 🔧 Development

### **Running Tests**
```bash
npm test                    # Run all tests
npm run test:watch         # Run tests in watch mode
npm run test:coverage      # Run tests with coverage
```

### **Local Development**
```bash
npm run dev                # Start development server
```

### **API Endpoints**

#### **Price Updates**
- `GET /api/price-updater` - Update prices for all items
- `POST /api/price-updater` - Manual price update trigger

#### **Price Approvals**
- `GET /api/price-approvals` - Get pending approvals
- `POST /api/price-approvals` - Approve/reject price changes

#### **LinkedIn Integration**
- `GET /api/linkedin-callback` - OAuth callback handler

## 🔐 Security

### **Environment Variables**
All sensitive credentials are stored in environment variables:

```bash
# Required
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
AMAZON_ACCESS_KEY=your_amazon_access_key
AMAZON_SECRET_KEY=your_amazon_secret_key

# Optional
RESEND_API_KEY=your_resend_api_key
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
```

### **Security Best Practices**
- ✅ No hardcoded credentials in code
- ✅ Environment variables for all secrets
- ✅ Input validation on all endpoints
- ✅ Rate limiting on API calls
- ✅ Error handling without exposing internals

## 📊 Monitoring

### **Health Checks**
- Database connectivity
- API endpoint availability
- Cron job execution status
- Price update success rates

### **Logging**
- Structured logging for all operations
- Error tracking and alerting
- Performance monitoring
- Security event logging

## 🚨 Troubleshooting

### **Common Issues**

1. **Price updates not working**
   - Check Amazon API credentials
   - Verify Supabase connection
   - Check GitHub Actions logs

2. **LinkedIn posting issues**
   - Verify OAuth token validity
   - Check API approval status
   - Review posting permissions

3. **Database connection errors**
   - Verify Supabase URL and keys
   - Check network connectivity
   - Review database permissions

### **Debug Mode**
```bash
# Enable debug logging
DEBUG=* npm run dev
```

## 📈 Performance

### **Optimizations**
- Single consolidated price update endpoint
- Efficient database queries with proper indexing
- Rate limiting to prevent API abuse
- Caching for frequently accessed data

### **Metrics**
- Response time: < 5 seconds
- Success rate: > 95%
- Uptime: > 99.9%

## 🤝 Contributing

### **Code Standards**
- ESLint for JavaScript linting
- Prettier for code formatting
- Jest for testing
- Conventional commits for version control

### **Development Workflow**
1. Create feature branch
2. Write tests for new functionality
3. Implement changes
4. Run test suite
5. Submit pull request

## 📄 License

This project is proprietary software. All rights reserved.

## 🆘 Support

For technical support or questions:
- Email: admin@mybookshelf.shop
- GitHub Issues: [Create an issue](https://github.com/MAM1967/mybookshelf-affiliate-system/issues)

---

**Last Updated**: August 5, 2025  
**Version**: 1.0.0  
**Status**: Production Ready ✅
