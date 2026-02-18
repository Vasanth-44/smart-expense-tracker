# 💰 Smart Expense Tracker - AI-Powered Personal Finance Intelligence Platform

A next-generation full-stack financial management application with AI-powered insights, predictive analytics, machine learning, and comprehensive wealth tracking.

## 🌟 Core Features

### Financial Management
- **Expense Management**: Add, edit, delete, and categorize expenses
- **Income Tracking**: Track multiple income sources with categories
- **Budget Management**: Set and monitor monthly budgets with visual indicators
- **Financial Dashboard**: Real-time overview of spending patterns and trends

### 🚀 NEW: Advanced AI Features

#### 1. Expense Forecasting
- **Predictive Analytics**: Forecast next month's spending using time series analysis
- **Category Predictions**: Get category-wise spending forecasts
- **Confidence Intervals**: View prediction ranges (lower/upper bounds)
- **Trend Analysis**: Identify spending trends (increasing/decreasing/stable)

#### 2. Net Worth Dashboard
- **Asset Tracking**: Monitor cash, investments, property, vehicles
- **Liability Management**: Track loans, credit cards, mortgages
- **Net Worth Calculation**: Real-time assets minus liabilities
- **Monthly Growth**: Track net worth changes over time
- **Cash Flow Summary**: Monthly income vs expenses analysis
- **Savings Rate**: Automatic savings percentage calculation

#### 3. Financial Health Score (0-100)
- **Comprehensive Scoring**: Based on 5 key financial metrics
- **Component Breakdown**: 
  - Savings Rate (30%)
  - Budget Adherence (25%)
  - Expense Stability (20%)
  - Debt Management (15%)
  - Spending Control (10%)
- **Color-Coded Rating**: Excellent/Good/Fair/Poor/Critical
- **Personalized Recommendations**: AI-generated improvement suggestions

#### 4. Financial Goal Planner
- **Goal Creation**: Set targets with deadlines
- **Progress Tracking**: Visual progress bars and percentages
- **Required Savings Calculator**: Know how much to save monthly
- **On-Track Status**: Automatic tracking vs actual savings
- **Completion Prediction**: Estimated achievement date
- **Goal Categories**: Emergency Fund, Vacation, House, Car, Education, Retirement

#### 5. Behavioral Spending Analysis
- **Month-over-Month Comparison**: Track category spending changes
- **Lifestyle Inflation Detection**: Identify increasing spending patterns
- **Budget Alerts**: Notifications for budget overruns
- **Smart Insights**: AI-generated spending pattern messages
- **Trend Identification**: Spot positive and negative changes

#### 6. Anomaly Detection
- **Unusual Transactions**: Statistical detection of outlier expenses
- **Category Anomalies**: Identify unusual category spending
- **Spending Spikes**: Detect sudden increases in daily spending
- **Severity Levels**: High/Medium risk classification
- **Detailed Explanations**: Understand why transactions are flagged

### Original Advanced Features
- **AI Chatbot Assistant**: Get financial advice and insights using AI
- **ML Predictions**: Machine learning model predicts expense categories automatically
- **SMS Auto-Import**: Parse and import expenses from SMS notifications
- **CSV Import/Export**: Bulk import expenses from CSV files
- **Data Visualization**: Interactive charts and graphs using Recharts
- **Authentication**: Secure JWT-based user authentication

### UI/UX
- **Premium Design**: Modern glass-morphism UI with animations
- **Responsive Layout**: Works seamlessly on desktop and mobile
- **Dark Theme**: Eye-friendly dark mode interface
- **Smooth Animations**: Framer Motion and React Spring animations
- **Real-time Updates**: Live data updates without page refresh
- **Professional Fintech Design**: Stripe/Revolut-inspired interface

## 🛠️ Tech Stack

### Frontend
- **React 18** - UI framework
- **Tailwind CSS** - Styling
- **Framer Motion** - Animations
- **Recharts** - Data visualization
- **Axios** - HTTP client
- **Lucide React** - Icons
- **React Hot Toast** - Notifications
- **React Circular Progressbar** - Health score visualization
- **React CountUp** - Animated counters

### Backend
- **FastAPI** - Python web framework
- **SQLAlchemy** - ORM
- **SQLite** - Database
- **JWT** - Authentication
- **Scikit-learn** - Machine learning
- **NumPy** - Statistical analysis
- **Uvicorn** - ASGI server
- **Python-dateutil** - Date handling

### AI & Analytics
- **Linear Regression** - Expense forecasting
- **Z-Score Analysis** - Anomaly detection
- **Time Series Analysis** - Trend prediction
- **Statistical Modeling** - Health score calculation

## 📦 Installation

### Prerequisites
- Node.js (v14 or higher)
- Python 3.8+
- pip

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python -m uvicorn main:app --reload
```

Backend will run on `http://127.0.0.1:8000`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

