"""
Subscription Management Service
Handles FREE/PRO plan management and access control
"""

from sqlalchemy.orm import Session
from models import Subscription, User, PlanType, SubscriptionStatus
from datetime import datetime, timedelta
from typing import Optional, Dict
from fastapi import HTTPException, status


class SubscriptionService:
    """Service for managing user subscriptions"""
    
    # Feature limits for FREE plan
    FREE_LIMITS = {
        "forecast_months": 1,  # Only 1 month forecast
        "insights_enabled": False,  # No advanced insights
        "anomaly_detection": False,  # No anomaly detection
        "groups_enabled": False,  # No group finance
        "advanced_analytics": False,  # No advanced analytics
        "max_goals": 3,  # Max 3 financial goals
    }
    
    # PRO plan features (unlimited)
    PRO_FEATURES = {
        "forecast_months": 12,  # 12 months forecast
        "insights_enabled": True,
        "anomaly_detection": True,
        "groups_enabled": True,
        "advanced_analytics": True,
        "max_goals": 999,  # Unlimited goals
    }
    
    @staticmethod
    def create_subscription(db: Session, user_id: int, plan_type: PlanType = PlanType.FREE) -> Subscription:
        """Create subscription for new user"""
        existing = db.query(Subscription).filter(Subscription.user_id == user_id).first()
        if existing:
            return existing
        
        subscription = Subscription(
            user_id=user_id,
            plan_type=plan_type,
            status=SubscriptionStatus.ACTIVE,
            start_date=datetime.utcnow()
        )
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
        
        return subscription
    
    @staticmethod
    def get_subscription(db: Session, user_id: int) -> Optional[Subscription]:
        """Get user subscription"""
        return db.query(Subscription).filter(Subscription.user_id == user_id).first()
    
    @staticmethod
    def upgrade_to_pro(db: Session, user_id: int, stripe_customer_id: Optional[str] = None, 
                      stripe_subscription_id: Optional[str] = None) -> Subscription:
        """Upgrade user to PRO plan"""
        subscription = SubscriptionService.get_subscription(db, user_id)
        
        if not subscription:
            subscription = SubscriptionService.create_subscription(db, user_id, PlanType.PRO)
        else:
            subscription.plan_type = PlanType.PRO
            subscription.status = SubscriptionStatus.ACTIVE
            subscription.start_date = datetime.utcnow()
            subscription.end_date = None  # Ongoing subscription
        
        if stripe_customer_id:
            subscription.stripe_customer_id = stripe_customer_id
        if stripe_subscription_id:
            subscription.stripe_subscription_id = stripe_subscription_id
        
        db.commit()
        db.refresh(subscription)
        
        return subscription
    
    @staticmethod
    def cancel_subscription(db: Session, user_id: int) -> Subscription:
        """Cancel PRO subscription (downgrade to FREE)"""
        subscription = SubscriptionService.get_subscription(db, user_id)
        
        if not subscription:
            raise ValueError("No subscription found")
        
        subscription.plan_type = PlanType.FREE
        subscription.status = SubscriptionStatus.CANCELLED
        subscription.end_date = datetime.utcnow()
        
        db.commit()
        db.refresh(subscription)
        
        return subscription
    
    @staticmethod
    def check_feature_access(db: Session, user_id: int, feature: str) -> bool:
        """Check if user has access to a feature"""
        subscription = SubscriptionService.get_subscription(db, user_id)
        
        if not subscription or subscription.plan_type == PlanType.FREE:
            return SubscriptionService.FREE_LIMITS.get(feature, False)
        
        return SubscriptionService.PRO_FEATURES.get(feature, True)
    
    @staticmethod
    def get_plan_limits(db: Session, user_id: int) -> Dict:
        """Get plan limits for user"""
        subscription = SubscriptionService.get_subscription(db, user_id)
        
        if not subscription or subscription.plan_type == PlanType.FREE:
            return {
                "plan": "FREE",
                "limits": SubscriptionService.FREE_LIMITS
            }
        
        return {
            "plan": "PRO",
            "limits": SubscriptionService.PRO_FEATURES
        }
    
    @staticmethod
    def require_pro(db: Session, user_id: int, feature_name: str = "this feature"):
        """Middleware helper to require PRO plan"""
        subscription = SubscriptionService.get_subscription(db, user_id)
        
        if not subscription or subscription.plan_type != PlanType.PRO:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"PRO plan required to access {feature_name}. Please upgrade your subscription."
            )
    
    @staticmethod
    def get_subscription_status(db: Session, user_id: int) -> Dict:
        """Get detailed subscription status"""
        subscription = SubscriptionService.get_subscription(db, user_id)
        
        if not subscription:
            # Create default FREE subscription
            subscription = SubscriptionService.create_subscription(db, user_id)
        
        return {
            "user_id": user_id,
            "plan_type": subscription.plan_type.value,
            "status": subscription.status.value,
            "start_date": subscription.start_date.isoformat() if subscription.start_date else None,
            "end_date": subscription.end_date.isoformat() if subscription.end_date else None,
            "features": SubscriptionService.PRO_FEATURES if subscription.plan_type == PlanType.PRO else SubscriptionService.FREE_LIMITS,
            "stripe_customer_id": subscription.stripe_customer_id,
            "stripe_subscription_id": subscription.stripe_subscription_id
        }


# Dependency for FastAPI routes
def get_subscription_or_create(db: Session, user_id: int) -> Subscription:
    """Get or create subscription for user"""
    subscription = SubscriptionService.get_subscription(db, user_id)
    if not subscription:
        subscription = SubscriptionService.create_subscription(db, user_id)
    return subscription
