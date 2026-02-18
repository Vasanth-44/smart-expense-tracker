"""
Anomaly Detection Service
Detects unusual spending patterns and transactions
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from models import Expense
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import Dict, List
import numpy as np


class AnomalyDetectionService:
    """Detect spending anomalies using statistical methods"""
    
    @staticmethod
    def detect_amount_anomalies(db: Session, user_id: int, months: int = 3) -> List[Dict]:
        """
        Detect transactions with unusual amounts using Z-score
        """
        end_date = datetime.now()
        start_date = end_date - relativedelta(months=months)
        
        # Get all expenses
        expenses = db.query(Expense).filter(
            Expense.user_id == user_id,
            Expense.date >= start_date.date()
        ).all()
        
        if len(expenses) < 10:
            return []
        
        amounts = [e.amount for e in expenses]
        mean_amount = np.mean(amounts)
        std_amount = np.std(amounts)
        
        if std_amount == 0:
            return []
        
        anomalies = []
        
        for expense in expenses:
            # Calculate Z-score
            z_score = (expense.amount - mean_amount) / std_amount
            
            # Flag if Z-score > 2.5 (unusual)
            if abs(z_score) > 2.5:
                anomalies.append({
                    "id": expense.id,
                    "amount": expense.amount,
                    "category": expense.category,
                    "date": expense.date.isoformat(),
                    "note": expense.note,
                    "z_score": round(z_score, 2),
                    "reason": f"Amount is {abs(round(z_score, 1))}x standard deviations from average",
                    "severity": "high" if abs(z_score) > 3 else "medium"
                })
        
        return anomalies
    
    @staticmethod
    def detect_category_anomalies(db: Session, user_id: int, months: int = 3) -> List[Dict]:
        """
        Detect unusual spending in specific categories
        """
        end_date = datetime.now()
        start_date = end_date - relativedelta(months=months)
        
        # Get category spending by month
        category_monthly = db.query(
            Expense.category,
            func.strftime('%Y-%m', Expense.date).label('month'),
            func.sum(Expense.amount).label('total')
        ).filter(
            Expense.user_id == user_id,
            Expense.date >= start_date.date()
        ).group_by(Expense.category, 'month').all()
        
        # Organize by category
        category_data = {}
        for category, month, total in category_monthly:
            if category not in category_data:
                category_data[category] = []
            category_data[category].append(float(total))
        
        anomalies = []
        current_month = datetime.now().strftime('%Y-%m')
        
        for category, values in category_data.items():
            if len(values) < 2:
                continue
            
            # Get current month spending
            current_spending = db.query(func.sum(Expense.amount)).filter(
                Expense.user_id == user_id,
                Expense.category == category,
                func.strftime('%Y-%m', Expense.date) == current_month
            ).scalar() or 0
            
            # Calculate statistics
            mean_val = np.mean(values)
            std_val = np.std(values)
            
            if std_val == 0:
                continue
            
            z_score = (current_spending - mean_val) / std_val
            
            if z_score > 2:
                percent_increase = ((current_spending - mean_val) / mean_val) * 100
                anomalies.append({
                    "category": category,
                    "current_spending": round(current_spending, 2),
                    "average_spending": round(mean_val, 2),
                    "percent_increase": round(percent_increase, 1),
                    "reason": f"{category} spending is {round(percent_increase, 1)}% above average",
                    "severity": "high" if z_score > 3 else "medium"
                })
        
        return anomalies
    
    @staticmethod
    def detect_spending_spikes(db: Session, user_id: int, days: int = 7) -> List[Dict]:
        """
        Detect sudden spending spikes in recent days
        """
        end_date = datetime.now()
        spike_start = end_date - timedelta(days=days)
        comparison_start = spike_start - timedelta(days=days*4)
        
        # Get recent spending
        recent_spending = db.query(func.sum(Expense.amount)).filter(
            Expense.user_id == user_id,
            Expense.date >= spike_start.date()
        ).scalar() or 0
        
        # Get comparison period spending
        comparison_spending = db.query(func.sum(Expense.amount)).filter(
            Expense.user_id == user_id,
            Expense.date >= comparison_start.date(),
            Expense.date < spike_start.date()
        ).scalar() or 0
        
        # Calculate daily averages
        recent_daily = recent_spending / days
        comparison_daily = comparison_spending / (days * 4) if comparison_spending > 0 else 0
        
        spikes = []
        
        if comparison_daily > 0:
            increase_ratio = recent_daily / comparison_daily
            
            if increase_ratio > 1.5:
                percent_increase = ((recent_daily - comparison_daily) / comparison_daily) * 100
                spikes.append({
                    "period": f"Last {days} days",
                    "daily_average": round(recent_daily, 2),
                    "normal_daily_average": round(comparison_daily, 2),
                    "percent_increase": round(percent_increase, 1),
                    "reason": f"Daily spending increased by {round(percent_increase, 1)}%",
                    "severity": "high" if increase_ratio > 2 else "medium"
                })
        
        return spikes
    
    @staticmethod
    def get_all_anomalies(db: Session, user_id: int) -> Dict:
        """
        Get all types of anomalies
        """
        amount_anomalies = AnomalyDetectionService.detect_amount_anomalies(db, user_id)
        category_anomalies = AnomalyDetectionService.detect_category_anomalies(db, user_id)
        spending_spikes = AnomalyDetectionService.detect_spending_spikes(db, user_id)
        
        # Count by severity
        all_anomalies = amount_anomalies + category_anomalies + spending_spikes
        high_severity = len([a for a in all_anomalies if a.get('severity') == 'high'])
        medium_severity = len([a for a in all_anomalies if a.get('severity') == 'medium'])
        
        return {
            "total_anomalies": len(all_anomalies),
            "high_severity": high_severity,
            "medium_severity": medium_severity,
            "unusual_transactions": amount_anomalies,
            "category_anomalies": category_anomalies,
            "spending_spikes": spending_spikes,
            "message": f"Found {len(all_anomalies)} unusual patterns in your spending"
        }
    
    @staticmethod
    def get_behavioral_insights(db: Session, user_id: int) -> List[Dict]:
        """
        Generate behavioral spending insights
        """
        insights = []
        
        # Compare last 2 months
        now = datetime.now()
        current_month_start = now.replace(day=1)
        last_month_start = (current_month_start - relativedelta(months=1))
        last_month_end = current_month_start - timedelta(days=1)
        
        # Get category spending for both months
        categories = db.query(Expense.category).filter(
            Expense.user_id == user_id
        ).distinct().all()
        
        for (category,) in categories:
            # Current month
            current_spending = db.query(func.sum(Expense.amount)).filter(
                Expense.user_id == user_id,
                Expense.category == category,
                Expense.date >= current_month_start.date()
            ).scalar() or 0
            
            # Last month
            last_spending = db.query(func.sum(Expense.amount)).filter(
                Expense.user_id == user_id,
                Expense.category == category,
                Expense.date >= last_month_start.date(),
                Expense.date <= last_month_end.date()
            ).scalar() or 0
            
            if last_spending == 0:
                continue
            
            change_percent = ((current_spending - last_spending) / last_spending) * 100
            
            if abs(change_percent) > 20:
                icon = "📈" if change_percent > 0 else "📉"
                direction = "increased" if change_percent > 0 else "decreased"
                
                insights.append({
                    "category": category,
                    "change_percent": round(change_percent, 1),
                    "current_amount": round(current_spending, 2),
                    "previous_amount": round(last_spending, 2),
                    "message": f"{icon} {category} spending {direction} by {abs(round(change_percent, 1))}% compared to last month",
                    "type": "increase" if change_percent > 0 else "decrease"
                })
        
        # Check budget overruns
        from models import Budget
        budgets = db.query(Budget).filter(Budget.user_id == user_id).all()
        
        for budget in budgets:
            spent = db.query(func.sum(Expense.amount)).filter(
                Expense.user_id == user_id,
                Expense.category == budget.category,
                Expense.date >= current_month_start.date()
            ).scalar() or 0
            
            if spent > budget.amount:
                overspend = spent - budget.amount
                insights.append({
                    "category": budget.category,
                    "budget": budget.amount,
                    "spent": round(spent, 2),
                    "overspend": round(overspend, 2),
                    "message": f"⚠️ {budget.category} exceeded budget by ₹{round(overspend, 2)}",
                    "type": "budget_exceeded"
                })
        
        return insights
