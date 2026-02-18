"""
Create test users for SaaS features testing
Run this script to create test accounts with different subscription levels
"""

from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import User, Subscription, PlanType, SubscriptionStatus
from auth import get_password_hash
from datetime import datetime

# Create tables
Base.metadata.create_all(bind=engine)

def create_test_users():
    db = SessionLocal()
    
    try:
        # Test users data
        test_users = [
            {
                "email": "free@test.com",
                "password": "password123",
                "plan": PlanType.FREE,
                "is_admin": False
            },
            {
                "email": "pro@test.com",
                "password": "password123",
                "plan": PlanType.PRO,
                "is_admin": False
            },
            {
                "email": "admin@test.com",
                "password": "password123",
                "plan": PlanType.PRO,
                "is_admin": True
            }
        ]
        
        created_users = []
        
        for user_data in test_users:
            # Check if user already exists
            existing = db.query(User).filter(User.email == user_data["email"]).first()
            if existing:
                print(f"❌ User {user_data['email']} already exists")
                continue
            
            # Create user
            user = User(
                email=user_data["email"],
                hashed_password=get_password_hash(user_data["password"]),
                is_admin=user_data["is_admin"],
                created_at=datetime.utcnow()
            )
            db.add(user)
            db.flush()
            
            # Create subscription
            subscription = Subscription(
                user_id=user.id,
                plan_type=user_data["plan"],
                status=SubscriptionStatus.ACTIVE,
                start_date=datetime.utcnow()
            )
            db.add(subscription)
            
            created_users.append(user_data["email"])
            print(f"✅ Created user: {user_data['email']} (Plan: {user_data['plan'].value}, Admin: {user_data['is_admin']})")
        
        db.commit()
        
        print("\n" + "="*60)
        print("🎉 Test Users Created Successfully!")
        print("="*60)
        print("\nLogin Credentials:")
        print("-" * 60)
        print("\n1. FREE User:")
        print("   Email: free@test.com")
        print("   Password: password123")
        print("   Features: Basic tracking, limited forecasting")
        
        print("\n2. PRO User:")
        print("   Email: pro@test.com")
        print("   Password: password123")
        print("   Features: All features + Groups + Advanced analytics")
        
        print("\n3. Admin User:")
        print("   Email: admin@test.com")
        print("   Password: password123")
        print("   Features: All PRO features + Admin Dashboard")
        
        print("\n" + "="*60)
        print("🚀 Ready to test SaaS features!")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Error creating test users: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("\n🔧 Creating Test Users for SaaS Features...\n")
    create_test_users()
