"""
SMS Transaction Parser
Parses transaction SMS from Indian banks and UPI apps
"""
import re
from datetime import datetime
from typing import Optional, Dict

class SMSTransactionParser:
    """
    Parse transaction SMS from various Indian banks and UPI apps.
    Supports: HDFC, ICICI, SBI, Axis, Paytm, PhonePe, Google Pay, etc.
    """
    
    # Common patterns for transaction SMS
    PATTERNS = {
        'amount': [
            r'(?:Rs\.?|INR|₹)\s*([0-9,]+(?:\.[0-9]{2})?)',
            r'(?:debited|spent|paid)\s+(?:Rs\.?|INR|₹)?\s*([0-9,]+(?:\.[0-9]{2})?)',
            r'(?:amount|amt)\s+(?:Rs\.?|INR|₹)?\s*([0-9,]+(?:\.[0-9]{2})?)',
        ],
        'merchant': [
            r'(?:at|to|for)\s+([A-Z][A-Za-z0-9\s\-\.]+?)(?:\s+on|\s+dated|\s+via|\.|\s+UPI)',
            r'(?:paid to|sent to)\s+([A-Z][A-Za-z0-9\s\-\.]+?)(?:\s+on|\s+via|\.)',
            r'(?:merchant|vendor):\s*([A-Za-z0-9\s\-\.]+)',
        ],
        'date': [
            r'(\d{2}[-/]\d{2}[-/]\d{2,4})',
            r'(\d{2}\s+[A-Za-z]{3}\s+\d{2,4})',
            r'on\s+(\d{2}[-/]\d{2}[-/]\d{2,4})',
        ],
        'upi_id': [
            r'UPI\s+Ref\s+No\s+(\d+)',
            r'UPI:\s*([A-Za-z0-9@\-\.]+)',
            r'VPA:\s*([A-Za-z0-9@\-\.]+)',
        ]
    }
    
    # Keywords to identify debit/expense transactions
    DEBIT_KEYWORDS = [
        'debited', 'spent', 'paid', 'withdrawn', 'purchase',
        'payment', 'debit', 'sent', 'transferred', 'used'
    ]
    
    # Keywords to identify credit transactions (ignore these)
    CREDIT_KEYWORDS = [
        'credited', 'received', 'refund', 'cashback', 'credit',
        'deposited', 'added', 'reward'
    ]
    
    @classmethod
    def is_transaction_sms(cls, sms_text: str) -> bool:
        """Check if SMS is a transaction notification."""
        sms_lower = sms_text.lower()
        
        # Check for debit keywords
        has_debit = any(keyword in sms_lower for keyword in cls.DEBIT_KEYWORDS)
        
        # Check for amount pattern
        has_amount = any(re.search(pattern, sms_text, re.IGNORECASE) 
                        for pattern in cls.PATTERNS['amount'])
        
        return has_debit and has_amount
    
    @classmethod
    def is_credit_transaction(cls, sms_text: str) -> bool:
        """Check if SMS is a credit transaction (should be ignored)."""
        sms_lower = sms_text.lower()
        return any(keyword in sms_lower for keyword in cls.CREDIT_KEYWORDS)
    
    @classmethod
    def parse_amount(cls, sms_text: str) -> Optional[float]:
        """Extract transaction amount from SMS."""
        for pattern in cls.PATTERNS['amount']:
            match = re.search(pattern, sms_text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    return float(amount_str)
                except ValueError:
                    continue
        return None
    
    @classmethod
    def parse_merchant(cls, sms_text: str) -> Optional[str]:
        """Extract merchant/payee name from SMS."""
        for pattern in cls.PATTERNS['merchant']:
            match = re.search(pattern, sms_text, re.IGNORECASE)
            if match:
                merchant = match.group(1).strip()
                # Clean up merchant name
                merchant = re.sub(r'\s+', ' ', merchant)
                merchant = merchant.strip('.')
                if len(merchant) > 3:  # Valid merchant name
                    return merchant[:100]  # Limit length
        return None
    
    @classmethod
    def parse_date(cls, sms_text: str) -> Optional[datetime.date]:
        """Extract transaction date from SMS."""
        for pattern in cls.PATTERNS['date']:
            match = re.search(pattern, sms_text, re.IGNORECASE)
            if match:
                date_str = match.group(1)
                # Try different date formats
                date_formats = [
                    '%d-%m-%Y', '%d/%m/%Y', '%d-%m-%y', '%d/%m/%y',
                    '%d %b %Y', '%d %b %y', '%d %B %Y', '%d %B %y'
                ]
                for fmt in date_formats:
                    try:
                        return datetime.strptime(date_str, fmt).date()
                    except ValueError:
                        continue
        
        # If no date found, use today
        return datetime.now().date()
    
    @classmethod
    def parse_upi_ref(cls, sms_text: str) -> Optional[str]:
        """Extract UPI reference number."""
        for pattern in cls.PATTERNS['upi_id']:
            match = re.search(pattern, sms_text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    
    @classmethod
    def parse_sms(cls, sms_text: str, sender: str = None) -> Optional[Dict]:
        """
        Parse transaction SMS and extract all details.
        
        Returns:
            dict with keys: amount, merchant, date, note, upi_ref
            None if not a valid transaction SMS
        """
        # Check if it's a transaction SMS
        if not cls.is_transaction_sms(sms_text):
            return None
        
        # Ignore credit transactions
        if cls.is_credit_transaction(sms_text):
            return None
        
        # Extract details
        amount = cls.parse_amount(sms_text)
        if not amount or amount <= 0:
            return None
        
        merchant = cls.parse_merchant(sms_text)
        date = cls.parse_date(sms_text)
        upi_ref = cls.parse_upi_ref(sms_text)
        
        # Create note from merchant and original SMS
        note_parts = []
        if merchant:
            note_parts.append(merchant)
        if upi_ref:
            note_parts.append(f"UPI: {upi_ref}")
        if sender:
            note_parts.append(f"via {sender}")
        
        note = ' | '.join(note_parts) if note_parts else sms_text[:200]
        
        return {
            'amount': amount,
            'merchant': merchant or 'Unknown',
            'date': date,
            'note': note,
            'upi_ref': upi_ref,
            'raw_sms': sms_text[:500]  # Store original SMS
        }
    
    @classmethod
    def get_bank_from_sender(cls, sender: str) -> Optional[str]:
        """Identify bank from SMS sender ID."""
        sender_upper = sender.upper()
        
        bank_mapping = {
            'HDFC': 'HDFC Bank',
            'ICICI': 'ICICI Bank',
            'SBI': 'State Bank of India',
            'AXIS': 'Axis Bank',
            'KOTAK': 'Kotak Bank',
            'PAYTM': 'Paytm',
            'PHONEPE': 'PhonePe',
            'GPAY': 'Google Pay',
            'AMAZONPAY': 'Amazon Pay',
            'BHIM': 'BHIM UPI',
        }
        
        for key, bank in bank_mapping.items():
            if key in sender_upper:
                return bank
        
        return None


# Example usage and test cases
if __name__ == '__main__':
    # Test SMS examples
    test_sms = [
        "Rs 250.00 debited from A/c XX1234 on 10-02-2024 at SWIGGY BANGALORE. UPI Ref No 402345678901",
        "Your A/c XX5678 is debited with Rs.1,500.00 on 10-Feb-24 for payment to UBER INDIA via UPI",
        "INR 450 spent on Amazon.in using HDFC Bank Card XX9012 on 10/02/2024",
        "You have paid Rs 300.00 to ZOMATO via PhonePe UPI on 10-02-2024",
        "Rs.2000 credited to your account XX1234 on 10-02-24 (This should be ignored)",
    ]
    
    parser = SMSTransactionParser()
    
    print("🧪 Testing SMS Parser\n")
    for i, sms in enumerate(test_sms, 1):
        print(f"Test {i}:")
        print(f"SMS: {sms[:80]}...")
        result = parser.parse_sms(sms, sender="HDFCBK")
        if result:
            print(f"✅ Parsed: ₹{result['amount']} at {result['merchant']} on {result['date']}")
            print(f"   Note: {result['note']}")
        else:
            print("❌ Not a valid debit transaction")
        print()
