"""
Machine Learning service for spending prediction and anomaly detection.
Uses scikit-learn for regression and statistical methods for anomalies.
"""
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from models import Expense
import numpy as np
from collections import defaultdict

class MLPredictionService:
    """
    ML-based prediction and anomaly detection service.
    Can be upgraded with more sophisticated models.
    """
    
    @classmethod
    def predict_next_month(cls, user_id: int, db: Session) -> dict:
        """
        Predict next month's total spending using historical data.
        Uses simple linear regression on monthly totals.
        """
        # Get historical monthly spending (last 6 months)
        now = datetime.now()
        six_months_ago = now - relativedelta(months=6)
        
        monthly_data = db.query(
            extract('year', Expense.date).label('year'),
            extract('month', Expense.date).label('month'),
            func.sum(Expense.amount).label('total')
        ).filter(
            Expense.user_id == user_id,
            Expense.date >= six_months_ago
        ).group_by('year', 'month').order_by('year', 'month').all()
        
        if len(monthly_data) < 2:
            return {
                "predicted_amount": 0,
                "confidence": "low",
                "message": "Not enough data for prediction. Add more expenses!",
                "historical_data": []
            }
        
        # Prepare data for prediction
        amounts = [float(total) for _, _, total in monthly_data]
        months = list(range(len(amounts)))
        
        # Simple linear regression
        prediction, trend = cls._simple_linear_regression(months, amounts)
        
        # Calculate confidence based on data variance
        variance = np.var(amounts)
        mean = np.mean(amounts)
        cv = (np.sqrt(variance) / mean) if mean > 0 else 1
        
        if cv < 0.2:
            confidence = "high"
        elif cv < 0.4:
            confidence = "medium"
        else:
            confidence = "low"
        
        # Generate insights
        if trend > 0:
            trend_message = f"📈 Your spending is trending upward by ₹{abs(trend):.0f}/month"
        elif trend < 0:
            trend_message = f"📉 Your spending is trending downward by ₹{abs(trend):.0f}/month"
        else:
            trend_message = "➡️ Your spending is stable"
        
        # Category-wise predictions
        category_predictions = cls._predict_category_spending(user_id, db)
        
        return {
            "predicted_amount": round(prediction, 2),
            "confidence": confidence,
            "trend": trend_message,
            "message": f"Based on {len(amounts)} months of data",
            "historical_data": [
                {
                    "month": datetime(int(year), int(month), 1).strftime('%b %Y'),
                    "amount": float(total)
                }
                for year, month, total in monthly_data
            ],
            "category_predictions": category_predictions
        }
    
    @classmethod
    def _simple_linear_regression(cls, x, y):
        """Simple linear regression implementation."""
        n = len(x)
        x_mean = np.mean(x)
        y_mean = np.mean(y)
        
        # Calculate slope
        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return y_mean, 0
        
        slope = numerator / denominator
        intercept = y_mean - slope * x_mean
        
        # Predict next month
        next_x = n
        prediction = slope * next_x + intercept
        
        return max(0, prediction), slope
    
    @classmethod
    def _predict_category_spending(cls, user_id: int, db: Session) -> list:
        """Predict spending for each category next month."""
        now = datetime.now()
        three_months_ago = now - relativedelta(months=3)
        
        # Get category averages for last 3 months
        category_data = db.query(
            Expense.category,
            func.avg(Expense.amount).label('avg_amount'),
            func.count(Expense.id).label('count')
        ).filter(
            Expense.user_id == user_id,
            Expense.date >= three_months_ago
        ).group_by(Expense.category).all()
        
        predictions = []
        for category, avg_amount, count in category_data:
            # Estimate monthly spending for category
            monthly_estimate = float(avg_amount) * (count / 3)
            predictions.append({
                "category": category,
                "predicted_amount": round(monthly_estimate, 2)
            })
        
        return sorted(predictions, key=lambda x: x['predicted_amount'], reverse=True)
    
    @classmethod
    def detect_anomalies(cls, user_id: int, db: Session) -> dict:
        """
        Detect unusual spending patterns using statistical methods.
        Identifies spikes that are significantly above normal.
        """
        now = datetime.now()
        current_month_start = now.replace(day=1)
        six_months_ago = current_month_start - relativedelta(months=6)
        
        # Get historical data by category
        historical_data = db.query(
            Expense.category,
            extract('year', Expense.date).label('year'),
            extract('month', Expense.date).label('month'),
            func.sum(Expense.amount).label('total')
        ).filter(
            Expense.user_id == user_id,
            Expense.date >= six_months_ago
        ).group_by(Expense.category, 'year', 'month').all()
        
        # Organize by category
        category_history = defaultdict(list)
        for category, year, month, total in historical_data:
            category_history[category].append(float(total))
        
        # Detect anomalies
        anomalies = []
        warnings = []
        
        for category, amounts in category_history.items():
            if len(amounts) < 3:
                continue
            
            # Calculate statistics
            mean = np.mean(amounts)
            std = np.std(amounts)
            current = amounts[-1]  # Most recent month
            
            # Z-score method for anomaly detection
            if std > 0:
                z_score = (current - mean) / std
                
                if z_score > 2:  # More than 2 standard deviations
                    severity = "high" if z_score > 3 else "medium"
                    anomalies.append({
                        "category": category,
                        "current_amount": round(current, 2),
                        "average_amount": round(mean, 2),
                        "deviation": round((current - mean), 2),
                        "percentage_increase": round(((current - mean) / mean) * 100, 1),
                        "severity": severity,
                        "message": f"Unusual spike in {category} spending"
                    })
                elif z_score > 1.5:
                    warnings.append({
                        "category": category,
                        "current_amount": round(current, 2),
                        "average_amount": round(mean, 2),
                        "message": f"{category} spending is above normal"
                    })
        
        # Detect unusual transaction patterns
        unusual_transactions = cls._detect_unusual_transactions(user_id, db)
        
        return {
            "anomalies": anomalies,
            "warnings": warnings,
            "unusual_transactions": unusual_transactions,
            "summary": {
                "total_anomalies": len(anomalies),
                "high_severity": len([a for a in anomalies if a['severity'] == 'high']),
                "medium_severity": len([a for a in anomalies if a['severity'] == 'medium'])
            }
        }
    
    @classmethod
    def _detect_unusual_transactions(cls, user_id: int, db: Session) -> list:
        """Detect individual transactions that are unusually large."""
        now = datetime.now()
        current_month_start = now.replace(day=1)
        
        # Get current month transactions
        current_expenses = db.query(Expense).filter(
            Expense.user_id == user_id,
            Expense.date >= current_month_start
        ).all()
        
        if not current_expenses:
            return []
        
        # Calculate statistics
        amounts = [e.amount for e in current_expenses]
        mean = np.mean(amounts)
        std = np.std(amounts)
        
        unusual = []
        for expense in current_expenses:
            if std > 0:
                z_score = (expense.amount - mean) / std
                if z_score > 2.5:  # Significantly larger than average
                    unusual.append({
                        "id": expense.id,
                        "amount": expense.amount,
                        "category": expense.category,
                        "date": expense.date.isoformat(),
                        "note": expense.note,
                        "deviation_from_average": round(expense.amount - mean, 2)
                    })
        
        return sorted(unusual, key=lambda x: x['amount'], reverse=True)[:5]
    
    @classmethod
    def get_spending_insights(cls, user_id: int, db: Session) -> dict:
        """
        Combine predictions and anomalies for comprehensive insights.
        """
        prediction = cls.predict_next_month(user_id, db)
        anomalies = cls.detect_anomalies(user_id, db)
        
        # Generate actionable insights
        insights = []
        
        if prediction['predicted_amount'] > 0:
            insights.append({
                "type": "prediction",
                "icon": "📊",
                "message": f"Predicted spending next month: ₹{prediction['predicted_amount']:.0f}",
                "confidence": prediction['confidence']
            })
        
        if anomalies['anomalies']:
            for anomaly in anomalies['anomalies'][:3]:
                insights.append({
                    "type": "anomaly",
                    "icon": "⚠️",
                    "message": anomaly['message'],
                    "severity": anomaly['severity']
                })
        
        if anomalies['warnings']:
            for warning in anomalies['warnings'][:2]:
                insights.append({
                    "type": "warning",
                    "icon": "⚡",
                    "message": warning['message']
                })
        
        return {
            "insights": insights,
            "prediction": prediction,
            "anomalies": anomalies
        }
