# MyBookshelf Affiliate System

## 📚 Overview

Automates Amazon affiliate revenue by fetching book and accessory recommendations, storing data in Supabase, and posting updates to LinkedIn. Includes a beautiful mini-app for browsing recommendations with Christian values integration.

## ✨ Features

- **Weekly Recommendations**: 3 leadership/productivity/AI books + 1 accessory per week
- **Christian Content Filtering**: Prioritizes Christian authors like Patrick Lencioni
- **Beautiful Mini-App**: Modern, responsive web interface for browsing recommendations
- **Supabase Integration**: Robust database storage and API connectivity
- **LinkedIn Automation**: Ready for post generation and approval workflows
- **Scripture Integration**: Features Proverbs 16:3 and Christian values alignment

## 🚀 Current Implementation Status

### ✅ Completed Components

- **Database Schema**: Supabase table structure for books and accessories
- **Backend Script**: Complete Python system with Supabase integration
- **Mini-App**: Professional frontend with filtering and affiliate links
- **Configuration**: Environment variable management and validation
- **Content Filtering**: Anti-Christian content filtering system

### 🔨 Next Steps

- Amazon PA API integration (currently using mock data)
- Pipedream automation workflows
- LinkedIn OAuth integration
- Email approval system

## 🛠️ Quick Setup

### 1. Install Dependencies

```bash
cd backend/
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
# Supabase Configuration (REQUIRED)
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key

# Amazon Associate Configuration (Optional for testing)
AMAZON_ACCESS_KEY=your_amazon_access_key
AMAZON_SECRET_KEY=your_amazon_secret_key
AMAZON_ASSOCIATE_ID=your_amazon_associate_tag

# Email for post approval
POST_APPROVAL_EMAIL=your_email@example.com
```

### 3. Test Your Setup

```bash
cd backend/
python test_connection.py
```

### 4. Configure Mini-App

Edit `frontend/mini-app/index.html` and update the Supabase credentials:

```javascript
const SUPABASE_URL = "your_supabase_project_url";
const SUPABASE_ANON_KEY = "your_supabase_anon_key";
```

### 5. Run the System

```bash
# Test with mock data
cd backend/
python fetch_books.py

# Open mini-app in browser
open frontend/mini-app/index.html
```

## 📖 Usage

### Backend Script

```python
from fetch_books import MyBookshelfSystem

system = MyBookshelfSystem()
result = system.run_weekly_update()
print(result)
```

### Mini-App Features

- **Category Filtering**: Filter by Books or Accessories
- **Responsive Design**: Works on desktop and mobile
- **Live Data**: Connects to your Supabase database
- **Mock Data Fallback**: Shows sample data when not configured

## 🏗️ Project Structure

```
mybookshelf-affiliate-system/
├── backend/
│   ├── scripts/
│   │   └── fetch_books.py       # Main system logic
│   ├── supabase/
│   │   └── schema.sql           # Database schema
│   ├── config.py                # Configuration management
│   ├── test_connection.py       # Test script
│   └── requirements.txt         # Python dependencies
├── frontend/
│   └── mini-app/
│       └── index.html           # Beautiful web interface
├── automation/
│   └── pipedream/
│       └── workflows.md         # Automation workflows
└── README.md
```

## 🔧 Technical Architecture

### Backend Components

- **MyBookshelfSystem**: Main class handling all operations
- **Supabase Integration**: Database storage and retrieval
- **Content Filtering**: Christian values-based content filtering
- **Mock Data System**: Development and testing support

### Frontend Components

- **Responsive Design**: Modern CSS Grid and Flexbox
- **Supabase JS Client**: Direct database connectivity
- **Category Filtering**: Dynamic content filtering
- **Professional UI**: Christian-themed professional design

## 🎯 Success Metrics (Per PRD)

- **Revenue Target**: $1-$5 in two weeks (1-2 Amazon affiliate sales)
- **Follower Growth**: 2-5 LinkedIn followers via organic growth
- **System Uptime**: 99% reliability
- **Setup Time**: <10 hours total
- **Christian Alignment**: Proverbs 16:3 integration and content filtering

## 🔜 Next Implementation Steps

### Week 1 Remaining Tasks

1. **Amazon PA API Integration**: Replace mock data with live Amazon data
2. **Pipedream Workflows**: Set up automation for weekly runs
3. **LinkedIn OAuth**: Create LinkedIn app for posting
4. **Email Approval System**: Implement post approval workflow

### Week 2 Tasks

1. **Canva Integration**: Automated image generation
2. **Performance Optimization**: Monitor and improve system performance
3. **Enhanced Filtering**: Improve Christian content filtering
4. **Analytics**: Track affiliate performance

## 🤝 Contributing

This project aligns with Christian values and focuses on providing valuable leadership and productivity resources to professionals. All content is filtered to ensure alignment with Christian principles.

## 📄 License

Built for personal use as part of the MyBookshelf Affiliate System business plan.