Frontend will run on `http://localhost:3000`

## 🚀 Quick Start

See [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md) for detailed setup instructions.

### Quick Setup

1. **Clone the repository**
```bash
git clone https://github.com/Vasanth-44/smart-expense-tracker.git
cd smart-expense-tracker
```

2. **Backend Setup**
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

3. **Frontend Setup**
```bash
cd frontend
npm install
npm start
```

4. **Access the Application**
- Frontend: http://localhost:3000
- Backend API: http://127.0.0.1:8000
- API Docs: http://127.0.0.1:8000/docs

## 📚 Documentation

- **[AI_FINANCE_PLATFORM_UPGRADE.md](AI_FINANCE_PLATFORM_UPGRADE.md)** - Complete feature documentation
- **[QUICK_START_GUIDE.md](QUICK_START_GUIDE.md)** - Setup and usage guide
- **[VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md)** - Deployment instructions

## 📱 Features in Detail

### Income Tracking
- Add multiple income sources
- Categorize income (Salary, Freelance, Investment, etc.)
- View income history and trends
- Track total income vs expenses

### Expense Management
- Quick expense entry with auto-categorization
- Edit and delete expenses
- Filter by date range and category
- Search functionality

### Budget Management
- Set monthly budgets per category
- Visual progress indicators
- Budget alerts and warnings
- Spending insights

### AI Features
- **AI Chatbot**: Ask questions about your finances
- **ML Predictions**: Automatic expense categorization
- **Smart Insights**: AI-generated financial advice

### Import/Export
- **SMS Import**: Parse bank SMS for automatic expense entry
- **CSV Import**: Bulk import from spreadsheets
- **CSV Export**: Export data for analysis

## 🎨 UI Components

- **Glass Card**: Modern glass-morphism design
- **Animated Background**: Dynamic gradient animations
- **Sidebar Navigation**: Smooth slide-in navigation
- **Modal Dialogs**: Elegant popup forms
- **Animated Counters**: Count-up number animations
- **Custom Buttons**: Styled interactive buttons

## 📊 API Endpoints

### Authentication
- `POST /auth/signup` - Register new user
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user

### Expenses & Income
- `GET/POST/PUT/DELETE /expenses` - Expense CRUD
- `GET/POST/PUT/DELETE /incomes` - Income CRUD

### Budget & Analytics
- `GET/POST/PUT/DELETE /budgets` - Budget management
- `GET /analytics/summary` - Financial summary
- `GET /analytics/insights` - Spending insights

### 🆕 Advanced Features
- `GET /forecast/next-month` - Expense forecast
- `GET /forecast/by-category` - Category forecasts
- `GET /forecast/trend` - Spending trend
- `GET /health/score` - Financial health score (0-100)
- `GET /networth/dashboard` - Net worth overview
- `GET/POST/PUT/DELETE /assets` - Asset management
- `GET/POST/PUT/DELETE /liabilities` - Liability management
- `GET/POST/PUT/DELETE /goals` - Financial goals
- `GET /goals/{id}/progress` - Goal progress
- `GET /anomalies/all` - Anomaly detection
- `GET /insights/behavioral` - Behavioral insights

### ML & AI
- `POST /predict-category` - Predict expense category
- `POST /ai/chat` - Chat with AI assistant

### Import
- `POST /import/sms` - Import from SMS
- `POST /import/csv` - Import from CSV

Full API documentation available at: http://127.0.0.1:8000/docs

## 🔐 Environment Variables

Create a `.env` file in the backend directory:

```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./expenses.db
```

## 📝 Project Structure

```
smart-expense-tracker/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── models.py            # Database models
│   ├── services.py          # Business logic
│   ├── auth.py              # Authentication
│   ├── database.py          # Database setup
│   ├── ai_assistant.py      # AI chatbot
│   ├── ml_predictions.py    # ML model
│   ├── sms_parser.py        # SMS parsing
│   ├── csv_import.py        # CSV import
│   ├── income_service.py    # Income logic
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── services/        # API services
│   │   └── App.js           # Main app
│   └── package.json         # Node dependencies
└── README.md
```

## 🚀 Deployment

### Deploy to Vercel (Frontend)
See [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md) for detailed instructions.

### Deploy Backend
Recommended platforms:
- **Render**: Easy Python deployment
- **Railway**: Simple setup with database
- **Heroku**: Classic PaaS option

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the MIT License.

## 👨‍💻 Author

**Vasanth**
- GitHub: [@Vasanth-44](https://github.com/Vasanth-44)

## 🙏 Acknowledgments

- FastAPI for the amazing Python framework
- React team for the excellent UI library
- Tailwind CSS for the utility-first CSS framework
- All open-source contributors

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

⭐ Star this repo if you find it helpful!
