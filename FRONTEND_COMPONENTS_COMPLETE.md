# COMPLETE FRONTEND COMPONENTS DOCUMENTATION

## Component Structure

### Main Components (11)
1. App.js - Main application with routing
2. Dashboard.js - Analytics dashboard with charts
3. ExpenseForm.js - Add/edit expense form
4. ExpenseList.js - Expense table with actions
5. IncomeForm.js - Add/edit income form
6. IncomeList.js - Income history table
7. FinancialSummary.js - Complete financial overview
8. BudgetManager.js - Budget management
9. Login.js - Login page
10. Signup.js - Signup page
11. AIChat.js - AI chatbot interface
12. CSVImport.js - CSV upload component
13. SMSImport.js - SMS import component

### UI Components (8)
1. GlassCard.js - Glassmorphism card wrapper
2. Button.js - Styled button component
3. Input.js - Styled input component
4. Modal.js - Modal dialog
5. Sidebar.js - Navigation sidebar
6. AnimatedBackground.js - Particle background
7. AnimatedCounter.js - Number counter animation

### Services (1)
1. api.js - API client with JWT interceptors

---

## Detailed Component Documentation

### App.js
**Purpose:** Main application component with routing and state management

**State:**
- user: Current authenticated user
- showSignup: Toggle between login/signup
- activeTab: Current active page
- refreshKey: Trigger data refresh
- editExpense: Expense being edited
- editIncome: Income being edited

**Key Functions:**
- handleLogin(userData): Set user after login
- handleSignup(userData): Set user after signup
- handleLogout(): Clear user and token
- handleExpenseSuccess(): Refresh data after expense operation
- handleEdit(expense): Set expense for editing
- handleEditIncome(income): Set income for editing

**Routing Logic:**
- If not authenticated: Show Login or Signup
- If authenticated: Show Sidebar + active tab content

**Active Tabs:**
- dashboard: Dashboard component
- add: ExpenseForm component
- expenses: ExpenseList component
- sms: SMSImport component
- add-income: IncomeForm component
- income-list: IncomeList component
- financial-summary: FinancialSummary component
- budget: BudgetManager component

**Features:**
- Animated background with particles
- Framer Motion page transitions
- Toast notifications
- JWT token persistence in localStorage

---

### Dashboard.js
**Purpose:** Main analytics dashboard with charts and insights

**Data Fetched:**
- Expenses (current month)
- Budgets
- Analytics summary
- ML predictions
- Anomalies

**Sections:**
1. Summary Cards (4 cards)
   - Total Spent (animated counter)
   - Budget Status (percentage)
   - Transactions Count
   - Average Transaction

2. ML Prediction Card
   - Next month spending prediction
   - Confidence level
   - Trend indicator

3. Anomaly Alerts
   - Large transactions
   - Category spikes
   - Unusual patterns

4. Charts (3 charts)
   - Spending by Category (Pie Chart)
   - Monthly Trend (Bar Chart)
   - Spending Forecast (Line Chart)

5. Budget Progress Bars
   - Per category progress
   - Color-coded (green/yellow/red)
   - Percentage indicators

**Animations:**
- Card entrance animations
- Counter animations
- Chart animations
- Hover effects

**Refresh:** Triggered by refreshKey prop

---

### ExpenseForm.js
**Purpose:** Add or edit expense with auto-categorization

**Props:**
- onSuccess: Callback after successful operation
- editExpense: Expense object to edit (optional)
- onCancel: Callback to cancel edit

**Form Fields:**
- amount: Number input (required)
- category: Dropdown (optional - auto-categorizes if empty)
- date: Date picker (required)
- note: Text input (optional)

**Features:**
- Auto-categorization: If note provided and category empty, ML predicts category
- Edit mode: Pre-fills form with expense data
- Validation: Amount > 0, date required
- Success toast notification
- Error handling

**API Calls:**
- POST /expenses (create)
- PUT /expenses/{id} (update)
- POST /predict-category (auto-categorize)

**Styling:**
- Glassmorphism card
- Animated form fields
- Gradient buttons
- Responsive layout

---

### ExpenseList.js
**Purpose:** Display all expenses in a table with actions

**Props:**
- refresh: Trigger data reload
- onEdit: Callback when edit clicked

**Features:**
- Sortable table
- Search/filter
- Edit button (calls onEdit)
- Delete button (with confirmation)
- Category badges (color-coded)
- Date formatting
- Amount formatting (currency)
- Empty state message
- Loading state
- CSV Import button

**Actions:**
- Edit: Opens ExpenseForm in edit mode
- Delete: Confirms and deletes expense

**API Calls:**
- GET /expenses (load data)
- DELETE /expenses/{id} (delete)

**Styling:**
- Glassmorphism table
- Hover effects
- Animated rows
- Responsive (mobile-friendly)

---

### IncomeForm.js
**Purpose:** Add or edit income entries

