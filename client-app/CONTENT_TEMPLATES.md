# Content Templates Documentation

Generated: 2025-12-15T21:05:30.663Z

This document provides templates and field descriptions for populating content.

## Education Module

### Video Tutorial Template

**Type**: `videos`

**Fields**:

- **title** (string, required)
- **description** (text, required)
- **video_url** (url, required)
- **thumbnail_url** (url, optional)
- **category** (enum, required) - Options: beginner, intermediate, advanced, strategy, forex, crypto, analysis
- **duration** (number, required) - Duration in seconds
- **language** (string, optional)
- **tags** (array, optional)
- **is_featured** (boolean, optional)

**Example JSON**:
```json
{
  "title": "Introduction to Forex Trading",
  "description": "Learn the basics of forex trading",
  "video_url": "https://example.com/videos/intro-forex.mp4",
  "thumbnail_url": "https://example.com/thumbnails/intro-forex.jpg",
  "category": "beginner",
  "duration": 1200,
  "language": "en",
  "tags": [
    "forex",
    "beginner",
    "introduction"
  ],
  "is_featured": true
}
```

### Ebook Template

**Type**: `ebooks`

**Fields**:

- **title** (string, required)
- **description** (text, required)
- **file_url** (url, required)
- **cover_url** (url, optional)
- **category** (enum, required) - Options: strategy, analysis, psychology, risk-management
- **language** (string, optional)
- **tags** (array, optional)

**Example JSON**:
```json
{
  "title": "Complete Trading Strategy Guide",
  "description": "Comprehensive guide to trading strategies",
  "file_url": "https://example.com/ebooks/strategy-guide.pdf",
  "cover_url": "https://example.com/covers/strategy-guide.jpg",
  "category": "strategy",
  "language": "en",
  "tags": [
    "strategy",
    "guide",
    "trading"
  ]
}
```

### Economic Calendar Event Template

**Type**: `calendar`

**Fields**:

- **event_name** (string, required)
- **country** (string, required) - ISO country code
- **currency** (string, required) - ISO currency code
- **impact** (enum, required) - Options: low, medium, high
- **event_date** (datetime, required)
- **category** (enum, required) - Options: employment, inflation, gdp, central-bank, trade
- **description** (text, optional)
- **previous_value** (string, optional)
- **forecast_value** (string, optional)

**Example JSON**:
```json
{
  "event_name": "US Non-Farm Payrolls",
  "country": "US",
  "currency": "USD",
  "impact": "high",
  "event_date": "2025-01-10T08:30:00Z",
  "category": "employment",
  "description": "Monthly employment data",
  "previous_value": "150K",
  "forecast_value": "180K"
}
```

### Market Report Template

**Type**: `reports`

**Fields**:

- **title** (string, required)
- **summary** (text, required)
- **content** (text, required)
- **report_date** (date, required)
- **period_start** (date, optional)
- **period_end** (date, optional)
- **category** (enum, required) - Options: daily, weekly, monthly, forex, crypto, commodities
- **is_featured** (boolean, optional)
- **thumbnail_url** (url, optional)

**Example JSON**:
```json
{
  "title": "Weekly Market Analysis - Week 1, 2025",
  "summary": "Market overview for the first week of 2025",
  "content": "Full report content...",
  "report_date": "2025-01-07",
  "period_start": "2025-01-01",
  "period_end": "2025-01-07",
  "category": "weekly",
  "is_featured": true,
  "thumbnail_url": "https://example.com/reports/weekly-1.jpg"
}
```

## Support Module

### Help Article Template

**Type**: `articles`

**Fields**:

- **title** (string, required)
- **content** (html, required)
- **category_id** (number, required) - Category ID from support categories
- **tags** (array, optional)
- **is_featured** (boolean, optional)
- **is_pinned** (boolean, optional)
- **language** (string, optional)

**Example JSON**:
```json
{
  "title": "How to Deposit Funds",
  "content": "<h2>Depositing Funds</h2><p>To deposit funds...</p>",
  "category_id": 1,
  "tags": [
    "deposit",
    "funding",
    "account"
  ],
  "is_featured": true,
  "is_pinned": false,
  "language": "en"
}
```

### FAQ Item Template

**Type**: `faq`

**Fields**:

- **question** (string, required)
- **answer** (text, required)
- **category** (enum, required) - Options: general, trading, account, technical, legal
- **is_featured** (boolean, optional)
- **language** (string, optional)

**Example JSON**:
```json
{
  "question": "How do I reset my password?",
  "answer": "To reset your password, click on 'Forgot Password'...",
  "category": "account",
  "is_featured": true,
  "language": "en"
}
```

## Legal Module

### Terms of Service Template

**Type**: `terms`

**Fields**:

- **version** (string, required)
- **content** (html, required)
- **effective_date** (date, required)
- **language** (string, optional)

**Example JSON**:
```json
{
  "version": "1.0",
  "content": "<h1>Terms of Service</h1><p>...</p>",
  "effective_date": "2025-01-01",
  "language": "en"
}
```

### Privacy Policy Template

**Type**: `privacy`

**Fields**:

- **version** (string, required)
- **content** (html, required)
- **effective_date** (date, required)
- **language** (string, optional)

**Example JSON**:
```json
{
  "version": "1.0",
  "content": "<h1>Privacy Policy</h1><p>...</p>",
  "effective_date": "2025-01-01",
  "language": "en"
}
```

### Risk Warning Template

**Type**: `risk_warning`

**Fields**:

- **content** (html, required)
- **language** (string, optional)

**Example JSON**:
```json
{
  "content": "<h1>Risk Warning</h1><p>...</p>",
  "language": "en"
}
```

