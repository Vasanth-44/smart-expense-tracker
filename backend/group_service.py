"""
Group Finance Management Service
Handles household/roommate/team finance groups
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from models import Group, GroupMember, GroupInvite, User, Expense, GroupRole, InviteStatus
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import secrets
import string


class GroupService:
    """Service for managing finance groups"""
    
    @staticmethod
    def generate_invite_token() -> str:
        """Generate secure invite token"""
        return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
    
    @staticmethod
    def create_group(db: Session, name: str, description: Optional[str], user_id: int) -> Group:
        """Create a new finance group"""
        group = Group(
            name=name,
            description=description,
            created_by=user_id
        )
        db.add(group)
        db.flush()
        
        # Add creator as owner
        member = GroupMember(
            group_id=group.id,
            user_id=user_id,
            role=GroupRole.OWNER
        )
        db.add(member)
        db.commit()
        db.refresh(group)
        
        return group
    
    @staticmethod
    def get_user_groups(db: Session, user_id: int) -> List[Group]:
        """Get all groups user is member of"""
        memberships = db.query(GroupMember).filter(
            GroupMember.user_id == user_id
        ).all()
        
        return [membership.group for membership in memberships]
    
    @staticmethod
    def get_group_details(db: Session, group_id: int, user_id: int) -> Optional[Dict]:
        """Get detailed group information"""
        # Check if user is member
        membership = db.query(GroupMember).filter(
            and_(
                GroupMember.group_id == group_id,
                GroupMember.user_id == user_id
            )
        ).first()
        
        if not membership:
            return None
        
        group = db.query(Group).filter(Group.id == group_id).first()
        if not group:
            return None
        
        # Get all members
        members = db.query(GroupMember).filter(
            GroupMember.group_id == group_id
        ).all()
        
        member_list = []
        for member in members:
            user = db.query(User).filter(User.id == member.user_id).first()
            member_list.append({
                "id": member.id,
                "user_id": member.user_id,
                "email": user.email if user else "Unknown",
                "role": member.role.value,
                "joined_at": member.joined_at.isoformat()
            })
        
        # Get expense count
        expense_count = db.query(func.count(Expense.id)).filter(
            Expense.group_id == group_id
        ).scalar()
        
        return {
            "id": group.id,
            "name": group.name,
            "description": group.description,
            "created_by": group.created_by,
            "created_at": group.created_at.isoformat(),
            "member_count": len(member_list),
            "expense_count": expense_count,
            "members": member_list,
            "user_role": membership.role.value
        }
    
    @staticmethod
    def invite_member(db: Session, group_id: int, email: str, invited_by: int) -> GroupInvite:
        """Create group invitation"""
        # Check if user is admin/owner
        membership = db.query(GroupMember).filter(
            and_(
                GroupMember.group_id == group_id,
                GroupMember.user_id == invited_by,
                GroupMember.role.in_([GroupRole.OWNER, GroupRole.ADMIN])
            )
        ).first()
        
        if not membership:
            raise PermissionError("Only owners and admins can invite members")
        
        # Check if already invited
        existing = db.query(GroupInvite).filter(
            and_(
                GroupInvite.group_id == group_id,
                GroupInvite.email == email,
                GroupInvite.status == InviteStatus.PENDING
            )
        ).first()
        
        if existing:
            return existing
        
        # Create invite
        token = GroupService.generate_invite_token()
        invite = GroupInvite(
            group_id=group_id,
            email=email,
            token=token,
            invited_by=invited_by,
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        db.add(invite)
        db.commit()
        db.refresh(invite)
        
        return invite
    
    @staticmethod
    def accept_invite(db: Session, token: str, user_id: int) -> GroupMember:
        """Accept group invitation"""
        invite = db.query(GroupInvite).filter(
            GroupInvite.token == token
        ).first()
        
        if not invite:
            raise ValueError("Invalid invite token")
        
        if invite.status != InviteStatus.PENDING:
            raise ValueError("Invite already used or expired")
        
        if invite.expires_at < datetime.utcnow():
            invite.status = InviteStatus.EXPIRED
            db.commit()
            raise ValueError("Invite has expired")
        
        # Get user email
        user = db.query(User).filter(User.id == user_id).first()
        if not user or user.email != invite.email:
            raise ValueError("Invite is for a different email address")
        
        # Check if already member
        existing = db.query(GroupMember).filter(
            and_(
                GroupMember.group_id == invite.group_id,
                GroupMember.user_id == user_id
            )
        ).first()
        
        if existing:
            invite.status = InviteStatus.ACCEPTED
            db.commit()
            return existing
        
        # Add as member
        member = GroupMember(
            group_id=invite.group_id,
            user_id=user_id,
            role=GroupRole.MEMBER
        )
        db.add(member)
        
        invite.status = InviteStatus.ACCEPTED
        db.commit()
        db.refresh(member)
        
        return member
    
    @staticmethod
    def get_group_expenses(db: Session, group_id: int, user_id: int) -> List[Dict]:
        """Get all expenses for a group"""
        # Verify membership
        membership = db.query(GroupMember).filter(
            and_(
                GroupMember.group_id == group_id,
                GroupMember.user_id == user_id
            )
        ).first()
        
        if not membership:
            raise PermissionError("Not a member of this group")
        
        expenses = db.query(Expense).filter(
            Expense.group_id == group_id
        ).order_by(Expense.date.desc()).all()
        
        result = []
        for expense in expenses:
            owner = db.query(User).filter(User.id == expense.user_id).first()
            result.append({
                "id": expense.id,
                "amount": expense.amount,
                "category": expense.category,
                "date": expense.date.isoformat(),
                "note": expense.note,
                "paid_by": owner.email if owner else "Unknown",
                "paid_by_id": expense.user_id
            })
        
        return result
    
    @staticmethod
    def remove_member(db: Session, group_id: int, member_id: int, removed_by: int) -> bool:
        """Remove member from group"""
        # Check if remover is admin/owner
        remover_membership = db.query(GroupMember).filter(
            and_(
                GroupMember.group_id == group_id,
                GroupMember.user_id == removed_by,
                GroupMember.role.in_([GroupRole.OWNER, GroupRole.ADMIN])
            )
        ).first()
        
        if not remover_membership:
            raise PermissionError("Only owners and admins can remove members")
        
        # Get member to remove
        member = db.query(GroupMember).filter(
            and_(
                GroupMember.group_id == group_id,
                GroupMember.id == member_id
            )
        ).first()
        
        if not member:
            return False
        
        # Cannot remove owner
        if member.role == GroupRole.OWNER:
            raise PermissionError("Cannot remove group owner")
        
        db.delete(member)
        db.commit()
        return True
    
    @staticmethod
    def update_member_role(db: Session, group_id: int, member_id: int, new_role: GroupRole, updated_by: int) -> GroupMember:
        """Update member role"""
        # Check if updater is owner
        updater_membership = db.query(GroupMember).filter(
            and_(
                GroupMember.group_id == group_id,
                GroupMember.user_id == updated_by,
                GroupMember.role == GroupRole.OWNER
            )
        ).first()
        
        if not updater_membership:
            raise PermissionError("Only owners can change roles")
        
        member = db.query(GroupMember).filter(
            and_(
                GroupMember.group_id == group_id,
                GroupMember.id == member_id
            )
        ).first()
        
        if not member:
            raise ValueError("Member not found")
        
        member.role = new_role
        db.commit()
        db.refresh(member)
        
        return member
    
    @staticmethod
    def delete_group(db: Session, group_id: int, user_id: int) -> bool:
        """Delete group (owner only)"""
        membership = db.query(GroupMember).filter(
            and_(
                GroupMember.group_id == group_id,
                GroupMember.user_id == user_id,
                GroupMember.role == GroupRole.OWNER
            )
        ).first()
        
        if not membership:
            raise PermissionError("Only owner can delete group")
        
        group = db.query(Group).filter(Group.id == group_id).first()
        if group:
            db.delete(group)
            db.commit()
            return True
        
        return False
