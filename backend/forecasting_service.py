"""
Expense Forecasting Service using Time Series Analysis
Predicts future spending based on historical data
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from models import Expense
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import numpy as np
from typing import Dict, List, Tuple


class ForecastingService:
    """Service for predicting future expenses using time series analysis"""
    
    @staticmethod
    def get_monthly_totals(db: Session, user_id: int, months: int = 6) -> List[Tuple[str, float]]:
        """Get monthly expense totals for the past N months"""
        end_date = datetime.now()
        start_date = end_date - relativedelta(months=months)
        
        # Query monthly totals
        monthly_data = db.query(
            func.strftime('%Y-%m', Expense.date).label('month'),
            func.sum(Expense.amount).label('total')
        ).filter(
            Expense.user_id == user_id,
            Expense.date >= start_date.date(),
            Expense.date <= end_date.date()
        ).group_by('month').order_by('month').all()
        
        return monthly_data
    
    @staticmethod
    def get_category_monthly_totals(db: Session, user_id: int, months: int = 6) -> Dict[str, List[float]]:
        """Get monthly totals by category"""
        end_date = datetime.now()
        start_date = end_date - relativedelta(months=months)
        
        category_data = db.query(
            Expense.category,
            func.strftime('%Y-%m', Expense.date).label('month'),
            func.sum(Expense.amount).label('total')
        ).filter(
            Expense.user_id == user_id,
            Expense.date >= start_date.date(),
            Expense.date <= end_date.date()
        ).group_by(Expense.category, 'month').order_by('month').all()
        
        # Organize by category
        result = {}
        for category, month, total in category_data:
            if category not in result:
                result[category] = []
            result[category].append(float(total))
        
        return result
    
    @staticmethod
    def linear_regression_forecast(values: List[float]) -> Tuple[float, float, float]:
        """
        Simple linear regression forecast
        Returns: (prediction, lower_bound, upper_bound)
        """
        if len(values) < 2:
            avg = sum(values) / len(values) if values else 0
            return avg, avg * 0.8, avg * 1.2
        
        n = len(values)
        x = np.arange(n)
        y = np.array(values)
        
        # Calculate slope and intercept
        x_mean = np.mean(x)
        y_mean = np.mean(y)
        
        numerator = np.sum((x - x_mean) * (y - y_mean))
        denominator = np.sum((x - x_mean) ** 2)
        
        if denominator == 0:
            return y_mean, y_mean * 0.8, y_mean * 1.2
        
        slope = numerator / denominator
        intercept = y_mean - slope * x_mean
        
        # Predict next value
        next_x = n
        prediction = slope * next_x + intercept
        
        # Calculate confidence interval (simple std dev based)
        residuals = y - (slope * x + intercept)
        std_error = np.std(residuals)
        
        lower_bound = max(0, prediction - 1.96 * std_error)
        upper_bound = prediction + 1.96 * std_error
        
        return float(prediction), float(lower_bound), float(upper_bound)
    
    @staticmethod
    def forecast_next_month(db: Session, user_id: int) -> Dict:
        """
        Forecast total spending for next month
        """
        # Get historical data
        monthly_data = ForecastingService.get_monthly_totals(db, user_id, months=6)
        
        if not monthly_data:
            return {
                "prediction": 0,
                "lower_bound": 0,
                "upper_bound": 0,
                "confidence": "low",
                "message": "Not enough historical data for prediction",
                "historical_data": []
            }
        
        # Extract values
        months = [m[0] for m in monthly_data]
        values = [float(m[1]) for m in monthly_data]
        
        # Make prediction
        prediction, lower, upper = ForecastingService.linear_regression_forecast(values)
        
        # Calculate confidence based on data consistency
        if len(values) >= 4:
            cv = np.std(values) / np.mean(values) if np.mean(values) > 0 else 1
            if cv < 0.2:
                confidence = "high"
            elif cv < 0.4:
                confidence = "medium"
            else:
                confidence = "low"
        else:
            confidence = "low"
        
        # Get next month name
        next_month = (datetime.now() + relativedelta(months=1)).strftime('%B %Y')
        
        return {
            "prediction": round(prediction, 2),
            "lower_bound": round(lower, 2),
            "upper_bound": round(upper, 2),
            "confidence": confidence,
            "next_month": next_month,
            "message": f"Based on past {len(values)} months, your spending for {next_month} is estimated at ₹{round(prediction, 2)}",
            "historical_data": [
                {"month": m, "amount": round(v, 2)} 
                for m, v in zip(months, values)
            ]
        }
    
    @staticmethod
    def forecast_by_category(db: Session, user_id: int) -> Dict:
        """
        Forecast spending by category for next month
        """
        category_data = ForecastingService.get_category_monthly_totals(db, user_id, months=6)
        
        if not category_data:
            return {
                "categories": [],
                "message": "Not enough historical data for category predictions"
            }
        
        forecasts = []
        
        for category, values in category_data.items():
            if len(values) >= 2:
                prediction, lower, upper = ForecastingService.linear_regression_forecast(values)
                
                forecasts.append({
                    "category": category,
                    "prediction": round(prediction, 2),
                    "lower_bound": round(lower, 2),
                    "upper_bound": round(upper, 2),
                    "historical_average": round(sum(values) / len(values), 2),
                    "trend": "increasing" if prediction > sum(values) / len(values) else "decreasing"
                })
        
        # Sort by prediction amount
        forecasts.sort(key=lambda x: x['prediction'], reverse=True)
        
        return {
            "categories": forecasts,
            "total_predicted": round(sum(f['prediction'] for f in forecasts), 2),
            "message": f"Category-wise predictions for next month"
        }
    
    @staticmethod
    def get_spending_trend(db: Session, user_id: int) -> Dict:
        """
        Analyze spending trend over time
        """
        monthly_data = ForecastingService.get_monthly_totals(db, user_id, months=6)
        
        if len(monthly_data) < 2:
            return {
                "trend": "insufficient_data",
                "change_percent": 0,
                "message": "Need at least 2 months of data"
            }
        
        values = [float(m[1]) for m in monthly_data]
        
        # Calculate trend
        first_half_avg = sum(values[:len(values)//2]) / (len(values)//2)
        second_half_avg = sum(values[len(values)//2:]) / (len(values) - len(values)//2)
        
        if first_half_avg == 0:
            change_percent = 0
        else:
            change_percent = ((second_half_avg - first_half_avg) / first_half_avg) * 100
        
        if change_percent > 10:
            trend = "increasing"
            message = f"Your spending has increased by {abs(round(change_percent, 1))}% recently"
        elif change_percent < -10:
            trend = "decreasing"
            message = f"Your spending has decreased by {abs(round(change_percent, 1))}% recently"
        else:
            trend = "stable"
            message = "Your spending has been relatively stable"
        
        return {
            "trend": trend,
            "change_percent": round(change_percent, 2),
            "message": message,
            "first_period_avg": round(first_half_avg, 2),
            "second_period_avg": round(second_half_avg, 2)
        }
