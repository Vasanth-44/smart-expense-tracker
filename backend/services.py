from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from models import Expense, Budget
from ai_categorizer import AICategorizer

class ExpenseService:
    
    @staticmethod
    def get_all_expenses(db: Session, user_id: int):
        return db.query(Expense).filter(Expense.user_id == user_id).order_by(Expense.date.desc()).all()
    
    @staticmethod
    def create_expense(db: Session, amount: float, category: str, date, note: str, user_id: int):
        expense = Expense(amount=amount, category=category, date=date, note=note, user_id=user_id)
        db.add(expense)
        db.commit()
        db.refresh(expense)
        return expense
    
    @staticmethod
    def update_expense(db: Session, expense_id: int, amount: float, category: str, date, note: str, user_id: int):
        expense = db.query(Expense).filter(Expense.id == expense_id, Expense.user_id == user_id).first()
        if expense:
            expense.amount = amount
            expense.category = category
            expense.date = date
            expense.note = note
            db.commit()
            db.refresh(expense)
        return expense
    
    @staticmethod
    def delete_expense(db: Session, expense_id: int, user_id: int):
        expense = db.query(Expense).filter(Expense.id == expense_id, Expense.user_id == user_id).first()
        if expense:
            db.delete(expense)
            db.commit()
            return True
        return False

class BudgetService:
    
    @staticmethod
    def get_all_budgets(db: Session, user_id: int):
        return db.query(Budget).filter(Budget.user_id == user_id).all()
    
    @staticmethod
    def set_budget(db: Session, category: str, amount: float, user_id: int):
        budget = db.query(Budget).filter(Budget.category == category, Budget.user_id == user_id).first()
        if budget:
            budget.amount = amount
        else:
            budget = Budget(category=category, amount=amount, user_id=user_id)
            db.add(budget)
        db.commit()
        db.refresh(budget)
        return budget

class AnalyticsService:
    
    @staticmethod
    def get_summary(db: Session, user_id: int):
        """Get dashboard summary with category breakdown and monthly trend."""
        now = datetime.now()
        current_month_start = now.replace(day=1)
        
        # Category-wise spending for current month
        category_spending = db.query(
            Expense.category,
            func.sum(Expense.amount).label('total')
        ).filter(
            Expense.user_id == user_id,
            Expense.date >= current_month_start
        ).group_by(Expense.category).all()
        
        category_data = [{"category": cat, "amount": float(total)} for cat, total in category_spending]
        
        # Monthly trend for last 6 months
        six_months_ago = current_month_start - relativedelta(months=5)
        monthly_spending = db.query(
            extract('year', Expense.date).label('year'),
            extract('month', Expense.date).label('month'),
            func.sum(Expense.amount).label('total')
        ).filter(
            Expense.user_id == user_id,
            Expense.date >= six_months_ago
        ).group_by('year', 'month').order_by('year', 'month').all()
        
        monthly_data = []
        for year, month, total in monthly_spending:
            month_name = datetime(int(year), int(month), 1).strftime('%b %Y')
            monthly_data.append({"month": month_name, "amount": float(total)})
        
        # Total spending current month
        total_current_month = sum(item['amount'] for item in category_data)
        
        # Budget alerts
        budgets = db.query(Budget).filter(Budget.user_id == user_id).all()
        budget_alerts = []
        for budget in budgets:
            spent = next((item['amount'] for item in category_data if item['category'] == budget.category), 0)
            if spent > budget.amount:
                budget_alerts.append({
                    "category": budget.category,
                    "budget": budget.amount,
                    "spent": spent,
                    "exceeded": spent - budget.amount
                })
        
        return {
            "total_current_month": total_current_month,
            "category_breakdown": category_data,
            "monthly_trend": monthly_data,
            "budget_alerts": budget_alerts
        }
    
    @staticmethod
    def get_insights(db: Session, user_id: int):
        """Generate AI-powered spending insights."""
        now = datetime.now()
        current_month_start = now.replace(day=1)
        last_month_start = (current_month_start - relativedelta(months=1))
        last_month_end = current_month_start - timedelta(days=1)
        
        # Current month spending by category
        current_spending = db.query(
            Expense.category,
            func.sum(Expense.amount).label('total')
        ).filter(
            Expense.user_id == user_id,
            Expense.date >= current_month_start
        ).group_by(Expense.category).all()
        
        # Last month spending by category
        last_spending = db.query(
            Expense.category,
            func.sum(Expense.amount).label('total')
        ).filter(
            Expense.user_id == user_id,
            Expense.date >= last_month_start,
            Expense.date <= last_month_end
        ).group_by(Expense.category).all()
        
        current_dict = {cat: float(total) for cat, total in current_spending}
        last_dict = {cat: float(total) for cat, total in last_spending}
        
        insights = []
        
        # Find highest spending category
        if current_dict:
            highest_cat = max(current_dict, key=current_dict.get)
            highest_amount = current_dict[highest_cat]
            insights.append({
                "type": "highest_spending",
                "message": f"Your highest spending is on {highest_cat} (₹{highest_amount:.0f} this month)"
            })
        
        # Compare with last month
        for category, current_amt in current_dict.items():
            last_amt = last_dict.get(category, 0)
            if last_amt > 0:
                change_pct = ((current_amt - last_amt) / last_amt) * 100
                if change_pct > 20:
                    potential_saving = current_amt * 0.2
                    insights.append({
                        "type": "increase_alert",
                        "message": f"You spent {change_pct:.0f}% more on {category}. Reducing expenses could save ₹{potential_saving:.0f}."
                    })
        
        # Budget-based insights
        budgets = db.query(Budget).filter(Budget.user_id == user_id).all()
        for budget in budgets:
            spent = current_dict.get(budget.category, 0)
            if spent > budget.amount:
                insights.append({
                    "type": "budget_exceeded",
                    "message": f"⚠️ {budget.category} budget exceeded by ₹{(spent - budget.amount):.0f}"
                })
        
        if not insights:
            insights.append({
                "type": "positive",
                "message": "Great job! Your spending is under control this month."
            })
        
        return insights
