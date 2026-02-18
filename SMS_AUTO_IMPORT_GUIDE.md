# 📱 SMS Auto-Import Feature

Automatically import expenses from transaction SMS messages!

---

## 🎯 How It Works

1. **Transaction SMS** → Your bank/UPI app sends transaction SMS
2. **SMS Forwarding** → Forward SMS to your expense tracker
3. **Auto-Parsing** → Backend extracts amount, merchant, date
4. **ML Categorization** → AI categorizes the expense
5. **Auto-Import** → Expense added to your account

---

## 🏦 Supported Banks & Apps

### Banks
- ✅ HDFC Bank
- ✅ ICICI Bank
- ✅ State Bank of India (SBI)
- ✅ Axis Bank
- ✅ Kotak Mahindra Bank
- ✅ Most other Indian banks

### UPI Apps
- ✅ Paytm
- ✅ PhonePe
- ✅ Google Pay (GPay)
- ✅ Amazon Pay
- ✅ BHIM UPI
- ✅ WhatsApp Pay

---

## 🚀 Setup Methods

### Method 1: SMS Forwarding App (Recommended)

#### Step 1: Install SMS Forwarder App
Download one of these apps from Play Store:
- **SMS Forwarder** (by Triangular Apps)
- **SMS to URL** (by Bogdan Poplauschi)
- **Tasker** (Advanced users)

#### Step 2: Configure Forwarding Rule

1. Open the SMS Forwarder app
2. Create a new rule:
   - **Filter**: Contains "debited" OR "paid" OR "spent"
   - **Sender**: Your bank's SMS sender ID (e.g., HDFCBK, ICICIB)
   - **Action**: Send to URL/Webhook

3. Set webhook URL:
   ```
   http://YOUR_SERVER_IP:8000/sms/webhook
   ```

4. Set HTTP Method: **POST**

5. Set Headers:
   ```
   Authorization: Bearer YOUR_JWT_TOKEN
   Content-Type: application/json
   ```

6. Set Body (JSON):
   ```json
   {
     "sender": "{{sender}}",
     "message": "{{message}}",
     "timestamp": "{{timestamp}}"
   }
   ```

#### Step 3: Get Your JWT Token

1. Login to your expense tracker
2. Open browser console (F12)
3. Type: `localStorage.getItem('token')`
4. Copy the token (without quotes)
5. Use it in the Authorization header

---

### Method 2: Manual SMS Forward

#### For Testing/Occasional Use:

1. Receive transaction SMS
2. Use a tool like **Postman** or **curl**
3. Send POST request to `/sms/webhook`

**Example using curl:**
```bash
curl -X POST http://localhost:8000/sms/webhook \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "sender": "HDFCBK",
    "message": "Rs 250.00 debited from A/c XX1234 on 10-02-2024 at SWIGGY BANGALORE"
  }'
```

---

### Method 3: IFTTT Integration

