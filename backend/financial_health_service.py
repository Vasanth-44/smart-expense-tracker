"""
Financial Health Score Calculator
Calculates a 0-100 score based on multiple financial metrics
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from models import Expense, Income, Budget, Asset, Liability
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import Dict, List
import numpy as np


class FinancialHealthService:
    """Calculate comprehensive financial health score"""
    
    @staticmethod
    def calculate_savings_rate(db: Session, user_id: int, months: int = 3) -> float:
        """Calculate average savings rate over past N months"""
        end_date = datetime.now()
        start_date = end_date - relativedelta(months=months)
        
        # Get total income
        total_income = db.query(func.sum(Income.amount)).filter(
            Income.user_id == user_id,
            Income.date >= start_date.date()
        ).scalar() or 0
        
        # Get total expenses
        total_expenses = db.query(func.sum(Expense.amount)).filter(
            Expense.user_id == user_id,
            Expense.date >= start_date.date()
        ).scalar() or 0
        
        if total_income == 0:
            return 0
        
        savings_rate = ((total_income - total_expenses) / total_income) * 100
        return max(0, min(100, savings_rate))  # Clamp between 0-100
    
    @staticmethod
    def calculate_budget_adherence(db: Session, user_id: int) -> float:
        """Calculate how well user sticks to budgets"""
        # Get current month
        now = datetime.now()
        month_start = now.replace(day=1)
        
        # Get all budgets
        budgets = db.query(Budget).filter(Budget.user_id == user_id).all()
        
        if not budgets:
            return 50  # Neutral score if no budgets set
        
        adherence_scores = []
        
        for budget in budgets:
            # Get spending in this category
            spent = db.query(func.sum(Expense.amount)).filter(
                Expense.user_id == user_id,
                Expense.category == budget.category,
                Expense.date >= month_start.date()
            ).scalar() or 0
            
            if budget.amount == 0:
                continue
            
            # Calculate adherence (100% if under budget, decreases if over)
            adherence = min(100, (1 - (spent / budget.amount - 1)) * 100) if spent > budget.amount else 100
            adherence_scores.append(max(0, adherence))
        
        return sum(adherence_scores) / len(adherence_scores) if adherence_scores else 50
    
    @staticmethod
    def calculate_expense_stability(db: Session, user_id: int, months: int = 6) -> float:
        """Calculate expense stability (lower variance = higher score)"""
        end_date = datetime.now()
        start_date = end_date - relativedelta(months=months)
        
        # Get monthly totals
        monthly_data = db.query(
            func.strftime('%Y-%m', Expense.date).label('month'),
            func.sum(Expense.amount).label('total')
        ).filter(
            Expense.user_id == user_id,
            Expense.date >= start_date.date()
        ).group_by('month').all()
        
        if len(monthly_data) < 2:
            return 50  # Neutral score
        
        values = [float(m[1]) for m in monthly_data]
        mean_val = np.mean(values)
        
        if mean_val == 0:
            return 50
        
        # Calculate coefficient of variation
        cv = np.std(values) / mean_val
        
        # Convert to score (lower CV = higher score)
        # CV of 0.2 or less = 100, CV of 0.5 or more = 0
        stability_score = max(0, min(100, (0.5 - cv) / 0.3 * 100))
        
        return stability_score
    
    @staticmethod
    def calculate_debt_ratio(db: Session, user_id: int) -> float:
        """Calculate debt-to-asset ratio (lower is better)"""
        # Get total assets
        total_assets = db.query(func.sum(Asset.value)).filter(
            Asset.user_id == user_id
        ).scalar() or 0
        
        # Get total liabilities
        total_liabilities = db.query(func.sum(Liability.amount)).filter(
            Liability.user_id == user_id
        ).scalar() or 0
        
        if total_assets == 0:
            return 50 if total_liabilities == 0 else 0
        
        debt_ratio = total_liabilities / total_assets
        
        # Convert to score (0 debt = 100, 50% debt = 50, 100%+ debt = 0)
        score = max(0, min(100, (1 - debt_ratio) * 100))
        
        return score
    
    @staticmethod
    def calculate_spending_growth(db: Session, user_id: int) -> float:
        """Calculate spending growth trend (negative growth = higher score)"""
        end_date = datetime.now()
        start_date = end_date - relativedelta(months=6)
        
        monthly_data = db.query(
            func.strftime('%Y-%m', Expense.date).label('month'),
            func.sum(Expense.amount).label('total')
        ).filter(
            Expense.user_id == user_id,
            Expense.date >= start_date.date()
        ).group_by('month').order_by('month').all()
        
        if len(monthly_data) < 2:
            return 50
        
        values = [float(m[1]) for m in monthly_data]
        
        # Calculate growth rate
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        
        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)
        
        if first_avg == 0:
            return 50
        
        growth_rate = ((second_avg - first_avg) / first_avg) * 100
        
        # Convert to score (negative growth = good, positive = bad)
        # -10% or better = 100, 0% = 50, +20% or worse = 0
        if growth_rate <= -10:
            score = 100
        elif growth_rate >= 20:
            score = 0
        else:
            score = 50 - (growth_rate / 20 * 50)
        
        return max(0, min(100, score))
    
    @staticmethod
    def calculate_health_score(db: Session, user_id: int) -> Dict:
        """
        Calculate comprehensive financial health score (0-100)
        """
        # Calculate individual metrics
        savings_rate = FinancialHealthService.calculate_savings_rate(db, user_id)
        budget_adherence = FinancialHealthService.calculate_budget_adherence(db, user_id)
        expense_stability = FinancialHealthService.calculate_expense_stability(db, user_id)
        debt_ratio = FinancialHealthService.calculate_debt_ratio(db, user_id)
        spending_growth = FinancialHealthService.calculate_spending_growth(db, user_id)
        
        # Weighted average
        weights = {
            'savings_rate': 0.30,
            'budget_adherence': 0.25,
            'expense_stability': 0.20,
            'debt_ratio': 0.15,
            'spending_growth': 0.10
        }
        
        total_score = (
            savings_rate * weights['savings_rate'] +
            budget_adherence * weights['budget_adherence'] +
            expense_stability * weights['expense_stability'] +
            debt_ratio * weights['debt_ratio'] +
            spending_growth * weights['spending_growth']
        )
        
        # Determine rating
        if total_score >= 80:
            rating = "Excellent"
            color = "green"
        elif total_score >= 70:
            rating = "Good"
            color = "green"
        elif total_score >= 50:
            rating = "Fair"
            color = "yellow"
        elif total_score >= 30:
            rating = "Poor"
            color = "orange"
        else:
            rating = "Critical"
            color = "red"
        
        # Generate insights
        insights = []
        
        if savings_rate < 20:
            insights.append("💡 Try to increase your savings rate to at least 20%")
        elif savings_rate >= 30:
            insights.append("✅ Great job maintaining a healthy savings rate!")
        
        if budget_adherence < 70:
            insights.append("💡 Focus on staying within your budget limits")
        elif budget_adherence >= 90:
            insights.append("✅ Excellent budget discipline!")
        
        if expense_stability < 50:
            insights.append("💡 Your expenses vary significantly. Try to maintain consistent spending")
        
        if debt_ratio < 50:
            insights.append("⚠️ Consider reducing your debt-to-asset ratio")
        
        if spending_growth > 60:
            insights.append("⚠️ Your spending is increasing. Review your expenses")
        
        return {
            "score": round(total_score, 1),
            "rating": rating,
            "color": color,
            "breakdown": {
                "savings_rate": {
                    "score": round(savings_rate, 1),
                    "weight": weights['savings_rate'] * 100,
                    "label": "Savings Rate"
                },
                "budget_adherence": {
                    "score": round(budget_adherence, 1),
                    "weight": weights['budget_adherence'] * 100,
                    "label": "Budget Adherence"
                },
                "expense_stability": {
                    "score": round(expense_stability, 1),
                    "weight": weights['expense_stability'] * 100,
                    "label": "Expense Stability"
                },
                "debt_ratio": {
                    "score": round(debt_ratio, 1),
                    "weight": weights['debt_ratio'] * 100,
                    "label": "Debt Management"
                },
                "spending_growth": {
                    "score": round(spending_growth, 1),
                    "weight": weights['spending_growth'] * 100,
                    "label": "Spending Control"
                }
            },
            "insights": insights
        }
