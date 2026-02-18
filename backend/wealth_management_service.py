"""
Wealth Management Service
Handles Assets, Liabilities, Net Worth, and Financial Goals
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from models import Asset, Liability, FinancialGoal, Income, Expense
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from typing import Dict, List, Optional


class AssetService:
    """Manage user assets"""
    
    @staticmethod
    def create_asset(db: Session, name: str, value: float, category: str, 
                    asset_date: date, note: Optional[str], user_id: int) -> Asset:
        asset = Asset(
            name=name,
            value=value,
            category=category,
            date=asset_date,
            note=note,
            user_id=user_id
        )
        db.add(asset)
        db.commit()
        db.refresh(asset)
        return asset
    
    @staticmethod
    def get_all_assets(db: Session, user_id: int) -> List[Asset]:
        return db.query(Asset).filter(Asset.user_id == user_id).order_by(Asset.date.desc()).all()
    
    @staticmethod
    def update_asset(db: Session, asset_id: int, name: str, value: float, 
                    category: str, asset_date: date, note: Optional[str], user_id: int) -> Optional[Asset]:
        asset = db.query(Asset).filter(Asset.id == asset_id, Asset.user_id == user_id).first()
        if asset:
            asset.name = name
            asset.value = value
            asset.category = category
            asset.date = asset_date
            asset.note = note
            db.commit()
            db.refresh(asset)
        return asset
    
    @staticmethod
    def delete_asset(db: Session, asset_id: int, user_id: int) -> bool:
        asset = db.query(Asset).filter(Asset.id == asset_id, Asset.user_id == user_id).first()
        if asset:
            db.delete(asset)
            db.commit()
            return True
        return False
    
    @staticmethod
    def get_total_assets(db: Session, user_id: int) -> float:
        total = db.query(func.sum(Asset.value)).filter(Asset.user_id == user_id).scalar()
        return float(total) if total else 0.0
    
    @staticmethod
    def get_assets_by_category(db: Session, user_id: int) -> Dict:
        assets = db.query(
            Asset.category,
            func.sum(Asset.value).label('total')
        ).filter(Asset.user_id == user_id).group_by(Asset.category).all()
        
        return {category: float(total) for category, total in assets}


class LiabilityService:
    """Manage user liabilities"""
    
    @staticmethod
    def create_liability(db: Session, name: str, amount: float, category: str,
                        interest_rate: float, liability_date: date, 
                        note: Optional[str], user_id: int) -> Liability:
        liability = Liability(
            name=name,
            amount=amount,
            category=category,
            interest_rate=interest_rate,
            date=liability_date,
            note=note,
            user_id=user_id
        )
        db.add(liability)
        db.commit()
        db.refresh(liability)
        return liability
    
    @staticmethod
    def get_all_liabilities(db: Session, user_id: int) -> List[Liability]:
        return db.query(Liability).filter(Liability.user_id == user_id).order_by(Liability.date.desc()).all()
    
    @staticmethod
    def update_liability(db: Session, liability_id: int, name: str, amount: float,
                        category: str, interest_rate: float, liability_date: date,
                        note: Optional[str], user_id: int) -> Optional[Liability]:
        liability = db.query(Liability).filter(
            Liability.id == liability_id, 
            Liability.user_id == user_id
        ).first()
        if liability:
            liability.name = name
            liability.amount = amount
            liability.category = category
            liability.interest_rate = interest_rate
            liability.date = liability_date
            liability.note = note
            db.commit()
            db.refresh(liability)
        return liability
    
    @staticmethod
    def delete_liability(db: Session, liability_id: int, user_id: int) -> bool:
        liability = db.query(Liability).filter(
            Liability.id == liability_id,
            Liability.user_id == user_id
        ).first()
        if liability:
            db.delete(liability)
            db.commit()
            return True
        return False
    
    @staticmethod
    def get_total_liabilities(db: Session, user_id: int) -> float:
        total = db.query(func.sum(Liability.amount)).filter(Liability.user_id == user_id).scalar()
        return float(total) if total else 0.0
    
    @staticmethod
    def get_liabilities_by_category(db: Session, user_id: int) -> Dict:
        liabilities = db.query(
            Liability.category,
            func.sum(Liability.amount).label('total')
        ).filter(Liability.user_id == user_id).group_by(Liability.category).all()
        
        return {category: float(total) for category, total in liabilities}


class NetWorthService:
    """Calculate and track net worth"""
    
    @staticmethod
    def get_net_worth_dashboard(db: Session, user_id: int) -> Dict:
        """Get comprehensive net worth dashboard"""
        # Get totals
        total_assets = AssetService.get_total_assets(db, user_id)
        total_liabilities = LiabilityService.get_total_liabilities(db, user_id)
        net_worth = total_assets - total_liabilities
        
        # Get current month income and expenses
        now = datetime.now()
        month_start = now.replace(day=1)
        
        monthly_income = db.query(func.sum(Income.amount)).filter(
            Income.user_id == user_id,
            Income.date >= month_start.date()
        ).scalar() or 0
        
        monthly_expenses = db.query(func.sum(Expense.amount)).filter(
            Expense.user_id == user_id,
            Expense.date >= month_start.date()
        ).scalar() or 0
        
        # Calculate savings rate
        savings_rate = 0
        if monthly_income > 0:
            savings_rate = ((monthly_income - monthly_expenses) / monthly_income) * 100
        
        # Get previous month for comparison
        last_month_start = month_start - relativedelta(months=1)
        last_month_end = month_start - timedelta(days=1)
        
        last_month_income = db.query(func.sum(Income.amount)).filter(
            Income.user_id == user_id,
            Income.date >= last_month_start.date(),
            Income.date <= last_month_end.date()
        ).scalar() or 0
        
        last_month_expenses = db.query(func.sum(Expense.amount)).filter(
            Expense.user_id == user_id,
            Expense.date >= last_month_start.date(),
            Expense.date <= last_month_end.date()
        ).scalar() or 0
        
        last_month_net = last_month_income - last_month_expenses
        current_month_net = monthly_income - monthly_expenses
        
        # Calculate monthly growth
        monthly_growth = 0
        if last_month_net != 0:
            monthly_growth = ((current_month_net - last_month_net) / abs(last_month_net)) * 100
        
        # Get breakdowns
        assets_by_category = AssetService.get_assets_by_category(db, user_id)
        liabilities_by_category = LiabilityService.get_liabilities_by_category(db, user_id)
        
        return {
            "net_worth": round(net_worth, 2),
            "total_assets": round(total_assets, 2),
            "total_liabilities": round(total_liabilities, 2),
            "monthly_income": round(monthly_income, 2),
            "monthly_expenses": round(monthly_expenses, 2),
            "monthly_net": round(current_month_net, 2),
            "savings_rate": round(savings_rate, 2),
            "monthly_growth": round(monthly_growth, 2),
            "growth_direction": "up" if monthly_growth > 0 else "down",
            "assets_breakdown": {k: round(v, 2) for k, v in assets_by_category.items()},
            "liabilities_breakdown": {k: round(v, 2) for k, v in liabilities_by_category.items()},
            "month": now.strftime('%B %Y')
        }


class GoalService:
    """Manage financial goals"""
    
    @staticmethod
    def create_goal(db: Session, name: str, target_amount: float, deadline: date,
                   category: str, user_id: int) -> FinancialGoal:
        goal = FinancialGoal(
            name=name,
            target_amount=target_amount,
            current_amount=0.0,
            deadline=deadline,
            category=category,
            status="active",
            created_date=datetime.now().date(),
            user_id=user_id
        )
        db.add(goal)
        db.commit()
        db.refresh(goal)
        return goal
    
    @staticmethod
    def get_all_goals(db: Session, user_id: int) -> List[FinancialGoal]:
        return db.query(FinancialGoal).filter(
            FinancialGoal.user_id == user_id
        ).order_by(FinancialGoal.deadline).all()
    
    @staticmethod
    def update_goal(db: Session, goal_id: int, name: str, target_amount: float,
                   current_amount: float, deadline: date, category: str,
                   status: str, user_id: int) -> Optional[FinancialGoal]:
        goal = db.query(FinancialGoal).filter(
            FinancialGoal.id == goal_id,
            FinancialGoal.user_id == user_id
        ).first()
        if goal:
            goal.name = name
            goal.target_amount = target_amount
            goal.current_amount = current_amount
            goal.deadline = deadline
            goal.category = category
            goal.status = status
            db.commit()
            db.refresh(goal)
        return goal
    
    @staticmethod
    def delete_goal(db: Session, goal_id: int, user_id: int) -> bool:
        goal = db.query(FinancialGoal).filter(
            FinancialGoal.id == goal_id,
            FinancialGoal.user_id == user_id
        ).first()
        if goal:
            db.delete(goal)
            db.commit()
            return True
        return False
    
    @staticmethod
    def get_goal_progress(db: Session, goal_id: int, user_id: int) -> Dict:
        """Get detailed progress for a goal"""
        goal = db.query(FinancialGoal).filter(
            FinancialGoal.id == goal_id,
            FinancialGoal.user_id == user_id
        ).first()
        
        if not goal:
            return {}
        
        # Calculate progress
        progress_percent = (goal.current_amount / goal.target_amount * 100) if goal.target_amount > 0 else 0
        remaining_amount = goal.target_amount - goal.current_amount
        
        # Calculate time remaining
        today = datetime.now().date()
        days_remaining = (goal.deadline - today).days
        months_remaining = max(1, days_remaining / 30)
        
        # Calculate required monthly savings
        required_monthly = remaining_amount / months_remaining if months_remaining > 0 else remaining_amount
        
        # Get user's average monthly savings
        month_start = today.replace(day=1)
        last_3_months = month_start - relativedelta(months=3)
        
        total_income = db.query(func.sum(Income.amount)).filter(
            Income.user_id == user_id,
            Income.date >= last_3_months
        ).scalar() or 0
        
        total_expenses = db.query(func.sum(Expense.amount)).filter(
            Expense.user_id == user_id,
            Expense.date >= last_3_months
        ).scalar() or 0
        
        avg_monthly_savings = (total_income - total_expenses) / 3
        
        # Determine if on track
        on_track = avg_monthly_savings >= required_monthly
        
        # Calculate completion date estimate
        if avg_monthly_savings > 0:
            months_to_complete = remaining_amount / avg_monthly_savings
            estimated_completion = today + relativedelta(months=int(months_to_complete))
        else:
            estimated_completion = None
        
        return {
            "goal": {
                "id": goal.id,
                "name": goal.name,
                "target_amount": goal.target_amount,
                "current_amount": goal.current_amount,
                "deadline": goal.deadline.isoformat(),
                "category": goal.category,
                "status": goal.status
            },
            "progress_percent": round(progress_percent, 1),
            "remaining_amount": round(remaining_amount, 2),
            "days_remaining": days_remaining,
            "required_monthly_savings": round(required_monthly, 2),
            "average_monthly_savings": round(avg_monthly_savings, 2),
            "on_track": on_track,
            "estimated_completion": estimated_completion.isoformat() if estimated_completion else None,
            "status_message": "On Track" if on_track else "Behind Schedule"
        }
    
    @staticmethod
    def get_all_goals_with_progress(db: Session, user_id: int) -> List[Dict]:
        """Get all goals with progress information"""
        goals = GoalService.get_all_goals(db, user_id)
        return [GoalService.get_goal_progress(db, goal.id, user_id) for goal in goals]
