"""
AI-powered spending assistant that analyzes user's expense data
and provides personalized financial advice.
"""
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from models import Expense, Budget
import random

class AISpendingAssistant:
    """
    Modular AI assistant for financial advice.
    Can be upgraded to use OpenAI API or local LLM later.
    """
    
    @classmethod
    def generate_response(cls, user_id: int, query: str, db: Session) -> dict:
        """
        Generate AI response based on user query and their expense data.
        
        Returns:
            dict: {
                "message": str,
                "insights": list,
                "suggested_actions": list,
                "data": dict (optional)
            }
        """
        query_lower = query.lower()
        
        # Analyze user's financial data
        analysis = cls._analyze_user_finances(user_id, db)
        
        # Route to appropriate handler
        if any(word in query_lower for word in ['save', 'saving', 'tips']):
            return cls._generate_saving_tips(analysis)
        elif any(word in query_lower for word in ['overspend', 'spending', 'spent', 'where']):
            return cls._generate_overspending_analysis(analysis)
        elif any(word in query_lower for word in ['budget', 'advice', 'help']):
            return cls._generate_budget_advice(analysis)
        elif any(word in query_lower for word in ['summary', 'overview', 'status']):
            return cls._generate_financial_summary(analysis)
        else:
            return cls._generate_general_response(analysis)
    
    @classmethod
    def _analyze_user_finances(cls, user_id: int, db: Session) -> dict:
        """Analyze user's complete financial situation."""
        now = datetime.now()
        current_month_start = now.replace(day=1)
        last_month_start = current_month_start - relativedelta(months=1)
        last_month_end = current_month_start - timedelta(days=1)
        
        # Current month expenses by category
        current_expenses = db.query(
            Expense.category,
            func.sum(Expense.amount).label('total'),
            func.count(Expense.id).label('count')
        ).filter(
            Expense.user_id == user_id,
            Expense.date >= current_month_start
        ).group_by(Expense.category).all()
        
        # Last month expenses
        last_expenses = db.query(
            Expense.category,
            func.sum(Expense.amount).label('total')
        ).filter(
            Expense.user_id == user_id,
            Expense.date >= last_month_start,
            Expense.date <= last_month_end
        ).group_by(Expense.category).all()
        
        # Budgets
        budgets = db.query(Budget).filter(Budget.user_id == user_id).all()
        
        # Process data
        current_dict = {cat: {'total': float(total), 'count': count} 
                       for cat, total, count in current_expenses}
        last_dict = {cat: float(total) for cat, total in last_expenses}
        budget_dict = {b.category: b.amount for b in budgets}
        
        total_current = sum(item['total'] for item in current_dict.values())
        total_last = sum(last_dict.values())
        
        return {
            'current_month': current_dict,
            'last_month': last_dict,
            'budgets': budget_dict,
            'total_current': total_current,
            'total_last': total_last,
            'month_name': now.strftime('%B')
        }
    
    @classmethod
    def _generate_saving_tips(cls, analysis: dict) -> dict:
        """Generate personalized saving tips."""
        current = analysis['current_month']
        budgets = analysis['budgets']
        
        tips = []
        actions = []
        
        # Find highest spending category
        if current:
            highest_cat = max(current, key=lambda x: current[x]['total'])
            highest_amount = current[highest_cat]['total']
            
            tips.append(f"Your highest spending is on {highest_cat} (₹{highest_amount:.0f})")
            
            # Category-specific tips
            if highest_cat == 'Food':
                tips.append("Consider meal prepping to reduce food delivery costs")
                actions.append("Set a weekly food budget")
                actions.append("Cook at home 3 more days per week")
            elif highest_cat == 'Travel':
                tips.append("Try carpooling or public transport to save on commute")
                actions.append("Plan trips in advance for better deals")
            elif highest_cat == 'Shopping':
                tips.append("Wait 24 hours before making non-essential purchases")
                actions.append("Use price comparison tools")
        
        # Budget-based tips
        for category, budget in budgets.items():
            if category in current:
                spent = current[category]['total']
                if spent > budget * 0.8:
                    tips.append(f"You've used {(spent/budget*100):.0f}% of your {category} budget")
                    actions.append(f"Reduce {category} spending this week")
        
        # General saving tips
        general_tips = [
            "Track every expense to identify spending patterns",
            "Set up automatic savings transfers",
            "Use the 50/30/20 rule: 50% needs, 30% wants, 20% savings"
        ]
        tips.extend(random.sample(general_tips, 1))
        
        potential_savings = analysis['total_current'] * 0.15
        
        return {
            "message": f"💡 Based on your spending of ₹{analysis['total_current']:.0f} this month, you could potentially save ₹{potential_savings:.0f} by following these tips!",
            "insights": tips,
            "suggested_actions": actions,
            "data": {"potential_savings": potential_savings}
        }
    
    @classmethod
    def _generate_overspending_analysis(cls, analysis: dict) -> dict:
        """Analyze where user is overspending."""
        current = analysis['current_month']
        last = analysis['last_month']
        budgets = analysis['budgets']
        
        insights = []
        actions = []
        overspending_categories = []
        
        # Compare with last month
        for category, data in current.items():
            current_amt = data['total']
            last_amt = last.get(category, 0)
            
            if last_amt > 0:
                change = ((current_amt - last_amt) / last_amt) * 100
                if change > 20:
                    insights.append(f"📈 {category}: +{change:.0f}% increase (₹{current_amt - last_amt:.0f} more)")
                    overspending_categories.append(category)
                    actions.append(f"Review {category} expenses and cut unnecessary items")
        
        # Check budget violations
        for category, budget in budgets.items():
            if category in current:
                spent = current[category]['total']
                if spent > budget:
                    exceeded = spent - budget
                    insights.append(f"⚠️ {category}: Exceeded budget by ₹{exceeded:.0f}")
                    overspending_categories.append(category)
                    actions.append(f"Stop {category} spending for this month")
        
        if not insights:
            insights.append("✅ Great job! You're staying within your budgets")
            insights.append(f"Total spending: ₹{analysis['total_current']:.0f}")
        
        return {
            "message": f"📊 Overspending Analysis for {analysis['month_name']}",
            "insights": insights,
            "suggested_actions": actions if actions else ["Keep up the good work!"],
            "data": {"overspending_categories": overspending_categories}
        }
    
    @classmethod
    def _generate_budget_advice(cls, analysis: dict) -> dict:
        """Generate budget recommendations."""
        current = analysis['current_month']
        budgets = analysis['budgets']
        total = analysis['total_current']
        
        insights = []
        actions = []
        
        # Budget status
        if budgets:
            for category, budget in budgets.items():
                spent = current.get(category, {}).get('total', 0)
                remaining = budget - spent
                percentage = (spent / budget * 100) if budget > 0 else 0
                
                if percentage > 90:
                    insights.append(f"🔴 {category}: {percentage:.0f}% used (₹{remaining:.0f} left)")
                elif percentage > 70:
                    insights.append(f"🟡 {category}: {percentage:.0f}% used (₹{remaining:.0f} left)")
                else:
                    insights.append(f"🟢 {category}: {percentage:.0f}% used (₹{remaining:.0f} left)")
        
        # Recommendations
        if not budgets:
            actions.append("Set budgets for all spending categories")
            actions.append("Start with the 50/30/20 budgeting rule")
        else:
            actions.append("Review and adjust budgets monthly")
            actions.append("Set aside emergency fund (3-6 months expenses)")
        
        # Category without budget
        for category in current.keys():
            if category not in budgets:
                actions.append(f"Set a budget for {category}")
        
        return {
            "message": f"💰 Budget Advice for {analysis['month_name']}",
            "insights": insights if insights else ["Set up budgets to get personalized advice"],
            "suggested_actions": actions,
            "data": {"total_budgeted": sum(budgets.values()), "total_spent": total}
        }
    
    @classmethod
    def _generate_financial_summary(cls, analysis: dict) -> dict:
        """Generate overall financial summary."""
        current = analysis['current_month']
        total_current = analysis['total_current']
        total_last = analysis['total_last']
        
        insights = []
        
        # Month comparison
        if total_last > 0:
            change = ((total_current - total_last) / total_last) * 100
            if change > 0:
                insights.append(f"📈 Spending increased by {change:.0f}% from last month")
            else:
                insights.append(f"📉 Spending decreased by {abs(change):.0f}% from last month")
        
        # Category breakdown
        insights.append(f"💳 Total expenses: ₹{total_current:.0f}")
        insights.append(f"📊 Tracked {sum(data['count'] for data in current.values())} transactions")
        
        if current:
            top_category = max(current, key=lambda x: current[x]['total'])
            insights.append(f"🏆 Top category: {top_category} (₹{current[top_category]['total']:.0f})")
        
        return {
            "message": f"📋 Financial Summary for {analysis['month_name']}",
            "insights": insights,
            "suggested_actions": [
                "Review your spending patterns",
                "Set goals for next month",
                "Identify areas to optimize"
            ],
            "data": {"total": total_current, "categories": len(current)}
        }
    
    @classmethod
    def _generate_general_response(cls, analysis: dict) -> dict:
        """Generate general helpful response."""
        return {
            "message": "👋 Hi! I'm your AI spending assistant. I can help you with:",
            "insights": [
                "💡 Saving tips and recommendations",
                "📊 Overspending analysis",
                "💰 Budget advice and tracking",
                "📈 Financial summaries and trends"
            ],
            "suggested_actions": [
                "Ask me 'How can I save more?'",
                "Ask me 'Where did I overspend?'",
                "Ask me 'Give me budget advice'"
            ],
            "data": {"total_spending": analysis['total_current']}
        }
    
    @classmethod
    def get_quick_suggestions(cls) -> list:
        """Get quick suggestion prompts for the chat UI."""
        return [
            "How can I save more?",
            "Where did I overspend?",
            "Budget advice for this month",
            "Show my financial summary"
        ]
