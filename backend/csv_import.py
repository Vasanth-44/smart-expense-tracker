"""
CSV Import service for bulk expense uploads.
Supports bank statements and custom CSV formats.
"""
import csv
import io
from datetime import datetime
from typing import List, Dict, Tuple
from sqlalchemy.orm import Session
from models import Expense
from ai_categorizer import AICategorizer
import hashlib

class CSVImportService:
    """
    Service for importing expenses from CSV files.
    Handles parsing, categorization, and duplicate detection.
    """
    
    # Supported date formats
    DATE_FORMATS = [
        '%Y-%m-%d',      # 2024-02-10
        '%d/%m/%Y',      # 10/02/2024
        '%m/%d/%Y',      # 02/10/2024
        '%d-%m-%Y',      # 10-02-2024
        '%Y/%m/%d',      # 2024/02/10
        '%d %b %Y',      # 10 Feb 2024
        '%d %B %Y',      # 10 February 2024
    ]
    
    @classmethod
    def parse_csv(cls, file_content: str) -> Tuple[List[Dict], List[str]]:
        """
        Parse CSV content and extract expense data.
        
        Returns:
            Tuple of (parsed_rows, errors)
        """
        parsed_rows = []
        errors = []
        
        try:
            # Try to detect delimiter
            sniffer = csv.Sniffer()
            sample = file_content[:1024]
            delimiter = sniffer.sniff(sample).delimiter
        except:
            delimiter = ','
        
        # Parse CSV
        csv_file = io.StringIO(file_content)
        reader = csv.DictReader(csv_file, delimiter=delimiter)
        
        # Normalize column names (case-insensitive)
        if reader.fieldnames:
            reader.fieldnames = [name.lower().strip() for name in reader.fieldnames]
        
        for idx, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
            try:
                parsed_row = cls._parse_row(row, idx)
                if parsed_row:
                    parsed_rows.append(parsed_row)
            except Exception as e:
                errors.append(f"Row {idx}: {str(e)}")
        
        return parsed_rows, errors
    
    @classmethod
    def _parse_row(cls, row: Dict, row_num: int) -> Dict:
        """Parse a single CSV row."""
        # Find date column
        date_str = cls._find_value(row, ['date', 'transaction date', 'trans date', 'posting date'])
        if not date_str:
            raise ValueError("Date column not found")
        
        # Parse date
        date = cls._parse_date(date_str)
        if not date:
            raise ValueError(f"Invalid date format: {date_str}")
        
        # Find description/note
        description = cls._find_value(row, [
            'description', 'note', 'memo', 'details', 
            'transaction description', 'narration', 'particulars'
        ]) or ''
        
        # Find amount
        amount_str = cls._find_value(row, [
            'amount', 'debit', 'withdrawal', 'spent', 
            'transaction amount', 'value'
        ])
        
        if not amount_str:
            raise ValueError("Amount column not found")
        
        # Parse amount (handle negative, currency symbols, commas)
        amount = cls._parse_amount(amount_str)
        if amount <= 0:
            raise ValueError(f"Invalid amount: {amount_str}")
        
        # Auto-categorize using ML
        category = AICategorizer.predict_category(description)
        
        return {
            'date': date,
            'note': description[:500],  # Limit length
            'amount': amount,
            'category': category,
            'row_num': row_num
        }
    
    @classmethod
    def _find_value(cls, row: Dict, possible_keys: List[str]) -> str:
        """Find value from row using multiple possible column names."""
        for key in possible_keys:
            if key in row and row[key]:
                return str(row[key]).strip()
        return ''
    
    @classmethod
    def _parse_date(cls, date_str: str) -> datetime.date:
        """Parse date string using multiple formats."""
        date_str = date_str.strip()
        
        for fmt in cls.DATE_FORMATS:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        
        return None
    
    @classmethod
    def _parse_amount(cls, amount_str: str) -> float:
        """Parse amount string, handling currency symbols and formatting."""
        # Remove currency symbols and whitespace
        amount_str = amount_str.strip()
        amount_str = amount_str.replace('₹', '').replace('$', '').replace('€', '')
        amount_str = amount_str.replace(',', '')  # Remove thousand separators
        amount_str = amount_str.replace(' ', '')
        
        # Handle negative amounts (credits)
        is_negative = amount_str.startswith('-') or amount_str.startswith('(')
        amount_str = amount_str.replace('-', '').replace('(', '').replace(')', '')
        
        try:
            amount = float(amount_str)
            return abs(amount)  # Always return positive
        except ValueError:
            raise ValueError(f"Invalid amount format: {amount_str}")
    
    @classmethod
    def import_expenses(
        cls, 
        user_id: int, 
        parsed_rows: List[Dict], 
        db: Session
    ) -> Dict:
        """
        Import parsed expenses into database with duplicate detection.
        
        Returns:
            Summary dict with success/failure counts
        """
        imported = []
        duplicates = []
        failed = []
        
        for row in parsed_rows:
            try:
                # Check for duplicates
                if cls._is_duplicate(user_id, row, db):
                    duplicates.append({
                        'row_num': row['row_num'],
                        'date': row['date'].isoformat(),
                        'amount': row['amount'],
                        'note': row['note']
                    })
                    continue
                
                # Create expense
                expense = Expense(
                    user_id=user_id,
                    date=row['date'],
                    amount=row['amount'],
                    category=row['category'],
                    note=row['note']
                )
                db.add(expense)
                
                imported.append({
                    'row_num': row['row_num'],
                    'date': row['date'].isoformat(),
                    'amount': row['amount'],
                    'category': row['category'],
                    'note': row['note']
                })
                
            except Exception as e:
                failed.append({
                    'row_num': row['row_num'],
                    'error': str(e)
                })
        
        # Commit all at once
        if imported:
            db.commit()
        
        # Generate category summary
        category_summary = {}
        for item in imported:
            cat = item['category']
            category_summary[cat] = category_summary.get(cat, 0) + 1
        
        return {
            'total_rows': len(parsed_rows),
            'imported': len(imported),
            'duplicates': len(duplicates),
            'failed': len(failed),
            'imported_records': imported,
            'duplicate_records': duplicates,
            'failed_records': failed,
            'category_summary': category_summary
        }
    
    @classmethod
    def _is_duplicate(cls, user_id: int, row: Dict, db: Session) -> bool:
        """
        Check if expense already exists (duplicate detection).
        Uses date, amount, and note hash for matching.
        """
        # Check for exact match within 1 day
        existing = db.query(Expense).filter(
            Expense.user_id == user_id,
            Expense.date == row['date'],
            Expense.amount == row['amount']
        ).first()
        
        if existing:
            # Check if notes are similar (to avoid false positives)
            if existing.note and row['note']:
                # Simple similarity check
                if existing.note.lower()[:50] == row['note'].lower()[:50]:
                    return True
            else:
                # If no notes, consider it duplicate based on date+amount
                return True
        
        return False
    
    @classmethod
    def validate_csv(cls, file_content: str) -> Dict:
        """
        Validate CSV format and return preview.
        """
        try:
            parsed_rows, errors = cls.parse_csv(file_content)
            
            # Get preview (first 5 rows)
            preview = parsed_rows[:5]
            
            return {
                'valid': len(errors) == 0 or len(parsed_rows) > 0,
                'total_rows': len(parsed_rows),
                'errors': errors[:10],  # Limit errors shown
                'preview': [
                    {
                        'date': row['date'].isoformat(),
                        'amount': row['amount'],
                        'category': row['category'],
                        'note': row['note'][:100]  # Truncate for preview
                    }
                    for row in preview
                ]
            }
        except Exception as e:
            return {
                'valid': False,
                'error': str(e),
                'total_rows': 0,
                'errors': [str(e)],
                'preview': []
            }
