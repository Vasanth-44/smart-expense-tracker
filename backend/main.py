from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from datetime import date, timedelta, datetime
from typing import Optional

from database import engine, get_db, Base
from models import User, Expense, Budget, Income
from services import ExpenseService, BudgetService, AnalyticsService
from income_service import IncomeService
from ai_categorizer import AICategorizer
from ai_assistant import AISpendingAssistant
from ml_predictions import MLPredictionService
from csv_import import CSVImportService
from sms_parser import SMSTransactionParser
from auth import (
    get_password_hash, 
    authenticate_user, 
    create_access_token, 
    get_current_user,
    get_user_by_email
)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart Expense Tracker API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class UserSignup(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict

class ExpenseCreate(BaseModel):
    amount: float
    category: Optional[str] = None
    date: date
    note: Optional[str] = None

class ExpenseUpdate(BaseModel):
    amount: float
    category: str
    date: date
    note: Optional[str] = None

class BudgetCreate(BaseModel):
    category: str
    amount: float

class CategoryPrediction(BaseModel):
    note: str

class ChatMessage(BaseModel):
    message: str

class SMSWebhook(BaseModel):
    sender: str
    message: str
    timestamp: Optional[str] = None

class IncomeCreate(BaseModel):
    amount: float
    category: str
    date: date
    note: Optional[str] = None

class IncomeUpdate(BaseModel):
    amount: float
    category: str
    date: date
    note: Optional[str] = None

# Auth Routes
@app.post("/auth/signup", response_model=Token)
def signup(user_data: UserSignup, db: Session = Depends(get_db)):
    # Check if user exists
    existing_user = get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(email=user_data.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create FREE subscription for new user
    from subscription_service import SubscriptionService
    SubscriptionService.create_subscription(db, new_user.id)
    
    # Create token
    access_token = create_access_token(data={"sub": new_user.email})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {"id": new_user.id, "email": new_user.email}
    }

@app.post("/auth/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password"
        )
    
    access_token = create_access_token(data={"sub": user.email})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {"id": user.id, "email": user.email}
    }

