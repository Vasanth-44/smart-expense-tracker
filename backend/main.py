from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import date, timedelta
from typing import Optional

from database import engine, get_db, Base
from models import User, Expense, Budget
from services import ExpenseService, BudgetService, AnalyticsService
from ai_categorizer import AICategorizer
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
