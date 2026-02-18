# 🚀 Quick Test Guide - SaaS Features

## Step 1: Create Test Users

Run this command to create test accounts:

```bash
cd backend
python create_test_users.py
```

This creates 3 test accounts:
- **free@test.com** - FREE plan user
- **pro@test.com** - PRO plan user  
- **admin@test.com** - Admin user with PRO plan

All passwords: `password123`

---

## Step 2: Start the Application

### Terminal 1 - Backend:
```bash
cd backend
uvicorn main:app --reload
```

### Terminal 2 - Frontend:
```bash
cd frontend
npm start
```

---

## Step 3: Test Features

### 🆓 Test FREE Plan Features
1. Login as: `free@test.com` / `password123`
2. ✅ Can use: Dashboard, Expenses, Budget, Forecasting (1 month)
3. ❌ Cannot use: Groups (shows upgrade prompt)
4. Click "Upgrade to PRO" button to see pricing page

### 👑 Test PRO Plan Features
1. Login as: `pro@test.com` / `password123`
2. ✅ Can use: All FREE features + Groups
3. Test Group Finance:
   - Click "Groups" in sidebar
   - Create a new group (e.g., "Roommates")
   - Invite a member (use any email)
   - Copy invite link
   - View group details and balances

### 🔧 Test Admin Dashboard
1. Login as: `admin@test.com` / `password123`
2. Click "Admin" in sidebar (orange badge)
3. View:
   - Total users count
   - PRO vs FREE users
   - Revenue statistics
   - Feature usage
   - Recent users list

---

## Step 4: Test Expense Splitting

1. Login as PRO user
2. Go to Groups → Select your group
3. Add an expense to the group
4. Click "Split" button
5. Choose split type:
   - **Equal**: Divide equally among members
   - **Percentage**: Custom percentages (must sum to 100%)
   - **Custom**: Specific amounts (must sum to total)
6. View balances in group dashboard

---

## Step 5: Test Subscription Flow

### Upgrade Flow:
1. Login as FREE user
2. Click "Upgrade to PRO" in sidebar
3. View pricing comparison
4. Click "Upgrade to PRO" button
5. See payment integration message (demo mode)

### Check Subscription Status:
1. Open browser console
2. Check API call: `GET /subscription/status`
3. See plan details and features

---

## 🎯 Key Features to Test

### ✅ Group Finance
- [ ] Create group (PRO only)
- [ ] Invite members
- [ ] View group expenses
- [ ] See member list with roles
- [ ] Check balances

### ✅ Expense Splitting
- [ ] Split expense equally
- [ ] Split by percentage
- [ ] Split by custom amounts
- [ ] Settle a split
- [ ] View who owes whom

### ✅ Subscription System
- [ ] FREE user sees upgrade prompts
- [ ] PRO user has access to all features
- [ ] Subscription badge shows in sidebar
- [ ] Pricing page displays correctly

### ✅ Admin Dashboard
- [ ] View user statistics
- [ ] See revenue metrics
- [ ] Check conversion rate
- [ ] View recent users
- [ ] Feature usage stats

---

## 🐛 Troubleshooting

### Database Issues:
```bash
cd backend
python -c "from database import Base, engine; Base.metadata.create_all(bind=engine)"
```

### Port Already in Use:
```bash
# Kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Kill process on port 3000
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

### Module Not Found:
```bash
cd backend
pip install -r requirements.txt

cd frontend
npm install
```

---

## 📊 API Testing with Swagger

Visit: http://localhost:8000/docs

Test endpoints:
- POST /groups/create
- GET /groups/list
- POST /expenses/{id}/split
- GET /subscription/status
- GET /admin/stats (requires admin token)

---

## 🎨 UI Features to Check

### Sidebar:
- [ ] PRO badge shows for PRO users
- [ ] "Upgrade to PRO" button for FREE users
- [ ] Groups menu item has crown icon (PRO feature)
- [ ] Admin menu has orange badge

### Group Dashboard:
- [ ] Glassmorphism cards
- [ ] Smooth animations
- [ ] Member list with roles
- [ ] Balance cards with colors (green/red)
- [ ] Invite modal with email input

### Pricing Page:
- [ ] Two plan cards (FREE and PRO)
- [ ] Feature comparison
- [ ] Current plan badge
- [ ] Upgrade button
- [ ] FAQ section

### Admin Dashboard:
- [ ] KPI cards with gradients
- [ ] Animated counters
- [ ] Revenue charts
- [ ] User table with pagination
- [ ] Feature usage metrics

---

## 🔐 Security Testing

### Test Access Control:
1. Login as FREE user
2. Try to access: http://localhost:8000/groups/create
3. Should get 403 error (PRO required)

### Test Admin Protection:
1. Login as regular user
2. Try to access: http://localhost:8000/admin/stats
3. Should get 403 error (Admin required)

### Test Group Permissions:
1. Create group as PRO user
2. Try to delete as non-owner
3. Should get permission error

---

## 📱 Mobile Testing

1. Open http://localhost:3000 on mobile
2. Check responsive layout
3. Test sidebar on mobile
4. Verify all features work

---

## 🎉 Success Criteria

All features working if:
- ✅ FREE users can't access Groups
- ✅ PRO users can create groups
- ✅ Expense splitting works correctly
- ✅ Balances calculate properly
- ✅ Admin dashboard shows stats
- ✅ Subscription badges display
- ✅ Upgrade flow works
- ✅ UI is smooth and responsive

---

## 📞 Need Help?

Check these files:
- `SAAS_UPGRADE_COMPLETE.md` - Full documentation
- `backend/main.py` - API endpoints
- `frontend/src/App.js` - Routes
- API Docs: http://localhost:8000/docs

---

**Happy Testing! 🚀**
