"""
Payment Service
Handles payment integration (Stripe/Razorpay scaffold)
"""

from sqlalchemy.orm import Session
from models import Subscription, User, PlanType
from subscription_service import SubscriptionService
from typing import Dict, Optional
import os


class PaymentService:
    """Service for payment processing"""
    
    # Payment provider configuration
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
    RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "")
    RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "")
    
    # Pricing
    PRO_PLAN_PRICE = 999.0  # ₹999/month
    PRO_PLAN_CURRENCY = "INR"
    
    @staticmethod
    def create_checkout_session(db: Session, user_id: int, plan_type: str = "pro") -> Dict:
        """
        Create payment checkout session
        This is a scaffold - integrate with Stripe or Razorpay
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        # TODO: Integrate with actual payment provider
        # Example for Stripe:
        # import stripe
        # stripe.api_key = PaymentService.STRIPE_SECRET_KEY
        # session = stripe.checkout.Session.create(
        #     customer_email=user.email,
        #     payment_method_types=['card'],
        #     line_items=[{
        #         'price_data': {
        #             'currency': 'inr',
        #             'product_data': {'name': 'ExpenseAI PRO'},
        #             'unit_amount': 99900,  # ₹999 in paise
        #             'recurring': {'interval': 'month'}
        #         },
        #         'quantity': 1,
        #     }],
        #     mode='subscription',
        #     success_url='https://yourapp.com/success',
        #     cancel_url='https://yourapp.com/cancel',
        # )
        # return {"checkout_url": session.url, "session_id": session.id}
        
        # Scaffold response
        return {
            "checkout_url": f"/payment/checkout?user_id={user_id}&plan={plan_type}",
            "session_id": "mock_session_id",
            "amount": PaymentService.PRO_PLAN_PRICE,
            "currency": PaymentService.PRO_PLAN_CURRENCY,
            "message": "Payment integration not configured. Set STRIPE_SECRET_KEY or RAZORPAY credentials."
        }
    
    @staticmethod
    def handle_webhook(db: Session, payload: Dict, signature: str) -> Dict:
        """
        Handle payment webhook events
        This is a scaffold - integrate with Stripe or Razorpay
        """
        # TODO: Verify webhook signature
        # Example for Stripe:
        # import stripe
        # event = stripe.Webhook.construct_event(
        #     payload, signature, os.getenv("STRIPE_WEBHOOK_SECRET")
        # )
        
        event_type = payload.get("type", "")
        
        if event_type == "checkout.session.completed":
            # Payment successful
            session = payload.get("data", {}).get("object", {})
            customer_email = session.get("customer_email")
            subscription_id = session.get("subscription")
            
            # Find user and upgrade
            user = db.query(User).filter(User.email == customer_email).first()
            if user:
                SubscriptionService.upgrade_to_pro(
                    db, 
                    user.id,
                    stripe_subscription_id=subscription_id
                )
                return {"status": "success", "message": "User upgraded to PRO"}
        
        elif event_type == "customer.subscription.deleted":
            # Subscription cancelled
            subscription_id = payload.get("data", {}).get("object", {}).get("id")
            
            # Find subscription and downgrade
            subscription = db.query(Subscription).filter(
                Subscription.stripe_subscription_id == subscription_id
            ).first()
            
            if subscription:
                SubscriptionService.cancel_subscription(db, subscription.user_id)
                return {"status": "success", "message": "Subscription cancelled"}
        
        return {"status": "ignored", "event_type": event_type}
    
    @staticmethod
    def cancel_subscription_external(db: Session, user_id: int) -> Dict:
        """
        Cancel subscription with payment provider
        This is a scaffold - integrate with Stripe or Razorpay
        """
        subscription = SubscriptionService.get_subscription(db, user_id)
        if not subscription:
            raise ValueError("No subscription found")
        
        if subscription.plan_type != PlanType.PRO:
            raise ValueError("User is not on PRO plan")
        
        # TODO: Cancel with payment provider
        # Example for Stripe:
        # import stripe
        # stripe.api_key = PaymentService.STRIPE_SECRET_KEY
        # stripe.Subscription.delete(subscription.stripe_subscription_id)
        
        # Cancel in database
        SubscriptionService.cancel_subscription(db, user_id)
        
        return {
            "status": "success",
            "message": "Subscription cancelled successfully",
            "downgraded_to": "FREE"
        }
    
    @staticmethod
    def get_payment_methods() -> Dict:
        """Get available payment methods"""
        return {
            "methods": [
                {
                    "id": "stripe",
                    "name": "Credit/Debit Card",
                    "enabled": bool(PaymentService.STRIPE_SECRET_KEY),
                    "description": "Pay securely with Stripe"
                },
                {
                    "id": "razorpay",
                    "name": "UPI / Cards / Netbanking",
                    "enabled": bool(PaymentService.RAZORPAY_KEY_ID),
                    "description": "Pay with Razorpay (India)"
                }
            ],
            "pricing": {
                "pro_monthly": PaymentService.PRO_PLAN_PRICE,
                "currency": PaymentService.PRO_PLAN_CURRENCY
            }
        }
