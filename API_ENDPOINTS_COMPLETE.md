# COMPLETE API ENDPOINTS DOCUMENTATION

## All Backend API Endpoints (40+)

### Authentication (3 endpoints)
- POST /auth/signup - Create account
- POST /auth/login - Login user
- GET /auth/me - Get current user

### Expenses (6 endpoints)
- GET /expenses - List all user expenses
- POST /expenses - Create expense (auto-categorizes if category omitted)
- PUT /expenses/{id} - Update expense
- DELETE /expenses/{id} - Delete expense
- POST /predict-category - Predict category from note text
- GET /categories - Get all expense categories

### Incomes (5 endpoints)
- GET /incomes - List all user incomes
- POST /incomes - Create income
- PUT /incomes/{id} - Update income
- DELETE /incomes/{id} - Delete income
- GET /income-categories - Get all income categories

### Budgets (2 endpoints)
- GET /budgets - List all user budgets
- POST /budgets - Create/update budget for category

### Analytics (3 endpoints)
- GET /analytics/summary - Dashboard summary (total spent, by category, trends)
- GET /analytics/insights - AI-generated spending insights
- GET /analytics/financial-summary - Complete financial overview (income vs expenses, net balance, savings rate)

### AI Chat (2 endpoints)
- POST /ai/chat - Send message to AI assistant, get personalized advice
- GET /ai/suggestions - Get quick suggestion prompts for chat UI

### ML Predictions (3 endpoints)
- GET /ml/predict-next-month - Predict next month spending using linear regression
- GET /ml/anomalies - Detect spending anomalies (unusual patterns, large transactions)
- GET /ml/insights - Get comprehensive ML-based insights

### CSV Import (2 endpoints)
- POST /expenses/import-csv - Import expenses from CSV file (with duplicate detection)
- POST /expenses/validate-csv - Validate CSV format and return preview

### SMS Webhook (2 endpoints)
- POST /sms/webhook - Receive SMS and auto-create expense (for SMS forwarding apps)
- POST /sms/test-parse - Test SMS parsing without creating expense

### Root (1 endpoint)
- GET / - API health check

---

## Detailed Endpoint Documentation

### DELETE /expenses/{expense_id}
Delete an expense.

**Headers:** Authorization: Bearer <token>

**Response (200):**
```json
{"message": "Expense deleted"}
```

**Errors:** 404 if not found

### POST /predict-category
Predict category from note text using ML model.

**Request:**
```json
{"note": "Bought groceries at supermarket"}
```

**Response:**
```json
{"category": "Food"}
```

### GET /categories
Get all available expense categories.

**Response:**
```json
{"categories": ["Food", "Gym", "Travel", "Shopping", "Misc"]}
```

### GET /budgets
Get all budgets for user.

**Headers:** Authorization: Bearer <token>

**Response:**
```json
[
  {"id": 1, "category": "Food", "amount": 500.00},
  {"id": 2, "category": "Shopping", "amount": 300.00}
]
```

### POST /budgets
Create or update budget for a category.

**Headers:** Authorization: Bearer <token>

**Request:**
```json
{"category": "Food", "amount": 500.00}
```

**Response:**
```json
{"id": 1, "category": "Food", "amount": 500.00}
```

### GET /analytics/summary
Get dashboard analytics summary.

**Headers:** Authorization: Bearer <token>

**Response:**
```json
{
  "total_spent": 1250.50,
  "by_category": {
    "Food": 450.00,
    "Shopping": 300.00,
    "Travel": 500.50
  },
  "budget_status": {
    "Food": {"spent": 450.00, "budget": 500.00, "percentage": 90.0}
  },
  "trends": {...}
}
```

### GET /analytics/insights
Get AI-generated spending insights.

**Headers:** Authorization: Bearer <token>

**Response:**
```json
{
  "insights": [
    "You spent 20% more on Food this month",
    "Travel expenses are within budget",
    "Consider reducing Shopping expenses"
  ]
}
```

### GET /income-categories
Get all income categories.

**Response:**
```json
{
  "categories": ["Salary", "Freelance", "Investment", "Business", "Gift", "Refund", "Cashback", "Bonus", "Other"]
}
```

### GET /analytics/financial-summary
Get complete financial overview with income and expenses.

**Headers:** Authorization: Bearer <token>