@app.get("/auth/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "email": current_user.email}

# Protected Routes
@app.get("/")
def root():
    return {"message": "Smart Expense Tracker API"}

@app.get("/expenses")
def get_expenses(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    expenses = ExpenseService.get_all_expenses(db, current_user.id)
    return [
        {
            "id": e.id,
            "amount": e.amount,
            "category": e.category,
            "date": e.date.isoformat(),
            "note": e.note
        }
        for e in expenses
    ]

@app.post("/expenses")
def create_expense(
    expense: ExpenseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Auto-categorize if category not provided
    category = expense.category
    if not category and expense.note:
        category = AICategorizer.predict_category(expense.note)
    elif not category:
        category = "Misc"
    
    new_expense = ExpenseService.create_expense(
        db, expense.amount, category, expense.date, expense.note, current_user.id
    )
    return {
        "id": new_expense.id,
        "amount": new_expense.amount,
        "category": new_expense.category,
        "date": new_expense.date.isoformat(),
        "note": new_expense.note
    }

@app.put("/expenses/{expense_id}")
def update_expense(
    expense_id: int,
    expense: ExpenseUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    updated = ExpenseService.update_expense(
        db, expense_id, expense.amount, expense.category, expense.date, expense.note, current_user.id
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Expense not found")
    return {
        "id": updated.id,
        "amount": updated.amount,
        "category": updated.category,
        "date": updated.date.isoformat(),
        "note": updated.note
    }

@app.delete("/expenses/{expense_id}")
def delete_expense(
    expense_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    success = ExpenseService.delete_expense(db, expense_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"message": "Expense deleted"}

@app.post("/predict-category")
def predict_category(data: CategoryPrediction):
    category = AICategorizer.predict_category(data.note)
    return {"category": category}

@app.get("/categories")
def get_categories():
    return {"categories": AICategorizer.get_categories()}

@app.get("/budgets")
def get_budgets(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    budgets = BudgetService.get_all_budgets(db, current_user.id)
    return [{"id": b.id, "category": b.category, "amount": b.amount} for b in budgets]

@app.post("/budgets")
def set_budget(
    budget: BudgetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_budget = BudgetService.set_budget(db, budget.category, budget.amount, current_user.id)
    return {"id": new_budget.id, "category": new_budget.category, "amount": new_budget.amount}

@app.get("/analytics/summary")
def get_summary(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return AnalyticsService.get_summary(db, current_user.id)

@app.get("/analytics/insights")
def get_insights(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return {"insights": AnalyticsService.get_insights(db, current_user.id)}

# Income Routes
@app.get("/incomes")
def get_incomes(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    incomes = IncomeService.get_all_incomes(db, current_user.id)
    return [
        {
            "id": i.id,
            "amount": i.amount,
            "category": i.category,
            "date": i.date.isoformat(),
            "note": i.note
        }
        for i in incomes
    ]

@app.post("/incomes")
def create_income(
    income: IncomeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_income = IncomeService.create_income(
        db, income.amount, income.category, income.date, income.note, current_user.id
    )
    return {
        "id": new_income.id,
        "amount": new_income.amount,
        "category": new_income.category,
        "date": new_income.date.isoformat(),
        "note": new_income.note
    }

@app.put("/incomes/{income_id}")
def update_income(
    income_id: int,
    income: IncomeUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    updated = IncomeService.update_income(
        db, income_id, income.amount, income.category, income.date, income.note, current_user.id
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Income not found")
    return {
        "id": updated.id,
        "amount": updated.amount,
        "category": updated.category,
        "date": updated.date.isoformat(),
        "note": updated.note
    }

@app.delete("/incomes/{income_id}")
def delete_income(
    income_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    success = IncomeService.delete_income(db, income_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Income not found")
    return {"message": "Income deleted"}

@app.get("/income-categories")
def get_income_categories():
    return {"categories": IncomeService.get_categories()}

@app.get("/analytics/financial-summary")
def get_financial_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get complete financial summary with income and expenses"""
    now = datetime.now()
    current_month_start = now.replace(day=1)
    
    # Get current month income and expenses
    total_income = IncomeService.get_total_income(db, current_user.id, current_month_start)
    total_expenses_result = db.query(func.sum(Expense.amount)).filter(
        Expense.user_id == current_user.id,
        Expense.date >= current_month_start
    ).scalar()
    total_expenses = float(total_expenses_result) if total_expenses_result else 0
    
    net_balance = total_income - total_expenses
    savings_rate = (net_balance / total_income * 100) if total_income > 0 else 0
    
    # Get income breakdown
    income_breakdown = IncomeService.get_income_by_category(db, current_user.id, current_month_start)
    
    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "net_balance": net_balance,
        "savings_rate": round(savings_rate, 2),
        "month": now.strftime('%B %Y'),
        "income_breakdown": income_breakdown
    }

# AI Chat Routes
@app.post("/ai/chat")
def chat_with_ai(
    chat: ChatMessage,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """AI-powered spending assistant endpoint."""
    response = AISpendingAssistant.generate_response(
        user_id=current_user.id,
        query=chat.message,
        db=db
    )
    return response

@app.get("/ai/suggestions")
def get_chat_suggestions():
    """Get quick suggestion prompts for chat UI."""
    return {"suggestions": AISpendingAssistant.get_quick_suggestions()}

# ML Prediction Routes
@app.get("/ml/predict-next-month")
def predict_next_month(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Predict next month's spending using ML."""
    prediction = MLPredictionService.predict_next_month(current_user.id, db)
    return prediction

@app.get("/ml/anomalies")
def detect_anomalies(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Detect spending anomalies and unusual patterns."""
    anomalies = MLPredictionService.detect_anomalies(current_user.id, db)
    return anomalies

@app.get("/ml/insights")
def get_ml_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive ML-based insights."""
    insights = MLPredictionService.get_spending_insights(current_user.id, db)
    return insights

# CSV Import Routes
@app.post("/expenses/import-csv")
async def import_csv(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Import expenses from CSV file."""
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    # Read file content
    content = await file.read()
    try:
        file_content = content.decode('utf-8')
    except UnicodeDecodeError:
        # Try with different encoding
        try:
            file_content = content.decode('latin-1')
        except:
            raise HTTPException(status_code=400, detail="Unable to decode file. Please ensure it's a valid CSV")
    
    # Parse CSV
    parsed_rows, errors = CSVImportService.parse_csv(file_content)
    
    if not parsed_rows:
        raise HTTPException(
            status_code=400, 
            detail=f"No valid rows found. Errors: {', '.join(errors[:3])}"
        )
    
    # Import expenses
    result = CSVImportService.import_expenses(current_user.id, parsed_rows, db)
    
    return result

@app.post("/expenses/validate-csv")
async def validate_csv(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Validate CSV format and return preview."""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    content = await file.read()
    try:
        file_content = content.decode('utf-8')
    except UnicodeDecodeError:
        try:
            file_content = content.decode('latin-1')
        except:
            raise HTTPException(status_code=400, detail="Unable to decode file")
    
    validation = CSVImportService.validate_csv(file_content)
    return validation


# SMS Webhook Routes
@app.post("/sms/webhook")
async def sms_webhook(
    sms: SMSWebhook,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Webhook endpoint to receive SMS and auto-create expenses.
    Can be called from SMS forwarding apps or services.
    """
    # Parse SMS
    parsed = SMSTransactionParser.parse_sms(sms.message, sms.sender)
    
    if not parsed:
        raise HTTPException(
            status_code=400,
            detail="SMS does not contain a valid transaction"
        )
    
    # Auto-categorize using ML
    category = AICategorizer.predict_category(parsed['note'])
    
    # Check for duplicates (same amount, date, and merchant)
    existing = db.query(Expense).filter(
        Expense.user_id == current_user.id,
        Expense.date == parsed['date'],
        Expense.amount == parsed['amount'],
        Expense.note.contains(parsed['merchant'])
    ).first()
    
    if existing:
        return {
            "status": "duplicate",
            "message": "Transaction already exists",
            "expense_id": existing.id
        }
    
    # Create expense
    new_expense = Expense(
        user_id=current_user.id,
        date=parsed['date'],
        amount=parsed['amount'],
        category=category,
        note=parsed['note']
    )
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    
    return {
        "status": "success",
        "message": "Expense created from SMS",
        "expense": {
            "id": new_expense.id,
            "amount": new_expense.amount,
            "category": new_expense.category,
            "date": new_expense.date.isoformat(),
            "note": new_expense.note,
            "merchant": parsed['merchant']
        },
        "parsed_data": parsed
    }

@app.post("/sms/test-parse")
def test_sms_parse(sms: SMSWebhook):
    """
    Test endpoint to check if SMS can be parsed.
    Does not create expense, just returns parsed data.
    """
    parsed = SMSTransactionParser.parse_sms(sms.message, sms.sender)
    
    if not parsed:
        return {
            "valid": False,
            "message": "SMS does not contain a valid transaction"
        }
    
    # Get suggested category
    category = AICategorizer.predict_category(parsed['note'])
    parsed['suggested_category'] = category
    
    return {
        "valid": True,
        "message": "SMS parsed successfully",
        "parsed_data": parsed
    }


# ==================== NEW ADVANCED FEATURES ====================

from forecasting_service import ForecastingService
from financial_health_service import FinancialHealthService
from anomaly_detection_service import AnomalyDetectionService
from wealth_management_service import AssetService, LiabilityService, NetWorthService, GoalService
from models import Asset, Liability, FinancialGoal

# Pydantic models for new features
class AssetCreate(BaseModel):
    name: str
    value: float
    category: str
    date: date
    note: Optional[str] = None

class AssetUpdate(BaseModel):
    name: str
    value: float
    category: str
    date: date
    note: Optional[str] = None

class LiabilityCreate(BaseModel):
    name: str
    amount: float
    category: str
    interest_rate: float = 0.0
    date: date
    note: Optional[str] = None

class LiabilityUpdate(BaseModel):
    name: str
    amount: float
    category: str
    interest_rate: float
    date: date
    note: Optional[str] = None

class GoalCreate(BaseModel):
    name: str
    target_amount: float
    deadline: date
    category: str

class GoalUpdate(BaseModel):
    name: str
    target_amount: float
    current_amount: float
    deadline: date
    category: str
    status: str


# ==================== FORECASTING ENDPOINTS ====================

@app.get("/forecast/next-month")
def forecast_next_month(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Forecast total spending for next month"""
    return ForecastingService.forecast_next_month(db, current_user.id)

@app.get("/forecast/by-category")
def forecast_by_category(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Forecast spending by category for next month"""
    return ForecastingService.forecast_by_category(db, current_user.id)

@app.get("/forecast/trend")
def get_spending_trend(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get spending trend analysis"""
    return ForecastingService.get_spending_trend(db, current_user.id)


# ==================== FINANCIAL HEALTH ENDPOINTS ====================

@app.get("/health/score")
def get_financial_health_score(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive financial health score (0-100)"""
    return FinancialHealthService.calculate_health_score(db, current_user.id)


# ==================== ANOMALY DETECTION ENDPOINTS ====================

@app.get("/anomalies/all")
def get_all_anomalies(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all detected anomalies"""
    return AnomalyDetectionService.get_all_anomalies(db, current_user.id)

@app.get("/anomalies/transactions")
def get_transaction_anomalies(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get unusual transactions"""
    return AnomalyDetectionService.detect_amount_anomalies(db, current_user.id)

@app.get("/insights/behavioral")
def get_behavioral_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get behavioral spending insights"""
    return {"insights": AnomalyDetectionService.get_behavioral_insights(db, current_user.id)}


# ==================== NET WORTH DASHBOARD ENDPOINTS ====================

@app.get("/networth/dashboard")
def get_networth_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive net worth dashboard"""
    return NetWorthService.get_net_worth_dashboard(db, current_user.id)


# ==================== ASSET ENDPOINTS ====================

@app.get("/assets")
def get_assets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all assets"""
    assets = AssetService.get_all_assets(db, current_user.id)
    return [
        {
            "id": a.id,
            "name": a.name,
            "value": a.value,
            "category": a.category,
            "date": a.date.isoformat(),
            "note": a.note
        }
        for a in assets
    ]

@app.post("/assets")
def create_asset(
    asset: AssetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new asset"""
    new_asset = AssetService.create_asset(
        db, asset.name, asset.value, asset.category, asset.date, asset.note, current_user.id
    )
    return {
        "id": new_asset.id,
        "name": new_asset.name,
        "value": new_asset.value,
        "category": new_asset.category,
        "date": new_asset.date.isoformat(),
        "note": new_asset.note
    }

@app.put("/assets/{asset_id}")
def update_asset(
    asset_id: int,
    asset: AssetUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update asset"""
    updated = AssetService.update_asset(
        db, asset_id, asset.name, asset.value, asset.category, asset.date, asset.note, current_user.id
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Asset not found")
    return {
        "id": updated.id,
        "name": updated.name,
        "value": updated.value,
        "category": updated.category,
        "date": updated.date.isoformat(),
        "note": updated.note
    }

@app.delete("/assets/{asset_id}")
def delete_asset(
    asset_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete asset"""
    success = AssetService.delete_asset(db, asset_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Asset not found")
    return {"message": "Asset deleted"}


# ==================== LIABILITY ENDPOINTS ====================

@app.get("/liabilities")
def get_liabilities(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all liabilities"""
    liabilities = LiabilityService.get_all_liabilities(db, current_user.id)
    return [
        {
            "id": l.id,
            "name": l.name,
            "amount": l.amount,
            "category": l.category,
            "interest_rate": l.interest_rate,
            "date": l.date.isoformat(),
            "note": l.note
        }
        for l in liabilities
    ]

@app.post("/liabilities")
def create_liability(
    liability: LiabilityCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new liability"""
    new_liability = LiabilityService.create_liability(
        db, liability.name, liability.amount, liability.category,
        liability.interest_rate, liability.date, liability.note, current_user.id
    )
    return {
        "id": new_liability.id,
        "name": new_liability.name,
        "amount": new_liability.amount,
        "category": new_liability.category,
        "interest_rate": new_liability.interest_rate,
        "date": new_liability.date.isoformat(),
        "note": new_liability.note
    }

@app.put("/liabilities/{liability_id}")
def update_liability(
    liability_id: int,
    liability: LiabilityUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update liability"""
    updated = LiabilityService.update_liability(
        db, liability_id, liability.name, liability.amount, liability.category,
        liability.interest_rate, liability.date, liability.note, current_user.id
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Liability not found")
    return {
        "id": updated.id,
        "name": updated.name,
        "amount": updated.amount,
        "category": updated.category,
        "interest_rate": updated.interest_rate,
        "date": updated.date.isoformat(),
        "note": updated.note
    }

@app.delete("/liabilities/{liability_id}")
def delete_liability(
    liability_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete liability"""
    success = LiabilityService.delete_liability(db, liability_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Liability not found")
    return {"message": "Liability deleted"}


# ==================== FINANCIAL GOAL ENDPOINTS ====================

@app.get("/goals")
def get_goals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all financial goals with progress"""
    return {"goals": GoalService.get_all_goals_with_progress(db, current_user.id)}

@app.post("/goals")
def create_goal(
    goal: GoalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new financial goal"""
    new_goal = GoalService.create_goal(
        db, goal.name, goal.target_amount, goal.deadline, goal.category, current_user.id
    )
    return GoalService.get_goal_progress(db, new_goal.id, current_user.id)

@app.put("/goals/{goal_id}")
def update_goal(
    goal_id: int,
    goal: GoalUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update financial goal"""
    updated = GoalService.update_goal(
        db, goal_id, goal.name, goal.target_amount, goal.current_amount,
        goal.deadline, goal.category, goal.status, current_user.id
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Goal not found")
    return GoalService.get_goal_progress(db, goal_id, current_user.id)

@app.delete("/goals/{goal_id}")
def delete_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete financial goal"""
    success = GoalService.delete_goal(db, goal_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Goal not found")
    return {"message": "Goal deleted"}

@app.get("/goals/{goal_id}/progress")
def get_goal_progress(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed progress for a specific goal"""
    progress = GoalService.get_goal_progress(db, goal_id, current_user.id)
    if not progress:
        raise HTTPException(status_code=404, detail="Goal not found")
    return progress


# ==================== SAAS FEATURES ====================

from group_service import GroupService
from split_service import SplitService, SplitType
from subscription_service import SubscriptionService, get_subscription_or_create
from admin_service import AdminService
from payment_service import PaymentService
from models import GroupRole, InviteStatus

# Pydantic models for SaaS features
class GroupCreate(BaseModel):
    name: str
    description: Optional[str] = None

class GroupInviteCreate(BaseModel):
    email: str

class InviteAccept(BaseModel):
    token: str

class SplitCreate(BaseModel):
    split_type: str  # equal, percentage, custom
    splits: list  # [{"user_id": 1, "amount": 100} or {"user_id": 1, "percentage": 50}]

class MemberRoleUpdate(BaseModel):
    role: str  # owner, admin, member

class SubscriptionUpgrade(BaseModel):
    plan_type: str = "pro"

class WebhookPayload(BaseModel):
    type: str
    data: dict


# ==================== GROUP ENDPOINTS ====================

@app.post("/groups/create")
def create_group(
    group: GroupCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new finance group (PRO feature)"""
    # Check PRO access
    SubscriptionService.require_pro(db, current_user.id, "group finance")
    
    new_group = GroupService.create_group(db, group.name, group.description, current_user.id)
    return {
        "id": new_group.id,
        "name": new_group.name,
        "description": new_group.description,
        "created_at": new_group.created_at.isoformat()
    }

@app.get("/groups/list")
def list_groups(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all groups user is member of"""
    groups = GroupService.get_user_groups(db, current_user.id)
    return {
        "groups": [
            {
                "id": g.id,
                "name": g.name,
                "description": g.description,
                "created_at": g.created_at.isoformat()
            }
            for g in groups
        ]
    }

@app.get("/groups/{group_id}")
def get_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get group details"""
    group = GroupService.get_group_details(db, group_id, current_user.id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found or access denied")
    return group

@app.post("/groups/{group_id}/invite")
def invite_to_group(
    group_id: int,
    invite: GroupInviteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Invite member to group"""
    try:
        invitation = GroupService.invite_member(db, group_id, invite.email, current_user.id)
        return {
            "id": invitation.id,
            "email": invitation.email,
            "token": invitation.token,
            "expires_at": invitation.expires_at.isoformat(),
            "invite_link": f"/groups/join?token={invitation.token}"
        }
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

@app.post("/groups/join")
def join_group(
    invite: InviteAccept,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Accept group invitation"""
    try:
        member = GroupService.accept_invite(db, invite.token, current_user.id)
        return {
            "message": "Successfully joined group",
            "group_id": member.group_id,
            "role": member.role.value
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/groups/{group_id}/expenses")
def get_group_expenses(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all expenses for a group"""
    try:
        expenses = GroupService.get_group_expenses(db, group_id, current_user.id)
        return {"expenses": expenses}
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

@app.delete("/groups/{group_id}")
def delete_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete group (owner only)"""
    try:
        success = GroupService.delete_group(db, group_id, current_user.id)
        if not success:
            raise HTTPException(status_code=404, detail="Group not found")
        return {"message": "Group deleted successfully"}
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

@app.delete("/groups/{group_id}/members/{member_id}")
def remove_member(
    group_id: int,
    member_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove member from group"""
    try:
        success = GroupService.remove_member(db, group_id, member_id, current_user.id)
        if not success:
            raise HTTPException(status_code=404, detail="Member not found")
        return {"message": "Member removed successfully"}
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

@app.put("/groups/{group_id}/members/{member_id}/role")
def update_member_role(
    group_id: int,
    member_id: int,
    role_update: MemberRoleUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update member role"""
    try:
        role = GroupRole(role_update.role)
        member = GroupService.update_member_role(db, group_id, member_id, role, current_user.id)
        return {
            "message": "Role updated successfully",
            "member_id": member.id,
            "new_role": member.role.value
        }
    except (PermissionError, ValueError) as e:
        raise HTTPException(status_code=403, detail=str(e))


# ==================== SPLIT ENDPOINTS ====================

@app.post("/expenses/{expense_id}/split")
def split_expense(
    expense_id: int,
    split_data: SplitCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create expense split"""
    try:
        split_type = SplitType(split_data.split_type)
        splits = SplitService.create_split(
            db, expense_id, split_type, split_data.splits, current_user.id
        )
        return {
            "message": "Expense split created",
            "splits": [
                {
                    "id": s.id,
                    "user_id": s.user_id,
                    "amount_owed": s.amount_owed,
                    "is_settled": s.is_settled
                }
                for s in splits
            ]
        }
    except (ValueError, PermissionError) as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/splits/{split_id}/settle")
def settle_split(
    split_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark split as settled"""
    try:
        split = SplitService.settle_split(db, split_id, current_user.id)
        return {
            "message": "Split settled successfully",
            "split_id": split.id,
            "settled_at": split.settled_at.isoformat()
        }
    except (ValueError, PermissionError) as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/groups/{group_id}/balances")
def get_group_balances(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all balances in a group"""
    try:
        balances = SplitService.get_group_balances(db, group_id, current_user.id)
        return {"balances": balances}
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

@app.get("/splits/my-splits")
def get_my_splits(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all splits for current user"""
    splits = SplitService.get_user_splits(db, current_user.id)
    return splits


# ==================== SUBSCRIPTION ENDPOINTS ====================

@app.post("/subscribe")
def subscribe_to_pro(
    upgrade: SubscriptionUpgrade,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upgrade to PRO plan"""
    # Create payment checkout session
    checkout = PaymentService.create_checkout_session(db, current_user.id, upgrade.plan_type)
    return checkout

@app.get("/subscription/status")
def get_subscription_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get subscription status"""
    status = SubscriptionService.get_subscription_status(db, current_user.id)
    return status

@app.post("/subscription/cancel")
def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel PRO subscription"""
    try:
        result = PaymentService.cancel_subscription_external(db, current_user.id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/subscription/payment-methods")
def get_payment_methods():
    """Get available payment methods"""
    return PaymentService.get_payment_methods()

@app.post("/webhook/payment")
async def payment_webhook(
    payload: WebhookPayload,
    signature: str = "",
    db: Session = Depends(get_db)
):
    """Handle payment provider webhooks"""
    result = PaymentService.handle_webhook(db, payload.dict(), signature)
    return result


# ==================== ADMIN ENDPOINTS ====================

def require_admin(current_user: User = Depends(get_current_user)):
    """Middleware to require admin access"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

@app.get("/admin/users")
def get_all_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all users (admin only)"""
    users = AdminService.get_all_users(db, skip, limit)
    return {"users": users, "total": len(users)}

@app.get("/admin/subscriptions")
def get_subscription_stats(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get subscription statistics (admin only)"""
    stats = AdminService.get_subscription_stats(db)
    return stats

@app.get("/admin/revenue")
def get_revenue_stats(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get revenue statistics (admin only)"""
    stats = AdminService.get_revenue_stats(db)
    return stats

@app.get("/admin/analytics")
def get_system_analytics(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get comprehensive system analytics (admin only)"""
    analytics = AdminService.get_system_analytics(db)
    return analytics

@app.get("/admin/stats")
def get_admin_stats(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get quick admin dashboard stats"""
    subscription_stats = AdminService.get_subscription_stats(db)
    revenue_stats = AdminService.get_revenue_stats(db)
    feature_usage = AdminService.get_feature_usage(db)
    
    return {
        "total_users": subscription_stats["total_users"],
        "pro_users": subscription_stats["pro_users"],
        "monthly_revenue": revenue_stats["monthly_revenue"],
        "total_expenses": feature_usage["total_expenses"],
        "total_groups": feature_usage["total_groups"]
    }
