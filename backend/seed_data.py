from datetime import datetime, timedelta
from database import SessionLocal, engine, Base
from models import Expense, Budget
from ai_categorizer import AICategorizer

def seed_database():
    """Seed database with sample expenses and budgets."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # Clear existing data
    db.query(Expense).delete()
    db.query(Budget).delete()
    db.commit()
    
    # Sample expenses for last 3 months
    sample_expenses = [
        # Current month
        {"amount": 450, "note": "Swiggy dinner order", "days_ago": 2},
        {"amount": 200, "note": "Uber ride to office", "days_ago": 3},
        {"amount": 1500, "note": "Amazon shopping clothes", "days_ago": 5},
        {"amount": 350, "note": "Zomato lunch", "days_ago": 7},
        {"amount": 150, "note": "Metro card recharge", "days_ago": 8},
        {"amount": 800, "note": "Gym membership", "days_ago": 10},
        {"amount": 2500, "note": "Flight tickets", "days_ago": 12},
        {"amount": 600, "note": "Restaurant dinner", "days_ago": 14},
        {"amount": 300, "note": "Miscellaneous items", "days_ago": 15},
        
        # Last month
        {"amount": 500, "note": "Swiggy food order", "days_ago": 35},
        {"amount": 250, "note": "Ola cab", "days_ago": 38},
        {"amount": 2000, "note": "Flipkart shopping", "days_ago": 40},
        {"amount": 400, "note": "Pizza hut", "days_ago": 42},
        {"amount": 1000, "note": "Petrol fuel", "days_ago": 45},
        {"amount": 500, "note": "Fitness trainer", "days_ago": 48},
        {"amount": 3000, "note": "Hotel booking", "days_ago": 50},
        {"amount": 700, "note": "Shopping mall", "days_ago": 52},
        
        # 2 months ago
        {"amount": 600, "note": "Restaurant meal", "days_ago": 65},
        {"amount": 300, "note": "Bus pass", "days_ago": 68},
        {"amount": 1800, "note": "Clothes shopping", "days_ago": 70},
        {"amount": 450, "note": "Cafe coffee", "days_ago": 72},
        {"amount": 200, "note": "Parking fee", "days_ago": 75},
        {"amount": 900, "note": "Yoga classes", "days_ago": 78},
        {"amount": 2200, "note": "Trip expenses", "days_ago": 80},
    ]
    
    for exp_data in sample_expenses:
        expense_date = datetime.now().date() - timedelta(days=exp_data["days_ago"])
        category = AICategorizer.predict_category(exp_data["note"])
        
        expense = Expense(
            amount=exp_data["amount"],
            category=category,
            date=expense_date,
            note=exp_data["note"]
        )
        db.add(expense)
    
    # Sample budgets
    budgets = [
        {"category": "Food", "amount": 5000},
        {"category": "Gym", "amount": 2000},
        {"category": "Travel", "amount": 4000},
        {"category": "Shopping", "amount": 3000},
        {"category": "Misc", "amount": 1500},
    ]
    
    for budget_data in budgets:
        budget = Budget(category=budget_data["category"], amount=budget_data["amount"])
        db.add(budget)
    
    db.commit()
    print("✅ Database seeded successfully!")
    print(f"   - Added {len(sample_expenses)} sample expenses")
    print(f"   - Added {len(budgets)} category budgets")
    db.close()

if __name__ == "__main__":
    seed_database()
