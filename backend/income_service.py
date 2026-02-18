"""
Income Service
Handles income tracking and management
"""
from sqlalchemy.orm import Session
from models import Income
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class IncomeService:
    """Service for managing income entries"""
    
    # Income categories
    INCOME_CATEGORIES = [
        "Salary",
        "Freelance",
        "Investment",
        "Business",
        "Gift",
        "Refund",
        "Cashback",
        "Bonus",
        "Other"
    ]
    
    @classmethod
    def get_categories(cls):
        """Get list of income categories"""
        return cls.INCOME_CATEGORIES
    
    @classmethod
    def get_all_incomes(cls, db: Session, user_id: int):
        """Get all incomes for a user"""
        return db.query(Income).filter(Income.user_id == user_id).order_by(Income.date.desc()).all()
    
    @classmethod
    def create_income(cls, db: Session, amount: float, category: str, date, note: str, user_id: int):
        """Create a new income entry"""
        income = Income(
            amount=amount,
            category=category,
            date=date,
            note=note,
            user_id=user_id
        )
        db.add(income)
        db.commit()
        db.refresh(income)
        return income
    
    @classmethod
    def update_income(cls, db: Session, income_id: int, amount: float, category: str, date, note: str, user_id: int):
        """Update an existing income entry"""
        income = db.query(Income).filter(Income.id == income_id, Income.user_id == user_id).first()
        if income:
            income.amount = amount
            income.category = category
            income.date = date
            income.note = note
            db.commit()
            db.refresh(income)
        return income
    
    @classmethod
    def delete_income(cls, db: Session, income_id: int, user_id: int):
        """Delete an income entry"""
        income = db.query(Income).filter(Income.id == income_id, Income.user_id == user_id).first()
        if income:
            db.delete(income)
            db.commit()
            return True
        return False
    
    @classmethod
    def get_total_income(cls, db: Session, user_id: int, start_date=None, end_date=None):
        """Get total income for a period"""
        query = db.query(Income).filter(Income.user_id == user_id)
        
        if start_date:
            query = query.filter(Income.date >= start_date)
        if end_date:
            query = query.filter(Income.date <= end_date)
        
        incomes = query.all()
        return sum(income.amount for income in incomes)
    
    @classmethod
    def get_income_by_category(cls, db: Session, user_id: int, start_date=None, end_date=None):
        """Get income breakdown by category"""
        query = db.query(Income).filter(Income.user_id == user_id)
        
        if start_date:
            query = query.filter(Income.date >= start_date)
        if end_date:
            query = query.filter(Income.date <= end_date)
        
        incomes = query.all()
        
        category_totals = {}
        for income in incomes:
            if income.category in category_totals:
                category_totals[income.category] += income.amount
            else:
                category_totals[income.category] = income.amount
        
        return [
            {"category": cat, "amount": amt}
            for cat, amt in category_totals.items()
        ]
