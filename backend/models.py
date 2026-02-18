from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import enum

# Enums for SaaS features
class PlanType(str, enum.Enum):
    FREE = "free"
    PRO = "pro"

class GroupRole(str, enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"

class InviteStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"

class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)  # SaaS: Admin flag
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Existing relationships
    expenses = relationship("Expense", back_populates="owner", cascade="all, delete-orphan")
    budgets = relationship("Budget", back_populates="owner", cascade="all, delete-orphan")
    incomes = relationship("Income", back_populates="owner", cascade="all, delete-orphan")
    assets = relationship("Asset", back_populates="owner", cascade="all, delete-orphan")
    liabilities = relationship("Liability", back_populates="owner", cascade="all, delete-orphan")
    goals = relationship("FinancialGoal", back_populates="owner", cascade="all, delete-orphan")
    
    # SaaS relationships
    subscription = relationship("Subscription", back_populates="user", uselist=False, cascade="all, delete-orphan")
    group_memberships = relationship("GroupMember", back_populates="user", cascade="all, delete-orphan")
    created_groups = relationship("Group", back_populates="creator", cascade="all, delete-orphan")
    splits_owed = relationship("ExpenseSplit", back_populates="user", cascade="all, delete-orphan")

class Expense(Base):
    __tablename__ = "expenses"
    
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    note = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)  # SaaS: Optional group
    
    owner = relationship("User", back_populates="expenses")
    group = relationship("Group", back_populates="expenses")
    splits = relationship("ExpenseSplit", back_populates="expense", cascade="all, delete-orphan")

class Budget(Base):
    __tablename__ = "budgets"
    
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    owner = relationship("User", back_populates="budgets")


class Income(Base):
    __tablename__ = "incomes"
    
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    note = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    owner = relationship("User", back_populates="incomes")


class Asset(Base):
    __tablename__ = "assets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    category = Column(String, nullable=False)  # Cash, Investment, Property, etc.
    date = Column(Date, nullable=False)
    note = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    owner = relationship("User", back_populates="assets")


class Liability(Base):
    __tablename__ = "liabilities"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=False)  # Loan, Credit Card, Mortgage, etc.
    interest_rate = Column(Float, default=0.0)
    date = Column(Date, nullable=False)
    note = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    owner = relationship("User", back_populates="liabilities")


class FinancialGoal(Base):
    __tablename__ = "financial_goals"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    target_amount = Column(Float, nullable=False)
    current_amount = Column(Float, default=0.0)
    deadline = Column(Date, nullable=False)
    category = Column(String, nullable=False)  # Emergency Fund, Vacation, House, etc.
    status = Column(String, default="active")  # active, achieved, cancelled
    created_date = Column(Date, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    owner = relationship("User", back_populates="goals")


# ==================== SaaS MODELS ====================

class Subscription(Base):
    """User subscription model for FREE/PRO plans"""
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    plan_type = Column(SQLEnum(PlanType), default=PlanType.FREE, nullable=False)
    status = Column(SQLEnum(SubscriptionStatus), default=SubscriptionStatus.ACTIVE, nullable=False)
    start_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    end_date = Column(DateTime, nullable=True)
    stripe_customer_id = Column(String, nullable=True)
    stripe_subscription_id = Column(String, nullable=True)
    
    user = relationship("User", back_populates="subscription")


class Group(Base):
    """Finance group for household/roommates/team"""
    __tablename__ = "groups"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    creator = relationship("User", back_populates="created_groups")
    members = relationship("GroupMember", back_populates="group", cascade="all, delete-orphan")
    expenses = relationship("Expense", back_populates="group", cascade="all, delete-orphan")
    invites = relationship("GroupInvite", back_populates="group", cascade="all, delete-orphan")


class GroupMember(Base):
    """Group membership with roles"""
    __tablename__ = "group_members"
    
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(SQLEnum(GroupRole), default=GroupRole.MEMBER, nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    group = relationship("Group", back_populates="members")
    user = relationship("User", back_populates="group_memberships")


class GroupInvite(Base):
    """Group invitation system"""
    __tablename__ = "group_invites"
    
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    email = Column(String, nullable=False, index=True)
    token = Column(String, unique=True, nullable=False, index=True)
    status = Column(SQLEnum(InviteStatus), default=InviteStatus.PENDING, nullable=False)
    invited_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    
    group = relationship("Group", back_populates="invites")


class ExpenseSplit(Base):
    """Expense splitting for group expenses"""
    __tablename__ = "expense_splits"
    
    id = Column(Integer, primary_key=True, index=True)
    expense_id = Column(Integer, ForeignKey("expenses.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount_owed = Column(Float, nullable=False)
    is_settled = Column(Boolean, default=False, nullable=False)
    settled_at = Column(DateTime, nullable=True)
    
    expense = relationship("Expense", back_populates="splits")
    user = relationship("User", back_populates="splits_owed")
