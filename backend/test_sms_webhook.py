"""
Test script for SMS webhook
Run this to test SMS parsing without needing a real SMS forwarder
"""
import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
# You'll need to get your JWT token after logging in
TOKEN = "YOUR_JWT_TOKEN_HERE"  # Replace with actual token

# Test SMS messages
test_messages = [
    {
        "sender": "HDFCBK",
        "message": "Rs 250.00 debited from A/c XX1234 on 10-02-2024 at SWIGGY BANGALORE. UPI Ref No 402345678901"
    },
    {
        "sender": "ICICIB",
        "message": "Your A/c XX5678 is debited with Rs.1,500.00 on 10-Feb-24 for payment to UBER INDIA via UPI"
    },
    {
        "sender": "PHONEPE",
        "message": "You have paid Rs 300.00 to ZOMATO via PhonePe UPI on 10-02-2024"
    },
    {
        "sender": "GPAY",
        "message": "INR 450 spent on Amazon.in using HDFC Bank Card XX9012 on 10/02/2024"
    },
]

def test_parse_only():
    """Test SMS parsing without creating expenses"""
    print("🧪 Testing SMS Parsing (No expenses created)\n")
    
    for i, sms in enumerate(test_messages, 1):
        print(f"Test {i}: {sms['sender']}")
        print(f"SMS: {sms['message'][:60]}...")
        
        response = requests.post(
            f"{BASE_URL}/sms/test-parse",
            json=sms
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['valid']:
                parsed = data['parsed_data']
                print(f"✅ Amount: ₹{parsed['amount']}")
                print(f"   Merchant: {parsed['merchant']}")
                print(f"   Category: {parsed['suggested_category']}")
                print(f"   Date: {parsed['date']}")
            else:
                print(f"❌ {data['message']}")
        else:
            print(f"❌ Error: {response.status_code}")
        
        print()

def test_webhook():
    """Test SMS webhook (creates actual expenses)"""
    print("🚀 Testing SMS Webhook (Creates expenses)\n")
    
    if TOKEN == "YOUR_JWT_TOKEN_HERE":
        print("❌ Please set your JWT token first!")
        print("   1. Login to your expense tracker")
        print("   2. Open browser console (F12)")
        print("   3. Type: localStorage.getItem('token')")
        print("   4. Copy the token and paste it in this script")
        return
    
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    for i, sms in enumerate(test_messages, 1):
        print(f"Test {i}: {sms['sender']}")
        print(f"SMS: {sms['message'][:60]}...")
        
        response = requests.post(
            f"{BASE_URL}/sms/webhook",
            json=sms,
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                expense = data['expense']
                print(f"✅ Expense created!")
                print(f"   ID: {expense['id']}")
                print(f"   Amount: ₹{expense['amount']}")
                print(f"   Category: {expense['category']}")
                print(f"   Merchant: {expense['merchant']}")
            elif data['status'] == 'duplicate':
                print(f"⚠️  Duplicate: {data['message']}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
        
        print()

if __name__ == "__main__":
    print("=" * 60)
    print("SMS Webhook Test Script")
    print("=" * 60)
    print()
    
    # Test parsing first (no auth needed)
    test_parse_only()
    
    print("\n" + "=" * 60)
    print("To test actual expense creation:")
    print("1. Get your JWT token from the browser")
    print("2. Update TOKEN variable in this script")
    print("3. Run: test_webhook()")
    print("=" * 60)
