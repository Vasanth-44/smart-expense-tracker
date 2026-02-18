# SMART EXPENSE TRACKER - COMPLETE PROJECT DOCUMENTATION

## TABLE OF CONTENTS
1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [Architecture](#architecture)
4. [Database Schema](#database-schema)
5. [Backend API Reference](#backend-api-reference)
6. [Frontend Components](#frontend-components)
7. [Features Documentation](#features-documentation)
8. [Setup & Installation](#setup--installation)
9. [File Structure](#file-structure)
10. [Development Guide](#development-guide)

---

## PROJECT OVERVIEW

**Name:** Smart Expense Tracker (AI-Powered Personal Finance Manager)

**Description:** A full-stack web application for comprehensive personal finance management with AI-powered features including expense tracking, income tracking, ML-based categorization, SMS transaction import, budget management, spending predictions, anomaly detection, and financial analytics.

**Purpose:** Help users manage their finances by automatically categorizing transactions, tracking budgets, predicting future spending, detecting unusual patterns, and providing personalized financial insights.

**Target Users:** Individuals who want to track personal finances with minimal manual effort

**Key Differentiators:**
- ML-based automatic expense categorization (TF-IDF + Naive Bayes)
- SMS transaction parsing for automatic import from bank notifications
- Predictive analytics for future spending
- Anomaly detection for unusual transactions
- AI chatbot for personalized financial advice
- Premium animated UI with glassmorphism design
- CSV import with duplicate detection
- Complete income and expense tracking with net balance calculation

---

## TECHNOLOGY STACK

### Backend Technologies

- **Framework:** FastAPI 0.104.1 (Modern Python web framework)
- **ORM:** SQLAlchemy 2.0.23 (Database abstraction layer)
- **Database:** SQLite (Lightweight embedded database)
- **Authentication:** JWT (JSON Web Tokens) via python-jose[cryptography]
- **Password Hashing:** bcrypt 4.1.1 (Secure password storage)
- **ML Libraries:** scikit-learn 1.3.2, numpy 1.26.2 (Machine learning)
- **Server:** Uvicorn 0.24.0 (ASGI server)
- **Validation:** Pydantic (Data validation via FastAPI)

### Frontend Technologies
- **Framework:** React 18.2.0 (UI library)
- **Styling:** Tailwind CSS 3.3.5 (Utility-first CSS)
- **Animations:** Framer Motion 10.16.5 (Animation library)
- **Charts:** Recharts 2.10.3 (Data visualization)
- **Icons:** Lucide React 0.294.0 (Icon library)
- **HTTP Client:** Axios 1.6.2 (API requests)
- **Notifications:** React Hot Toast 2.4.1 (Toast notifications)
- **Additional:** react-intersection-observer, react-countup, @react-spring/web

### Development Tools
- **Backend Package Manager:** pip (Python)
- **Frontend Package Manager:** npm (Node.js)
- **Version Control:** Git
- **Code Editor:** Any (VS Code recommended)

---

## ARCHITECTURE

### System Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                          │
│  React SPA (localhost:3000)                                  │
│  - Components (Dashboard, Forms, Lists)                      │
│  - UI Components (GlassCard, Button, Modal, Sidebar)         │
│  - Services (API Client with JWT interceptors)               │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP/REST API
                     │ (JWT Token in Headers)
┌────────────────────▼────────────────────────────────────────┐
│                      API LAYER                               │
│  FastAPI Backend (localhost:8000)                            │
│  - 40+ REST Endpoints                                        │
│  - JWT Authentication Middleware                             │
│  - CORS Configuration                                        │
│  - Request Validation (Pydantic)                             │
└────────────────────┬────────────────────────────────────────┘

                     │
┌────────────────────▼────────────────────────────────────────┐
│                   BUSINESS LOGIC LAYER                       │
│  - ExpenseService (CRUD operations)                          │
│  - IncomeService (Income management)                         │
│  - BudgetService (Budget tracking)                           │
│  - AnalyticsService (Financial analytics)                    │
│  - AICategorizer (ML categorization)                         │
│  - AISpendingAssistant (Chatbot)                             │
│  - MLPredictionService (Predictions & anomalies)             │
│  - CSVImportService (CSV parsing)                            │
│  - SMSTransactionParser (SMS parsing)                        │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                    DATA ACCESS LAYER                         │
│  SQLAlchemy ORM                                              │
│  - Models (User, Expense, Budget, Income)                    │
│  - Relationships (One-to-Many)                               │
│  - Session Management                                        │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                    DATABASE LAYER                            │
│  SQLite Database (expenses.db)                               │
│  - users table                                               │
│  - expenses table                                            │
│  - budgets table                                             │
│  - incomes table                                             │
└─────────────────────────────────────────────────────────────┘
```

### Authentication Flow
```
1. User submits email/password → Frontend
2. Frontend sends POST /auth/login → Backend
3. Backend validates credentials (bcrypt)
4. Backend generates JWT token
5. Backend returns token + user data
6. Frontend stores token in localStorage
7. Frontend includes token in all API requests (Authorization: Bearer <token>)
8. Backend validates token on each request
9. Backend extracts user_id from token
10. Backend filters data by user_id
```

### Data Flow Example (Create Expense)
```
1. User fills expense form → ExpenseForm component
2. Component calls api.createExpense() → API service
3. API service sends POST /expenses with JWT token
4. Backend validates JWT → get_current_user()
5. Backend auto-categorizes if needed → AICategorizer
6. Backend creates expense → ExpenseService
7. Backend saves to database → SQLAlchemy
8. Backend returns created expense
9. Frontend updates UI → Dashboard refresh
10. Frontend shows success toast
```

---

## DATABASE SCHEMA

### Tables Overview

The database contains 4 main tables with relationships:

**1. users** - User accounts
**2. expenses** - Expense transactions
**3. incomes** - Income transactions
**4. budgets** - Budget limits per category

### Table: users
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL
);
CREATE INDEX ix_users_id ON users (id);
CREATE INDEX ix_users_email ON users (email);
```

**Columns:**
- `id` (Integer, Primary Key): Unique user identifier
- `email` (String, Unique, Not Null): User email for login
- `hashed_password` (String, Not Null): bcrypt hashed password

**Relationships:**
- One-to-Many with expenses (user can have multiple expenses)
- One-to-Many with incomes (user can have multiple incomes)
- One-to-Many with budgets (user can have multiple budgets)

**SQLAlchemy Model:**
```python
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    expenses = relationship("Expense", back_populates="owner", cascade="all, delete-orphan")
    budgets = relationship("Budget", back_populates="owner", cascade="all, delete-orphan")
    incomes = relationship("Income", back_populates="owner", cascade="all, delete-orphan")
```

### Table: expenses
```sql
CREATE TABLE expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount FLOAT NOT NULL,
    category VARCHAR NOT NULL,
    date DATE NOT NULL,
    note VARCHAR,
    user_id INTEGER NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE INDEX ix_expenses_id ON expenses (id);
```

**Columns:**
- `id` (Integer, Primary Key): Unique expense identifier
- `amount` (Float, Not Null): Expense amount in currency
- `category` (String, Not Null): Expense category (Food, Gym, Travel, Shopping, Misc)
- `date` (Date, Not Null): Transaction date
- `note` (String, Nullable): Description/merchant name
- `user_id` (Integer, Foreign Key, Not Null): References users.id

**SQLAlchemy Model:**
```python
class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    note = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="expenses")
```

### Table: incomes
```sql
CREATE TABLE incomes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount FLOAT NOT NULL,
    category VARCHAR NOT NULL,
    date DATE NOT NULL,
    note VARCHAR,
    user_id INTEGER NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE INDEX ix_incomes_id ON incomes (id);
```

**Columns:**
- `id` (Integer, Primary Key): Unique income identifier
- `amount` (Float, Not Null): Income amount in currency
- `category` (String, Not Null): Income category (Salary, Freelance, Investment, Business, Gift, Refund, Cashback, Bonus, Other)
- `date` (Date, Not Null): Transaction date
- `note` (String, Nullable): Description/source
- `user_id` (Integer, Foreign Key, Not Null): References users.id

**SQLAlchemy Model:**
```python
class Income(Base):
    __tablename__ = "incomes"
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    note = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="incomes")
```

### Table: budgets
```sql
CREATE TABLE budgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category VARCHAR NOT NULL,
    amount FLOAT NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE INDEX ix_budgets_id ON budgets (id);
```

**Columns:**
- `id` (Integer, Primary Key): Unique budget identifier
- `category` (String, Not Null): Budget category (Food, Gym, Travel, Shopping, Misc)
- `amount` (Float, Not Null): Budget limit amount
- `user_id` (Integer, Foreign Key, Not Null): References users.id

**SQLAlchemy Model:**
```python
class Budget(Base):
    __tablename__ = "budgets"
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="budgets")
```

### Categories

**Expense Categories (5):**
1. Food - Restaurants, groceries, food delivery
2. Gym - Fitness, sports, health
3. Travel - Transportation, flights, hotels
4. Shopping - Retail, online shopping, clothing
5. Misc - Everything else

**Income Categories (9):**
1. Salary - Regular employment income
2. Freelance - Contract work, gigs
3. Investment - Dividends, capital gains
4. Business - Business revenue
5. Gift - Money received as gifts
6. Refund - Returns, reimbursements
7. Cashback - Rewards, cashback
8. Bonus - Performance bonuses
9. Other - Miscellaneous income

---

## BACKEND API REFERENCE

### Base URL
```
http://localhost:8000
```

### Authentication Endpoints

#### POST /auth/signup
Create a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com"
  }
}
```

**Errors:**
- 400: Email already registered

#### POST /auth/login
Authenticate user and get JWT token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com"
  }
}
```

**Errors:**
- 401: Incorrect email or password

#### GET /auth/me
Get current authenticated user info.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "id": 1,
  "email": "user@example.com"
}
```

### Expense Endpoints (Protected)

#### GET /expenses
Get all expenses for authenticated user.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
[
  {
    "id": 1,
    "amount": 45.50,
    "category": "Food",
    "date": "2024-01-15",
    "note": "Lunch at restaurant"
  },
  {
    "id": 2,
    "amount": 120.00,
    "category": "Shopping",
    "date": "2024-01-16",
    "note": "New shoes"
  }
]
```

#### POST /expenses
Create a new expense.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "amount": 45.50,
  "category": "Food",  // Optional - will auto-categorize if omitted
  "date": "2024-01-15",
  "note": "Lunch at restaurant"
}
```

**Response (200):**
```json
{
  "id": 1,
  "amount": 45.50,
  "category": "Food",
  "date": "2024-01-15",
  "note": "Lunch at restaurant"
}
```

**Auto-Categorization:**
- If `category` is omitted and `note` is provided, ML model predicts category
- If both omitted, defaults to "Misc"

#### PUT /expenses/{expense_id}
Update an existing expense.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "amount": 50.00,
  "category": "Food",
  "date": "2024-01-15",
  "note": "Updated note"
}
```

**Response (200):**
```json
{
  "id": 1,
  "amount": 50.00,
  "category": "Food",
  "date": "2024-01-15",
  "note": "Updated note"
}
```

**Errors:**
- 404: Expense not found or doesn't belong to user
