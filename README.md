# Smart Expense Tracker

AI-powered expense tracking application with auto-categorization, budget alerts, and smart insights.

## Tech Stack

- **Frontend**: React + Tailwind CSS + Recharts
- **Backend**: Python FastAPI + SQLAlchemy
- **Database**: SQLite

## Features

- ✅ Expense Management (Add/Edit/Delete)
- 🤖 AI Auto-Categorization (ML Model: TF-IDF + Naive Bayes)
- 📊 Dashboard with Charts (Pie & Bar)
- 💰 Budget Tracking & Alerts
- 💡 Smart Spending Insights
- 🔐 User Authentication (JWT + bcrypt)
- 👤 Multi-user Support (Each user sees only their data)
- 🧠 Machine Learning with automatic keyword fallback

## Setup Instructions

### Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Train ML model (optional but recommended)
python train_model.py

# Database will be created automatically on first run
uvicorn main:app --reload
```

Backend runs at: http://localhost:8000

**Note:** The old database needs to be deleted if you had one before. Delete `expenses.db` file and restart the server to create a new database with authentication tables.

**ML Model:** The system uses a trained ML model for categorization. If the model file is not found, it automatically falls back to keyword-based logic.

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

Frontend runs at: http://localhost:3000

## Project Structure

```
smart-expense-tracker/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── models.py            # Database models
│   ├── database.py          # DB connection
│   ├── services.py          # Business logic
│   ├── ai_categorizer.py    # AI categorization
│   ├── seed_data.py         # Sample data
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── services/        # API calls
│   │   ├── App.js
│   │   └── index.js
│   ├── package.json
│   └── tailwind.config.js
└── README.md
```

## API Endpoints

### Authentication
- `POST /auth/signup` - Create new account
- `POST /auth/login` - Login user
- `GET /auth/me` - Get current user

### Protected Endpoints (Require JWT Token)
- `GET /expenses` - List user's expenses
- `POST /expenses` - Create expense
- `PUT /expenses/{id}` - Update expense
- `DELETE /expenses/{id}` - Delete expense
- `GET /budgets` - List user's budgets
- `POST /budgets` - Create/update budget
- `GET /analytics/summary` - Dashboard analytics
- `GET /analytics/insights` - AI insights

### Public Endpoints
- `POST /predict-category` - Predict category from note
- `GET /categories` - List all categories

## Sample Data

Create an account using the signup page. Each user has their own isolated data.
