# COMPLETE BACKEND SERVICES DOCUMENTATION

## Backend Service Files

### Core Services (9 files)
1. main.py - FastAPI application with all endpoints
2. models.py - SQLAlchemy database models
3. database.py - Database connection and session management
4. auth.py - JWT authentication and password hashing
5. services.py - ExpenseService, BudgetService, AnalyticsService
6. income_service.py - IncomeService for income management
7. ai_categorizer.py - ML-based expense categorization
8. ai_assistant.py - AI chatbot for financial advice
9. ml_predictions.py - Spending predictions and anomaly detection
10. csv_import.py - CSV file parsing and import
11. sms_parser.py - SMS transaction parsing
12. train_model.py - ML model training script
13. create_simple_model.py - Fallback model creation
14. seed_data.py - Sample data generator

---

## Detailed Service Documentation

### auth.py
**Purpose:** JWT authentication and password hashing

**Dependencies:**
- bcrypt: Password hashing
- python-jose: JWT token generation/validation
- datetime: Token expiration

**Configuration:**
- SECRET_KEY: "your-secret-key-here-change-in-production"
- ALGORITHM: "HS256"
- ACCESS_TOKEN_EXPIRE_MINUTES: 30

**Functions:**

#### get_password_hash(password: str) -> str
Hashes a plain password using bcrypt.
- Input: Plain text password
- Output: Bcrypt hashed password
- Salt rounds: 12 (default)

#### verify_password(plain_password: str, hashed_password: str) -> bool
Verifies a password against its hash.
- Input: Plain password, hashed password
- Output: True if match, False otherwise

#### create_access_token(data: dict) -> str
Creates a JWT access token.
- Input: Data dict (usually {"sub": email})
- Output: JWT token string
- Expiration: 30 minutes from creation
- Includes: exp (expiration time)

#### get_user_by_email(db: Session, email: str) -> User | None
Fetches user by email from database.
- Input: Database session, email
- Output: User object or None

#### authenticate_user(db: Session, email: str, password: str) -> User | False
Authenticates user credentials.
- Input: Database session, email, password
- Output: User object if valid, False otherwise
- Process: Fetch user, verify password

#### get_current_user(token: str, db: Session) -> User
Dependency for protected routes. Validates JWT and returns user.
- Input: JWT token (from Authorization header), database session
- Output: User object
- Raises: HTTPException 401 if invalid token
- Process: Decode JWT, extract email, fetch user

---

### services.py
**Purpose:** Business logic for expenses, budgets, and analytics

#### ExpenseService

**Methods:**

##### get_all_expenses(db: Session, user_id: int) -> List[Expense]
Get all expenses for a user, ordered by date descending.

##### create_expense(db, amount, category, date, note, user_id) -> Expense
Create a new expense.
- Validates amount > 0
- Creates Expense object
- Saves to database
- Returns created expense

##### update_expense(db, expense_id, amount, category, date, note, user_id) -> Expense | None
Update an existing expense.
- Fetches expense by ID and user_id
- Updates fields
- Commits to database
- Returns updated expense or None if not found

##### delete_expense(db, expense_id, user_id) -> bool
Delete an expense.
- Fetches expense by ID and user_id
- Deletes from database
- Returns True if deleted, False if not found

#### BudgetService

**Methods:**

##### get_all_budgets(db: Session, user_id: int) -> List[Budget]
Get all budgets for a user.

##### set_budget(db, category, amount, user_id) -> Budget
Create or update budget for a category.
- Checks if budget exists for category
- Updates if exists, creates if not
- Returns budget object

##### get_budget_status(db, user_id) -> dict
Get budget status with spending comparison.
- Fetches all budgets
- Calculates total spent per category
- Returns dict with budget, spent, percentage for each category

#### AnalyticsService

**Methods:**

##### get_summary(db, user_id) -> dict
Get dashboard analytics summary.
- Total spent (current month)
- Spending by category
- Budget status
- Monthly trends
- Returns comprehensive dict

##### get_insights(db, user_id) -> List[str]
Generate AI insights about spending.
- Analyzes spending patterns
- Compares to previous month
- Checks budget adherence
- Returns list of insight strings

