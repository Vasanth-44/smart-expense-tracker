# Authentication Setup Guide

## Quick Setup Steps

### 1. Install Backend Dependencies

Open a **new Command Prompt** (not PowerShell) and run:

```cmd
cd backend
pip install bcrypt python-jose[cryptography] passlib python-multipart
```

### 2. Start Backend Server

```cmd
python -m uvicorn main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### 3. Refresh Your Browser

Press F5 or Ctrl+R to reload the frontend at http://localhost:3000

### 4. Create Your Account

- Click "Sign up" 
- Enter your email and password (min 6 characters)
- You'll be automatically logged in!

## Troubleshooting

### If signup still fails:

1. **Check backend is running**: Open http://localhost:8000 in browser - should show `{"message":"Smart Expense Tracker API"}`

2. **Check browser console**: Press F12, go to Console tab, look for error messages

3. **Check backend logs**: Look at the terminal where backend is running for error messages

4. **Try these commands in order**:
```cmd
cd backend
pip uninstall bcrypt python-jose passlib -y
pip install bcrypt==4.1.2 python-jose[cryptography]==3.3.0 passlib==1.7.4 python-multipart==0.0.6
python -m uvicorn main:app --reload
```

### Common Issues:

- **"Email already registered"**: The email is already in the database. Try a different email or switch to Login.
- **"Could not validate credentials"**: Token expired or invalid. Clear browser localStorage and try again.
- **Connection refused**: Backend is not running. Start it with `uvicorn main:app --reload`

## What Changed?

- ✅ Added User authentication with JWT tokens
- ✅ Password hashing with bcrypt
- ✅ Each user has isolated data
- ✅ Login/Signup pages
- ✅ Protected API routes
- ✅ Logout functionality

## Security Notes

- Passwords are hashed with bcrypt (never stored in plain text)
- JWT tokens expire after 7 days
- Each user can only access their own expenses and budgets
- Change `SECRET_KEY` in `backend/auth.py` for production use