**Props:**
- onSuccess: Callback after successful operation
- editIncome: Income object to edit (optional)
- onCancel: Callback to cancel edit

**Form Fields:**
- amount: Number input (required)
- category: Dropdown (Salary, Freelance, Investment, etc.)
- date: Date picker (required)
- note: Text input (optional)

**Features:**
- 9 income categories
- Edit mode support
- Validation
- Success toast
- Green theme (vs red for expenses)

**API Calls:**
- POST /incomes (create)
- PUT /incomes/{id} (update)
- GET /income-categories (load categories)

---

### IncomeList.js
**Purpose:** Display all income entries in a table

**Props:**
- refresh: Trigger data reload
- onEdit: Callback when edit clicked

**Features:**
- Income table with all entries
- Edit and delete actions
- Category badges (green theme)
- Date and amount formatting
- Empty state
- Loading state

**API Calls:**
- GET /incomes (load data)
- DELETE /incomes/{id} (delete)

---

### FinancialSummary.js
**Purpose:** Complete financial overview with income vs expenses

**Data Fetched:**
- GET /analytics/financial-summary

**Sections:**
1. Summary Cards (4 cards)
   - Total Income (green)
   - Total Expenses (red)
   - Net Balance (blue/red based on positive/negative)
   - Savings Rate (percentage)

2. Income Breakdown Chart
   - Pie chart showing income by category
   - Animated with Recharts

3. Income vs Expenses Chart
   - Bar chart comparing income and expenses
   - Monthly view

4. Financial Health Indicator
   - Visual indicator based on savings rate
   - Color-coded (green/yellow/red)
   - Personalized message

**Calculations:**
- Net Balance = Total Income - Total Expenses
- Savings Rate = (Net Balance / Total Income) × 100

**Styling:**
- Green theme for income
- Red theme for expenses
- Animated counters
- Glassmorphism cards

---

### BudgetManager.js
**Purpose:** Set and manage budgets per category

**Data Fetched:**
- GET /budgets (existing budgets)
- GET /categories (available categories)

**Features:**
- Budget form for each category
- Current budget display
- Update budget
- Progress indicators
- Budget vs actual spending comparison

**API Calls:**
- GET /budgets
- POST /budgets (create/update)

**Styling:**
- Category cards
- Input fields
- Save buttons
- Progress bars

---

### Login.js
**Purpose:** User login page

**Props:**
- onLogin: Callback with user data
- onSwitchToSignup: Switch to signup page

**Form Fields:**
- email: Email input
- password: Password input

**Features:**
- Form validation
- Error messages
- Loading state
- Switch to signup link

**API Calls:**
- POST /auth/login

**On Success:**
- Stores JWT token in localStorage
- Stores user data in localStorage
- Calls onLogin callback

**Styling:**
- Centered card
- Glassmorphism
- Animated entrance
- Gradient background

---

### Signup.js
**Purpose:** User registration page

**Props:**
- onSignup: Callback with user data
- onSwitchToLogin: Switch to login page

**Form Fields:**
- email: Email input
- password: Password input
- confirmPassword: Password confirmation

**Features:**
- Password matching validation
- Email format validation
- Error messages
- Loading state
- Switch to login link

**API Calls:**
- POST /auth/signup

**On Success:**
- Stores JWT token in localStorage
- Stores user data in localStorage
- Calls onSignup callback

---

### AIChat.js
**Purpose:** AI-powered spending assistant chatbot

**State:**
- isOpen: Chat window open/closed
- messages: Chat history
- input: Current message input
- isTyping: AI typing indicator

**Features:**
- Floating chat button (bottom-right)
- Animated modal window
- Message history
- Quick suggestions
- Typing animation
- Auto-scroll to latest message

**API Calls:**
- POST /ai/chat (send message)
- GET /ai/suggestions (load suggestions)

**Message Types:**
- User messages (right-aligned, blue)
- AI messages (left-aligned, purple)

**Quick Suggestions:**
- "How can I save more?"
- "Analyze my spending"
- "Budget recommendations"
- "Where am I overspending?"

**Styling:**
- Glassmorphism modal
- Animated entrance/exit
- Gradient backgrounds
- Smooth scrolling

---

### CSVImport.js
**Purpose:** Import expenses from CSV files

**Props:**
- onImportSuccess: Callback after successful import

**Features:**
- Drag and drop file upload
- File validation (CSV only)
- Preview table (first 5 rows)
- Import progress indicator
- Success summary with category breakdown
- Duplicate detection
- Error handling

**CSV Format:**
- Columns: date, amount, note (category optional)
- Date formats: YYYY-MM-DD, DD/MM/YYYY, MM/DD/YYYY
- Amount: Numeric values

**API Calls:**
- POST /expenses/validate-csv (preview)
- POST /expenses/import-csv (import)

**Styling:**
- Upload area with dashed border
- Preview table
- Progress animation
- Success/error messages

---

### SMSImport.js
**Purpose:** Import expenses from SMS notifications