##### get_category_breakdown(db, user_id, start_date, end_date) -> dict
Get spending breakdown by category for date range.
- Groups expenses by category
- Sums amounts
- Returns dict {category: amount}

##### get_monthly_trend(db, user_id, months=6) -> List[dict]
Get monthly spending trend.
- Fetches expenses for last N months
- Groups by month
- Returns list of {month, amount}

---

### income_service.py
**Purpose:** Business logic for income management

**Income Categories:**
- Salary, Freelance, Investment, Business, Gift, Refund, Cashback, Bonus, Other

#### IncomeService

**Methods:**

##### get_categories() -> List[str]
Returns list of all income categories.

##### get_all_incomes(db: Session, user_id: int) -> List[Income]
Get all incomes for a user, ordered by date descending.

##### create_income(db, amount, category, date, note, user_id) -> Income
Create a new income entry.
- Validates amount > 0
- Validates category in allowed list
- Creates Income object
- Saves to database
- Returns created income

##### update_income(db, income_id, amount, category, date, note, user_id) -> Income | None
Update an existing income.
- Fetches income by ID and user_id
- Updates fields
- Commits to database
- Returns updated income or None if not found

##### delete_income(db, income_id, user_id) -> bool
Delete an income.
- Fetches income by ID and user_id
- Deletes from database
- Returns True if deleted, False if not found

##### get_total_income(db, user_id, start_date) -> float
Get total income from start_date to now.
- Sums all income amounts
- Filters by user_id and date >= start_date
- Returns total as float

##### get_income_by_category(db, user_id, start_date) -> dict
Get income breakdown by category.
- Groups incomes by category
- Sums amounts per category
- Returns dict {category: amount}

---

### ai_categorizer.py
**Purpose:** ML-based expense categorization

**Categories:** Food, Gym, Travel, Shopping, Misc

**ML Model:**
- Algorithm: TF-IDF + Naive Bayes
- Training data: 100+ labeled examples
- Model file: expense_model.pkl
- Fallback: Keyword-based matching

**Keyword Mapping:**
```python
CATEGORY_KEYWORDS = {
    'Food': ['restaurant', 'food', 'lunch', 'dinner', 'breakfast', 'cafe', 'pizza', 'burger', 'swiggy', 'zomato', 'grocery', 'supermarket'],
    'Gym': ['gym', 'fitness', 'yoga', 'sports', 'workout', 'health', 'exercise'],
    'Travel': ['uber', 'ola', 'taxi', 'flight', 'hotel', 'train', 'bus', 'travel', 'petrol', 'fuel'],
    'Shopping': ['amazon', 'flipkart', 'shopping', 'mall', 'store', 'clothes', 'shoes', 'electronics'],
    'Misc': []
}
```

#### AICategorizer

**Methods:**

##### load_model() -> tuple
Load ML model from pickle file.
- Returns: (vectorizer, classifier) or (None, None) if not found
- Handles file not found gracefully

##### predict_category(note: str) -> str
Predict category from note text.
- Input: Note/description text
- Output: Category string
- Process:
  1. Try ML model if loaded
  2. Fall back to keyword matching
  3. Default to "Misc" if no match
- Case insensitive matching

##### get_categories() -> List[str]
Returns list of all expense categories.

---

### ai_assistant.py
**Purpose:** AI-powered spending assistant chatbot

#### AISpendingAssistant

**Methods:**

##### generate_response(user_id, query, db) -> dict
Generate AI response to user query.
- Input: User ID, query text, database session
- Output: Dict with response and suggestions
- Process:
  1. Fetch user's expense data
  2. Analyze spending patterns
  3. Generate personalized response
  4. Return response with suggestions

**Response Types:**
- Saving tips
- Overspending analysis
- Budget recommendations
- Category insights
- Financial summary

**Example Queries:**
- "How can I save more?"
- "Analyze my spending"
- "Where am I overspending?"
- "Budget recommendations"

##### get_quick_suggestions() -> List[str]
Returns list of quick suggestion prompts for UI.

**Suggestions:**
- "How can I save more money?"
- "Analyze my spending patterns"
- "Give me budget recommendations"
- "Where am I overspending?"

---

### ml_predictions.py
**Purpose:** ML-based spending predictions and anomaly detection

