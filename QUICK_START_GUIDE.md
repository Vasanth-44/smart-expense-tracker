# 🚀 Quick Start Guide - AI Finance Platform

## Installation Steps

### 1. Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Start the server
python -m uvicorn main:app --reload
```

Backend will run on: `http://127.0.0.1:8000`

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm start
```

Frontend will run on: `http://localhost:3000`

## 🎯 First Steps

1. **Sign Up / Login**
   - Create an account or login with existing credentials

2. **Add Some Expenses**
   - Click "Add Expense" in sidebar
   - Enter a few expenses from past months
   - This data is needed for forecasting

3. **Add Income**
   - Click "Add Income"
   - Enter your monthly income sources

4. **Set Budgets**
   - Click "Budget"
   - Set monthly budgets for categories

5. **Explore New Features**
   - **Forecast**: View spending predictions
   - **Net Worth**: Add assets and liabilities
   - **Health Score**: Check your financial health
   - **Goals**: Create financial goals
   - **Insights**: View spending patterns

## 📊 Feature Overview

### Forecast Dashboard
- Predicts next month's spending
- Shows category-wise forecasts
- Displays confidence levels
- Analyzes spending trends

### Net Worth Dashboard
- Track total assets
- Monitor liabilities
- Calculate net worth
- View monthly growth

### Financial Health Score
- 0-100 score based on 5 metrics
- Color-coded rating
- Personalized recommendations
- Component breakdown

### Goals Planner
- Create financial goals
- Track progress
- Required savings calculator
- On-track status

### Insights Dashboard
- Behavioral spending analysis
- Anomaly detection
- Budget alerts
- Month-over-month comparisons

## 🎨 Navigation

**Sidebar Menu:**
- Dashboard - Overview
- Financial Summary - Income vs Expenses
- Net Worth - Assets & Liabilities
- Forecast - Predictions
- Health Score - Financial wellness
- Goals - Goal tracking
- Insights - Anomalies & patterns
- Add Expense - Quick entry
- Expenses - Transaction list
- Add Income - Income entry
- Income History - Income list
- SMS Import - Auto-import
- Budget - Budget management

## 💡 Tips

1. **For Accurate Forecasts**: Add at least 2-3 months of historical data
2. **Update Regularly**: Enter expenses daily for best insights
3. **Set Realistic Goals**: Use the required savings calculator
4. **Monitor Health Score**: Aim to improve it monthly
5. **Review Insights**: Check weekly for spending patterns

## 🔧 Troubleshooting

**Backend won't start:**
- Check if port 8000 is available
- Verify Python dependencies are installed
- Delete `expenses.db` if database errors occur

**Frontend won't start:**
- Run `npm install` again
- Clear npm cache: `npm cache clean --force`
- Check if port 3000 is available

**No data in forecasts:**
- Add more historical expenses (need at least 2 months)
- Ensure expenses have proper dates

**API connection errors:**
- Verify backend is running on port 8000
- Check browser console for CORS errors

## 📱 Mobile Access

The app is fully responsive and works on mobile browsers. For best experience:
- Use Chrome or Safari on mobile
- Enable desktop mode for full features
- Consider deploying to Vercel for public access

## 🎉 You're Ready!

Start exploring your new AI-powered Personal Finance Intelligence Platform!

For detailed documentation, see `AI_FINANCE_PLATFORM_UPGRADE.md`