**Props:**
- onImportSuccess: Callback after successful import

**Features:**
- SMS text input area
- Example SMS templates
- Parse and preview
- Auto-categorization
- Create expense from SMS
- Duplicate detection

**Supported Banks:**
- HDFC, ICICI, SBI, Axis, Kotak
- Paytm, PhonePe, Google Pay
- 10+ bank formats

**SMS Format:**
- Extracts: amount, merchant, date, UPI reference
- Handles multiple date formats
- Parses Indian currency (Rs, INR)

**API Calls:**
- POST /sms/test-parse (preview)
- POST /sms/webhook (create expense)

**Example Templates:**
- Provides 3-4 example SMS formats
- Click to fill input

**Styling:**
- Text area for SMS input
- Example cards
- Preview section
- Success/error messages

---

### UI Components

#### GlassCard.js
**Purpose:** Reusable glassmorphism card wrapper

**Props:**
- children: Card content
- className: Additional CSS classes
- variant: 'default' | 'hover' | 'glow'

**Styling:**
- Semi-transparent background
- Backdrop blur effect
- Border with gradient
- Shadow effects
- Hover animations (if variant='hover')

#### Button.js
**Purpose:** Styled button component

**Props:**
- children: Button text
- onClick: Click handler
- variant: 'primary' | 'secondary' | 'danger'
- disabled: Boolean
- className: Additional CSS classes

**Variants:**
- primary: Blue gradient
- secondary: Gray
- danger: Red gradient

**Features:**
- Hover effects
- Active state
- Disabled state
- Loading spinner (optional)

#### Input.js
**Purpose:** Styled input component

**Props:**
- type: Input type
- value: Input value
- onChange: Change handler
- placeholder: Placeholder text
- className: Additional CSS classes

**Styling:**
- Glassmorphism background
- Focus effects
- Border animations
- Icon support (optional)

#### Modal.js
**Purpose:** Modal dialog component

**Props:**
- isOpen: Boolean
- onClose: Close handler
- title: Modal title
- children: Modal content

**Features:**
- Backdrop overlay
- Close button
- Click outside to close
- ESC key to close
- Animated entrance/exit

**Styling:**
- Centered modal
- Glassmorphism
- Framer Motion animations

#### Sidebar.js
**Purpose:** Navigation sidebar

**Props:**
- activeTab: Current active tab
- setActiveTab: Tab change handler
- onLogout: Logout handler
- user: Current user object

**Menu Items:**
- Dashboard
- Add Expense
- Expenses List
- Add Income
- Income History
- Financial Summary
- SMS Import
- Budget Manager
- Logout

**Features:**
- Active tab highlighting
- Icons for each item
- User email display
- Hover effects
- Responsive (collapsible on mobile)

**Styling:**
- Fixed left sidebar
- Glassmorphism
- Gradient accents
- Smooth transitions

#### AnimatedBackground.js
**Purpose:** Particle animation background

**Features:**
- 80+ animated particles
- Connecting lines between nearby particles
- Mouse interaction (particles move away from cursor)
- Smooth animations
- Canvas-based rendering

**Configuration:**
- Particle count: 80
- Particle size: 2-4px
- Connection distance: 150px
- Animation speed: Slow drift

**Styling:**
- Fixed position
- Full screen
- Behind all content (z-index: 0)
- Transparent particles with glow

#### AnimatedCounter.js
**Purpose:** Animated number counter

**Props:**
- value: Target number
- duration: Animation duration (ms)
- prefix: Text before number (e.g., "$")
- suffix: Text after number (e.g., "%")

**Features:**
- Smooth counting animation
- Decimal support
- Currency formatting
- Percentage formatting

**Usage:**
```jsx
<AnimatedCounter value={1250.50} prefix="$" duration={1000} />
```

---

### Services

#### api.js
**Purpose:** Centralized API client with JWT authentication

**Base URL:** http://localhost:8000

**Features:**
- Axios instance with interceptors
- Automatic JWT token injection
- Token refresh handling
- Error handling
- Request/response logging

**Request Interceptor:**
- Adds Authorization header with JWT token
- Reads token from localStorage

**Response Interceptor:**
- Handles 401 errors (redirects to login)
- Handles network errors
- Logs errors

**API Methods:**
- Auth: login, signup, getMe
- Expenses: getExpenses, createExpense, updateExpense, deleteExpense
- Incomes: getIncomes, createIncome, updateIncome, deleteIncome
- Budgets: getBudgets, setBudget
- Analytics: getSummary, getInsights, getFinancialSummary
- AI: chat, getSuggestions
- ML: predictNextMonth, getAnomalies, getInsights
- CSV: importCSV, validateCSV
- SMS: smsWebhook, testParse

**Error Handling:**
- Network errors: Shows toast notification
- 401 errors: Clears token and redirects to login
- 400/500 errors: Returns error message

**Token Management:**
- Stores token in localStorage on login/signup
- Reads token on every request
- Clears token on logout or 401 error