#### MLPredictionService

**Methods:**

##### predict_next_month(user_id, db) -> dict
Predict next month's spending using linear regression.
- Input: User ID, database session
- Output: Dict with prediction, confidence, trend
- Algorithm: Linear regression on last 6 months
- Returns:
  - predicted_amount: Float
  - confidence: "high" | "medium" | "low"
  - trend: "increasing" | "decreasing" | "stable"
  - historical_average: Float

**Confidence Levels:**
- High: R² > 0.7
- Medium: R² > 0.4
- Low: R² <= 0.4

##### detect_anomalies(user_id, db) -> dict
Detect spending anomalies using Z-score.
- Input: User ID, database session
- Output: Dict with anomalies list
- Detection methods:
  1. Large transactions (Z-score > 2)
  2. Category spikes (>50% increase from average)
  3. Unusual patterns

**Anomaly Types:**
- large_transaction: Single large expense
- category_spike: Category spending spike
- unusual_pattern: Other unusual patterns

##### get_spending_insights(user_id, db) -> dict
Get comprehensive ML insights.
- Combines predictions and anomalies
- Adds trends and recommendations
- Returns complete insight dict

---

### csv_import.py
**Purpose:** CSV file parsing and expense import

**Supported Formats:**
- Columns: date, amount, note, category (optional)
- Date formats: YYYY-MM-DD, DD/MM/YYYY, MM/DD/YYYY, DD-MM-YYYY
- Amount: Numeric with optional currency symbols

#### CSVImportService

**Methods:**

##### parse_csv(file_content: str) -> tuple
Parse CSV file content.
- Input: CSV file content as string
- Output: (parsed_rows, errors)
- Process:
  1. Detect delimiter (comma, semicolon, tab)
  2. Parse rows
  3. Validate and normalize data
  4. Return valid rows and errors

**Column Name Variations:**
- Date: date, Date, DATE, transaction_date, Transaction Date
- Amount: amount, Amount, AMOUNT, value, Value
- Note: note, Note, NOTE, description, Description, merchant
- Category: category, Category, CATEGORY (optional)

##### validate_csv(file_content: str) -> dict
Validate CSV and return preview.
- Input: CSV file content
- Output: Dict with validation results
- Returns:
  - valid: Boolean
  - rows: Row count
  - preview: First 5 rows
  - errors: List of errors

##### import_expenses(user_id, parsed_rows, db) -> dict
Import expenses from parsed rows.
- Input: User ID, parsed rows, database session
- Output: Import summary dict
- Features:
  - Auto-categorization using ML
  - Duplicate detection (same date + amount + note)
  - Error handling
- Returns:
  - imported: Count of imported expenses
  - duplicates: Count of duplicates skipped
  - errors: Count of errors
  - category_breakdown: Dict of counts per category

---

### sms_parser.py
**Purpose:** Parse SMS transaction notifications

**Supported Banks/Apps:**
- HDFC Bank, ICICI Bank, SBI, Axis Bank, Kotak Bank
- Paytm, PhonePe, Google Pay
- 10+ bank formats

#### SMSTransactionParser

**Methods:**

##### parse_sms(message: str, sender: str) -> dict | None
Parse SMS transaction message.
- Input: SMS message text, sender ID
- Output: Dict with parsed data or None
- Extracts:
  - amount: Float
  - merchant: String
  - date: Date object
  - note: String (formatted)
  - upi_ref: String (optional)

**Parsing Logic:**
1. Extract amount (Rs, INR, ₹)
2. Extract merchant name
3. Extract date (multiple formats)
4. Extract UPI reference (if present)
5. Format note string

**Date Formats Supported:**
- DD-MMM-YY (15-Jan-24)
- DD/MM/YYYY (15/01/2024)
- DD-MM-YYYY (15-01-2024)
- YYYY-MM-DD (2024-01-15)

**Amount Formats:**
- Rs 450.00
- INR 450.00
- ₹450.00
- 450.00 INR

**Example SMS:**
```
Rs 450.00 debited from A/c XX1234 on 15-Jan-24 at Swiggy
```