**Response:**
```json
{
  "total_income": 5000.00,
  "total_expenses": 3500.00,
  "net_balance": 1500.00,
  "savings_rate": 30.00,
  "month": "January 2024",
  "income_breakdown": {
    "Salary": 4500.00,
    "Freelance": 500.00
  }
}
```

### POST /ai/chat
Chat with AI spending assistant.

**Headers:** Authorization: Bearer <token>

**Request:**
```json
{"message": "How can I save more money?"}
```

**Response:**
```json
{
  "response": "Based on your spending patterns, here are some tips...",
  "suggestions": ["Reduce dining out", "Set stricter budgets"]
}
```

### GET /ai/suggestions
Get quick chat suggestions.

**Response:**
```json
{
  "suggestions": [
    "How can I save more?",
    "Analyze my spending",
    "Budget recommendations",
    "Where am I overspending?"
  ]
}
```

### GET /ml/predict-next-month
Predict next month's spending.

**Headers:** Authorization: Bearer <token>

**Response:**
```json
{
  "predicted_amount": 3200.50,
  "confidence": "high",
  "trend": "increasing",
  "historical_average": 3000.00
}
```

### GET /ml/anomalies
Detect spending anomalies.

**Headers:** Authorization: Bearer <token>

**Response:**
```json
{
  "anomalies": [
    {
      "type": "large_transaction",
      "amount": 1500.00,
      "category": "Shopping",
      "date": "2024-01-15",
      "note": "Laptop purchase"
    },
    {
      "type": "category_spike",
      "category": "Food",
      "usual_amount": 400.00,
      "current_amount": 650.00,
      "increase_percentage": 62.5
    }
  ]
}
```

### GET /ml/insights
Get comprehensive ML insights.

**Headers:** Authorization: Bearer <token>

**Response:**
```json
{
  "prediction": {...},
  "anomalies": [...],
  "trends": {...},
  "recommendations": [...]
}
```

### POST /expenses/import-csv
Import expenses from CSV file.

**Headers:** Authorization: Bearer <token>, Content-Type: multipart/form-data

**Request:** Form data with file field

**Response:**
```json
{
  "imported": 25,
  "duplicates": 3,
  "errors": 1,
  "category_breakdown": {
    "Food": 10,
    "Shopping": 8,
    "Travel": 7
  }
}
```

### POST /expenses/validate-csv
Validate CSV before import.

**Headers:** Authorization: Bearer <token>, Content-Type: multipart/form-data

**Request:** Form data with file field

**Response:**
```json
{
  "valid": true,
  "rows": 28,
  "preview": [
    {"date": "2024-01-15", "amount": 45.50, "note": "Lunch"},
    {"date": "2024-01-16", "amount": 120.00, "note": "Shoes"}
  ],
  "errors": []
}
```

### POST /sms/webhook
Receive SMS and auto-create expense.

**Headers:** Authorization: Bearer <token>

**Request:**
```json
{
  "sender": "HDFCBK",
  "message": "Rs 450.00 debited from A/c XX1234 on 15-Jan-24 at Swiggy",
  "timestamp": "2024-01-15T14:30:00"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Expense created from SMS",
  "expense": {
    "id": 123,
    "amount": 450.00,
    "category": "Food",
    "date": "2024-01-15",
    "note": "Swiggy - Rs 450.00",
    "merchant": "Swiggy"
  },
  "parsed_data": {
    "amount": 450.00,
    "merchant": "Swiggy",
    "date": "2024-01-15",
    "note": "Swiggy - Rs 450.00"
  }
}
```

**Duplicate Response:**
```json
{
  "status": "duplicate",
  "message": "Transaction already exists",
  "expense_id": 120
}
```

### POST /sms/test-parse
Test SMS parsing without creating expense.

**Request:**
```json
{
  "sender": "HDFCBK",
  "message": "Rs 450.00 debited from A/c XX1234 on 15-Jan-24 at Swiggy"
}
```

**Response:**
```json
{
  "valid": true,
  "message": "SMS parsed successfully",
  "parsed_data": {
    "amount": 450.00,
    "merchant": "Swiggy",
    "date": "2024-01-15",
    "note": "Swiggy - Rs 450.00",
    "suggested_category": "Food"
  }
}
```

**Invalid SMS Response:**
```json
{
  "valid": false,
  "message": "SMS does not contain a valid transaction"
}
```