#### Step 1: Create IFTTT Account
Go to [ifttt.com](https://ifttt.com) and sign up

#### Step 2: Create Applet

1. **IF**: Android SMS → New SMS received
   - Filter: Sender contains "HDFC" OR "ICICI" etc.
   - Filter: Body contains "debited"

2. **THEN**: Webhooks → Make a web request
   - URL: `http://YOUR_SERVER:8000/sms/webhook`
   - Method: POST
   - Content Type: application/json
   - Body:
     ```json
     {
       "sender": "{{FromNumber}}",
       "message": "{{Text}}",
       "timestamp": "{{OccurredAt}}"
     }
     ```
   - Headers:
     ```
     Authorization: Bearer YOUR_JWT_TOKEN
     ```

---

## 🧪 Testing

### Test SMS Parsing (No Expense Created)

```bash
curl -X POST http://localhost:8000/sms/test-parse \
  -H "Content-Type: application/json" \
  -d '{
    "sender": "HDFCBK",
    "message": "Rs 250.00 debited from A/c XX1234 on 10-02-2024 at SWIGGY BANGALORE. UPI Ref No 402345678901"
  }'
```

**Response:**
```json
{
  "valid": true,
  "message": "SMS parsed successfully",
  "parsed_data": {
    "amount": 250.0,
    "merchant": "SWIGGY BANGALORE",
    "date": "2024-02-10",
    "note": "SWIGGY BANGALORE | UPI: 402345678901 | via HDFCBK",
    "upi_ref": "402345678901",
    "suggested_category": "Food"
  }
}
```

---

## 📋 SMS Format Examples

### Example 1: HDFC Bank
```
Rs 250.00 debited from A/c XX1234 on 10-02-2024 at SWIGGY BANGALORE. 
UPI Ref No 402345678901
```
**Parsed:**
- Amount: ₹250
- Merchant: SWIGGY BANGALORE
- Category: Food
- Date: 10-02-2024

### Example 2: ICICI Bank
```
Your A/c XX5678 is debited with Rs.1,500.00 on 10-Feb-24 for payment 
to UBER INDIA via UPI
```
**Parsed:**
- Amount: ₹1,500
- Merchant: UBER INDIA
- Category: Travel
- Date: 10-Feb-2024

### Example 3: PhonePe
```
You have paid Rs 300.00 to ZOMATO via PhonePe UPI on 10-02-2024
```
**Parsed:**
- Amount: ₹300
- Merchant: ZOMATO
- Category: Food
- Date: 10-02-2024

### Example 4: Google Pay
```
INR 450 spent on Amazon.in using HDFC Bank Card XX9012 on 10/02/2024
```
**Parsed:**
- Amount: ₹450
- Merchant: Amazon.in
- Category: Shopping
- Date: 10/02/2024

---

## 🔒 Security

### Important Security Notes:

1. **JWT Token**: Keep your token secure, don't share it
2. **HTTPS**: Use HTTPS in production (not HTTP)
3. **Token Expiry**: Tokens expire, you'll need to refresh
4. **Webhook Security**: Consider adding webhook secret key
5. **Rate Limiting**: Backend should have rate limiting

### Recommended: Add Webhook Secret

Update your webhook to include a secret key:

```python
# In main.py
WEBHOOK_SECRET = "your-secret-key-here"

@app.post("/sms/webhook")
async def sms_webhook(
    sms: SMSWebhook,
    webhook_secret: str = Header(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if webhook_secret != WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="Invalid webhook secret")
    # ... rest of code
```

---

## 🎯 Features

### ✅ What It Does:
- Parses transaction SMS automatically
- Extracts amount, merchant, date
- Auto-categorizes using ML model
- Detects and prevents duplicates
- Supports multiple banks and UPI apps
- Works with various SMS formats

### ❌ What It Doesn't Do:
- Doesn't read SMS directly from your phone (needs forwarding)
- Doesn't store credit/refund transactions
- Doesn't work with non-transaction SMS
- Doesn't require bank API access

---

## 🐛 Troubleshooting

### SMS Not Parsing?

1. **Check SMS Format**: Use `/sms/test-parse` endpoint
2. **Check Sender**: Make sure sender ID is correct
3. **Check Keywords**: SMS must contain "debited", "paid", or "spent"
4. **Check Amount**: Amount must be in format "Rs 250" or "₹250"

### Duplicate Expenses?

The system checks for duplicates based on:
- Same date
- Same amount
- Same merchant name

If you still get duplicates, the merchant name might be slightly different.

### Token Expired?

1. Login again to get new token
2. Update token in SMS forwarder app
3. Consider implementing token refresh

---

## 📱 Mobile App (Future Enhancement)

Want a dedicated Android app? You can build:

1. **SMS Reader App**:
   - Reads transaction SMS automatically
   - No manual forwarding needed
   - Background service
   - Real-time sync

2. **Features**:
   - Auto-detect transaction SMS
   - One-tap approve/reject
   - Offline queue
   - Push notifications

**Tech Stack**: React Native or Flutter

---

## 🚀 Production Deployment

### For Public Access:

1. **Deploy Backend**:
   - Use Railway, Render, or Heroku
   - Get public HTTPS URL
   - Enable CORS for your domain

2. **Update Webhook URL**:
   - Change from `localhost:8000` to your public URL
   - Example: `https://your-app.railway.app/sms/webhook`

3. **Security**:
   - Use environment variables for secrets
   - Enable rate limiting
   - Add webhook authentication
   - Use HTTPS only

---

## 💡 Pro Tips

1. **Test First**: Use `/sms/test-parse` before enabling auto-import
2. **Filter Senders**: Only forward SMS from known bank senders
3. **Review Daily**: Check imported expenses daily
4. **Backup**: Keep SMS backup in case of errors
5. **Categories**: Train ML model with your spending patterns

---

## 📊 API Endpoints

### 1. SMS Webhook (Auto-Import)
```
POST /sms/webhook
Authorization: Bearer {token}
Content-Type: application/json

Body:
{
  "sender": "HDFCBK",
  "message": "Rs 250 debited...",
  "timestamp": "2024-02-10T10:30:00"
}

Response:
{
  "status": "success",
  "message": "Expense created from SMS",
  "expense": {...}
}
```

### 2. Test SMS Parse
```
POST /sms/test-parse
Content-Type: application/json

Body:
{
  "sender": "HDFCBK",
  "message": "Rs 250 debited..."
}

Response:
{
  "valid": true,
  "parsed_data": {...}
}
```

---

## 🎉 Success!

Once set up, your expenses will be automatically imported from SMS! 

**No more manual entry!** 🚀

---

## 📚 Resources

- [SMS Forwarder App](https://play.google.com/store/apps/details?id=com.trianguloy.smsforwarder)
- [IFTTT](https://ifttt.com)
- [Tasker](https://tasker.joaoapps.com/)
- [Postman](https://www.postman.com/)

---

**Questions? Issues? Let me know!** 💬
