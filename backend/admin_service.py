"""
Admin Service
Handles admin dashboard analytics and user management
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from models import User, Subscription, Expense, Group, PlanType, SubscriptionStatus
from datetime import datetime, timedelta
from typing import Dict, List


class AdminService:
    """Service for admin dashboard and analytics"""
    
    @staticmethod
    def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> List[Dict]:
        """Get all users with subscription info"""
        users = db.query(User).offset(skip).limit(limit).all()
        
        result = []
        for user in users:
            subscription = db.query(Subscription).filter(
                Subscription.user_id == user.id
            ).first()
            
            result.append({
                "id": user.id,
                "email": user.email,
                "is_admin": user.is_admin,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "plan_type": subscription.plan_type.value if subscription else "free",
                "subscription_status": subscription.status.value if subscription else "active"
            })
        
        return result
    
    @staticmethod
    def get_subscription_stats(db: Session) -> Dict:
        """Get subscription statistics"""
        total_users = db.query(func.count(User.id)).scalar()
        
        free_users = db.query(func.count(Subscription.id)).filter(
            Subscription.plan_type == PlanType.FREE
        ).scalar()
        
        pro_users = db.query(func.count(Subscription.id)).filter(
            Subscription.plan_type == PlanType.PRO
        ).scalar()
        
        active_subscriptions = db.query(func.count(Subscription.id)).filter(
            Subscription.status == SubscriptionStatus.ACTIVE
        ).scalar()
        
        cancelled_subscriptions = db.query(func.count(Subscription.id)).filter(
            Subscription.status == SubscriptionStatus.CANCELLED
        ).scalar()
        
        return {
            "total_users": total_users,
            "free_users": free_users or 0,
            "pro_users": pro_users or 0,
            "active_subscriptions": active_subscriptions or 0,
            "cancelled_subscriptions": cancelled_subscriptions or 0,
            "conversion_rate": round((pro_users / total_users * 100), 2) if total_users > 0 else 0
        }
    
    @staticmethod
    def get_revenue_stats(db: Session, pro_price: float = 999.0) -> Dict:
        """Calculate revenue statistics (assuming PRO plan price)"""
        pro_users = db.query(func.count(Subscription.id)).filter(
            and_(
                Subscription.plan_type == PlanType.PRO,
                Subscription.status == SubscriptionStatus.ACTIVE
            )
        ).scalar()
        
        monthly_revenue = (pro_users or 0) * pro_price
        annual_revenue = monthly_revenue * 12
        
        # Get new PRO subscriptions this month
        now = datetime.utcnow()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        new_pro_this_month = db.query(func.count(Subscription.id)).filter(
            and_(
                Subscription.plan_type == PlanType.PRO,
                Subscription.start_date >= month_start
            )
        ).scalar()
        
        return {
            "monthly_revenue": round(monthly_revenue, 2),
            "annual_revenue": round(annual_revenue, 2),
            "active_pro_users": pro_users or 0,
            "new_pro_this_month": new_pro_this_month or 0,
            "pro_plan_price": pro_price
        }
    
    @staticmethod
    def get_feature_usage(db: Session) -> Dict:
        """Get feature usage statistics"""
        # Total expenses tracked
        total_expenses = db.query(func.count(Expense.id)).scalar()
        
        # Total groups created
        total_groups = db.query(func.count(Group.id)).scalar()
        
        # Users with groups (PRO feature)
        users_with_groups = db.query(func.count(func.distinct(Group.created_by))).scalar()
        
        # Get expense count by month (last 6 months)
        now = datetime.utcnow()
        six_months_ago = now - timedelta(days=180)
        
        monthly_expenses = db.query(
            func.strftime('%Y-%m', Expense.date).label('month'),
            func.count(Expense.id).label('count')
        ).filter(
            Expense.date >= six_months_ago.date()
        ).group_by('month').order_by('month').all()
        
        return {
            "total_expenses": total_expenses or 0,
            "total_groups": total_groups or 0,
            "users_with_groups": users_with_groups or 0,
            "monthly_expense_trend": [
                {"month": month, "count": count}
                for month, count in monthly_expenses
            ]
        }
    
    @staticmethod
    def get_system_analytics(db: Session) -> Dict:
        """Get comprehensive system analytics"""
        subscription_stats = AdminService.get_subscription_stats(db)
        revenue_stats = AdminService.get_revenue_stats(db)
        feature_usage = AdminService.get_feature_usage(db)
        
        # Get user growth (last 30 days)
        now = datetime.utcnow()
        thirty_days_ago = now - timedelta(days=30)
        
        new_users_30d = db.query(func.count(User.id)).filter(
            User.created_at >= thirty_days_ago
        ).scalar()
        
        return {
            "subscription_stats": subscription_stats,
            "revenue_stats": revenue_stats,
            "feature_usage": feature_usage,
            "user_growth": {
                "new_users_last_30_days": new_users_30d or 0
            },
            "generated_at": now.isoformat()
        }
