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
