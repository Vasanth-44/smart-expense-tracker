"""
Expense Splitting Service
Handles expense splitting logic and settlement tracking
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from models import ExpenseSplit, Expense, User, GroupMember
from datetime import datetime
from typing import List, Dict, Optional
from enum import Enum


class SplitType(str, Enum):
    EQUAL = "equal"
    PERCENTAGE = "percentage"
    CUSTOM = "custom"


class SplitService:
    """Service for managing expense splits"""
    
    @staticmethod
    def create_split(
        db: Session,
        expense_id: int,
        split_type: SplitType,
        splits: List[Dict],  # [{"user_id": 1, "amount": 100} or {"user_id": 1, "percentage": 50}]
        user_id: int
    ) -> List[ExpenseSplit]:
        """Create expense splits"""
        expense = db.query(Expense).filter(Expense.id == expense_id).first()
        if not expense:
            raise ValueError("Expense not found")
        
        # Verify user has permission (owner or group member)
        if expense.user_id != user_id:
            if expense.group_id:
                membership = db.query(GroupMember).filter(
                    and_(
                        GroupMember.group_id == expense.group_id,
                        GroupMember.user_id == user_id
                    )
                ).first()
                if not membership:
                    raise PermissionError("Not authorized to split this expense")
            else:
                raise PermissionError("Not authorized to split this expense")
        
        # Delete existing splits
        db.query(ExpenseSplit).filter(ExpenseSplit.expense_id == expense_id).delete()
        
        # Calculate amounts based on split type
        split_records = []
        
        if split_type == SplitType.EQUAL:
            amount_per_person = expense.amount / len(splits)
            for split in splits:
                if split['user_id'] != expense.user_id:  # Don't create split for payer
                    split_record = ExpenseSplit(
                        expense_id=expense_id,
                        user_id=split['user_id'],
                        amount_owed=round(amount_per_person, 2)
                    )
                    db.add(split_record)
                    split_records.append(split_record)
        
        elif split_type == SplitType.PERCENTAGE:
            total_percentage = sum(s.get('percentage', 0) for s in splits)
            if abs(total_percentage - 100) > 0.01:
                raise ValueError("Percentages must sum to 100")
            
            for split in splits:
                if split['user_id'] != expense.user_id:
                    amount = (expense.amount * split['percentage']) / 100
                    split_record = ExpenseSplit(
                        expense_id=expense_id,
                        user_id=split['user_id'],
                        amount_owed=round(amount, 2)
                    )
                    db.add(split_record)
                    split_records.append(split_record)
        
        elif split_type == SplitType.CUSTOM:
            total_amount = sum(s.get('amount', 0) for s in splits)
            if abs(total_amount - expense.amount) > 0.01:
                raise ValueError("Split amounts must sum to expense amount")
            
            for split in splits:
                if split['user_id'] != expense.user_id:
                    split_record = ExpenseSplit(
                        expense_id=expense_id,
                        user_id=split['user_id'],
                        amount_owed=round(split['amount'], 2)
                    )
                    db.add(split_record)
                    split_records.append(split_record)
        
        db.commit()
        for record in split_records:
            db.refresh(record)
        
        return split_records
    
    @staticmethod
    def settle_split(db: Session, split_id: int, user_id: int) -> ExpenseSplit:
        """Mark a split as settled"""
        split = db.query(ExpenseSplit).filter(ExpenseSplit.id == split_id).first()
        if not split:
            raise ValueError("Split not found")
        
        # Verify user is the one who owes or the expense owner
        expense = db.query(Expense).filter(Expense.id == split.expense_id).first()
        if split.user_id != user_id and expense.user_id != user_id:
            raise PermissionError("Not authorized to settle this split")
        
        split.is_settled = True
        split.settled_at = datetime.utcnow()
        db.commit()
        db.refresh(split)
        
        return split
    
    @staticmethod
    def get_user_balances(db: Session, group_id: int, user_id: int) -> Dict:
        """Get balance summary for user in a group"""
        # Verify membership
        membership = db.query(GroupMember).filter(
            and_(
                GroupMember.group_id == group_id,
                GroupMember.user_id == user_id
            )
        ).first()
        
        if not membership:
            raise PermissionError("Not a member of this group")
        
        # Get all group expenses
        group_expenses = db.query(Expense).filter(Expense.group_id == group_id).all()
        expense_ids = [e.id for e in group_expenses]
        
        # Amount user owes to others
        owes = db.query(
            Expense.user_id,
            func.sum(ExpenseSplit.amount_owed).label('total')
        ).join(
            Expense, ExpenseSplit.expense_id == Expense.id
        ).filter(
            and_(
                ExpenseSplit.user_id == user_id,
                ExpenseSplit.is_settled == False,
                Expense.id.in_(expense_ids)
            )
        ).group_by(Expense.user_id).all()
        
        # Amount others owe to user
        owed = db.query(
            ExpenseSplit.user_id,
            func.sum(ExpenseSplit.amount_owed).label('total')
        ).join(
            Expense, ExpenseSplit.expense_id == Expense.id
        ).filter(
            and_(
                Expense.user_id == user_id,
                ExpenseSplit.is_settled == False,
                Expense.id.in_(expense_ids)
            )
        ).group_by(ExpenseSplit.user_id).all()
        
        # Format results
        owes_list = []
        for creditor_id, amount in owes:
            creditor = db.query(User).filter(User.id == creditor_id).first()
            owes_list.append({
                "user_id": creditor_id,
                "email": creditor.email if creditor else "Unknown",
                "amount": float(amount)
            })
        
        owed_list = []
        for debtor_id, amount in owed:
            debtor = db.query(User).filter(User.id == debtor_id).first()
            owed_list.append({
                "user_id": debtor_id,
                "email": debtor.email if debtor else "Unknown",
                "amount": float(amount)
            })
        
        total_owes = sum(item['amount'] for item in owes_list)
        total_owed = sum(item['amount'] for item in owed_list)
        net_balance = total_owed - total_owes
        
        return {
            "user_id": user_id,
            "group_id": group_id,
            "owes": owes_list,
            "owed": owed_list,
            "total_owes": round(total_owes, 2),
            "total_owed": round(total_owed, 2),
            "net_balance": round(net_balance, 2)
        }
    
    @staticmethod
    def get_group_balances(db: Session, group_id: int, user_id: int) -> List[Dict]:
        """Get all balances in a group"""
        # Verify membership
        membership = db.query(GroupMember).filter(
            and_(
                GroupMember.group_id == group_id,
                GroupMember.user_id == user_id
            )
        ).first()
        
        if not membership:
            raise PermissionError("Not a member of this group")
        
        # Get all members
        members = db.query(GroupMember).filter(GroupMember.group_id == group_id).all()
        
        balances = []
        for member in members:
            try:
                balance = SplitService.get_user_balances(db, group_id, member.user_id)
                user = db.query(User).filter(User.id == member.user_id).first()
                balance['email'] = user.email if user else "Unknown"
                balances.append(balance)
            except:
                continue
        
        return balances
    
    @staticmethod
    def get_user_splits(db: Session, user_id: int) -> Dict:
        """Get all splits for a user across all groups"""
        # Splits user owes
        owes_splits = db.query(ExpenseSplit).filter(
            and_(
                ExpenseSplit.user_id == user_id,
                ExpenseSplit.is_settled == False
            )
        ).all()
        
        owes_list = []
        for split in owes_splits:
            expense = db.query(Expense).filter(Expense.id == split.expense_id).first()
            if expense:
                payer = db.query(User).filter(User.id == expense.user_id).first()
                owes_list.append({
                    "split_id": split.id,
                    "expense_id": expense.id,
                    "amount": split.amount_owed,
                    "category": expense.category,
                    "date": expense.date.isoformat(),
                    "note": expense.note,
                    "paid_by": payer.email if payer else "Unknown",
                    "paid_by_id": expense.user_id
                })
        
        # Splits owed to user
        user_expenses = db.query(Expense).filter(Expense.user_id == user_id).all()
        expense_ids = [e.id for e in user_expenses]
        
        owed_splits = db.query(ExpenseSplit).filter(
            and_(
                ExpenseSplit.expense_id.in_(expense_ids),
                ExpenseSplit.is_settled == False
            )
        ).all()
        
        owed_list = []
        for split in owed_splits:
            expense = db.query(Expense).filter(Expense.id == split.expense_id).first()
            debtor = db.query(User).filter(User.id == split.user_id).first()
            if expense:
                owed_list.append({
                    "split_id": split.id,
                    "expense_id": expense.id,
                    "amount": split.amount_owed,
                    "category": expense.category,
                    "date": expense.date.isoformat(),
                    "note": expense.note,
                    "owed_by": debtor.email if debtor else "Unknown",
                    "owed_by_id": split.user_id
                })
        
        return {
            "owes": owes_list,
            "owed": owed_list,
            "total_owes": sum(s['amount'] for s in owes_list),
            "total_owed": sum(s['amount'] for s in owed_list)
        }