**Parsed Output:**
```python
{
    "amount": 450.00,
    "merchant": "Swiggy",
    "date": date(2024, 1, 15),
    "note": "Swiggy - Rs 450.00",
    "upi_ref": None
}
```

---

### train_model.py
**Purpose:** Train ML model for expense categorization

**Training Data:**
- 100+ labeled examples
- 5 categories: Food, Gym, Travel, Shopping, Misc
- Diverse merchant names and descriptions

**Algorithm:**
- TF-IDF Vectorizer (max_features=100)
- Multinomial Naive Bayes classifier

**Process:**
1. Load training data (hardcoded examples)
2. Create TF-IDF vectorizer
3. Transform text to vectors
4. Train Naive Bayes classifier
5. Save model to expense_model.pkl

**Usage:**
```bash
python train_model.py
```

**Output:**
- expense_model.pkl (contains vectorizer and classifier)
- Training accuracy printed to console

---

### create_simple_model.py
**Purpose:** Create fallback model without scikit-learn

**Use Case:**
- When scikit-learn installation fails
- Windows systems without C++ build tools

**Model:**
- Simple pickle file with keyword mappings
- No ML, just keyword-based categorization

**Usage:**
```bash
python create_simple_model.py
```

---

### seed_data.py
**Purpose:** Generate sample data for testing

**Creates:**
- Sample user account
- 20+ sample expenses across all categories
- Sample budgets for each category

**Usage:**
```bash
python seed_data.py
```

**Sample Data:**
- Food: Restaurant, grocery, cafe expenses
- Gym: Fitness, yoga expenses
- Travel: Uber, flight, hotel expenses
- Shopping: Amazon, mall expenses
- Misc: Various other expenses

---

## Database Connection (database.py)

**Purpose:** SQLAlchemy database setup and session management

**Configuration:**
- Database: SQLite
- File: expenses.db
- Connection string: sqlite:///./expenses.db

**Components:**

### engine
SQLAlchemy engine for database connection.
- Creates database file if not exists
- Handles connection pooling

### SessionLocal
Session factory for creating database sessions.
- autocommit=False: Manual commit required
- autoflush=False: Manual flush required

### Base
Declarative base for SQLAlchemy models.
- All models inherit from Base

### get_db()
Dependency function for FastAPI routes.
- Yields database session
- Automatically closes session after request
- Usage: `db: Session = Depends(get_db)`

**Database Initialization:**
```python
Base.metadata.create_all(bind=engine)
```
- Creates all tables on application startup
- Idempotent (safe to run multiple times)

---

## Pydantic Models (main.py)

**Purpose:** Request/response validation

**Models:**

### UserSignup
- email: str
- password: str

### UserLogin
- email: str
- password: str

### Token
- access_token: str
- token_type: str
- user: dict

### ExpenseCreate
- amount: float
- category: Optional[str]
- date: date
- note: Optional[str]

### ExpenseUpdate
- amount: float
- category: str
- date: date
- note: Optional[str]

### BudgetCreate
- category: str
- amount: float

### CategoryPrediction
- note: str

### ChatMessage
- message: str

### SMSWebhook
- sender: str
- message: str
- timestamp: Optional[str]

### IncomeCreate
- amount: float
- category: str
- date: date
- note: Optional[str]

### IncomeUpdate
- amount: float
- category: str
- date: date
- note: Optional[str]

---

## CORS Configuration

**Allowed Origins:**
- http://localhost:3000 (React frontend)

**Allowed Methods:**
- All methods (GET, POST, PUT, DELETE, etc.)

**Allowed Headers:**
- All headers

**Credentials:**
- Enabled (allows cookies and auth headers)

---

## Error Handling

**HTTP Exceptions:**
- 400: Bad Request (validation errors, duplicates)
- 401: Unauthorized (invalid credentials, expired token)
- 404: Not Found (resource doesn't exist)
- 500: Internal Server Error (unexpected errors)

**Error Response Format:**
```json
{
  "detail": "Error message here"
}
```

**Common Errors:**
- "Email already registered" (signup with existing email)
- "Incorrect email or password" (login with wrong credentials)
- "Expense not found" (update/delete non-existent expense)
- "SMS does not contain a valid transaction" (invalid SMS format)
- "Only CSV files are supported" (wrong file type)
