# 💰 Smart Expense Tracker

A full-stack expense tracking application with AI-powered features, machine learning predictions, and a premium modern UI.

## 🌟 Features

### Core Functionality
- **Expense Management**: Add, edit, delete, and categorize expenses
- **Income Tracking**: Track multiple income sources with categories
- **Budget Management**: Set and monitor monthly budgets with visual indicators
- **Financial Dashboard**: Real-time overview of spending patterns and trends

### Advanced Features
- **AI Chatbot Assistant**: Get financial advice and insights using AI
- **ML Predictions**: Machine learning model predicts expense categories automatically
- **SMS Auto-Import**: Parse and import expenses from SMS notifications
- **CSV Import/Export**: Bulk import expenses from CSV files
- **Data Visualization**: Interactive charts and graphs using Recharts
- **Authentication**: Secure JWT-based user authentication

### UI/UX
- **Premium Design**: Modern glass-morphism UI with animations
- **Responsive Layout**: Works seamlessly on desktop and mobile
- **Dark Theme**: Eye-friendly dark mode interface
- **Smooth Animations**: Framer Motion and React Spring animations
- **Real-time Updates**: Live data updates without page refresh

## 🛠️ Tech Stack

### Frontend
- **React 18** - UI framework
- **Tailwind CSS** - Styling
- **Framer Motion** - Animations
- **Recharts** - Data visualization
- **Axios** - HTTP client
- **Lucide React** - Icons
- **React Hot Toast** - Notifications

### Backend
- **FastAPI** - Python web framework
- **SQLAlchemy** - ORM
- **SQLite** - Database
- **JWT** - Authentication
- **Scikit-learn** - Machine learning
- **Uvicorn** - ASGI server

## 📦 Installation

### Prerequisites
- Node.js (v14 or higher)
- Python 3.8+
- pip

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python -m uvicorn main:app --reload
```

Backend will run on `http://127.0.0.1:8000`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

Frontend will run on `http://localhost:3000`

## 🚀 Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/Vasanth-44/smart-expense-tracker.git
cd smart-expense-tracker
```

2. **Set up the backend** (see Backend Setup above)

3. **Set up the frontend** (see Frontend Setup above)

4. **Create initial ML model** (optional)
```bash
cd backend
python create_simple_model.py
```

5. **Seed sample data** (optional)
```bash
python seed_data.py
```

## 📱 Features in Detail

### Income Tracking
- Add multiple income sources
- Categorize income (Salary, Freelance, Investment, etc.)
- View income history and trends
- Track total income vs expenses

### Expense Management
- Quick expense entry with auto-categorization
- Edit and delete expenses
- Filter by date range and category
- Search functionality

### Budget Management
- Set monthly budgets per category
- Visual progress indicators
- Budget alerts and warnings
- Spending insights

### AI Features
- **AI Chatbot**: Ask questions about your finances
- **ML Predictions**: Automatic expense categorization
- **Smart Insights**: AI-generated financial advice

### Import/Export
- **SMS Import**: Parse bank SMS for automatic expense entry
- **CSV Import**: Bulk import from spreadsheets
- **CSV Export**: Export data for analysis

## 🎨 UI Components

- **Glass Card**: Modern glass-morphism design
- **Animated Background**: Dynamic gradient animations
- **Sidebar Navigation**: Smooth slide-in navigation
- **Modal Dialogs**: Elegant popup forms
- **Animated Counters**: Count-up number animations
- **Custom Buttons**: Styled interactive buttons

## 📊 API Endpoints

### Authentication
- `POST /auth/signup` - Register new user
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user

### Expenses
- `GET /expenses` - Get all expenses
- `POST /expenses` - Create expense
- `PUT /expenses/{id}` - Update expense
- `DELETE /expenses/{id}` - Delete expense

### Income
- `GET /income` - Get all income
- `POST /income` - Create income entry
- `PUT /income/{id}` - Update income
- `DELETE /income/{id}` - Delete income

### Budget
- `GET /budgets` - Get all budgets
- `POST /budgets` - Create budget
- `PUT /budgets/{id}` - Update budget

### ML & AI
- `POST /predict-category` - Predict expense category
- `POST /ai/chat` - Chat with AI assistant

### Import
- `POST /import/sms` - Import from SMS
- `POST /import/csv` - Import from CSV

## 🔐 Environment Variables

Create a `.env` file in the backend directory:

```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./expenses.db
```

## 📝 Project Structure

```
smart-expense-tracker/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── models.py            # Database models
│   ├── services.py          # Business logic
│   ├── auth.py              # Authentication
│   ├── database.py          # Database setup
│   ├── ai_assistant.py      # AI chatbot
│   ├── ml_predictions.py    # ML model
│   ├── sms_parser.py        # SMS parsing
│   ├── csv_import.py        # CSV import
│   ├── income_service.py    # Income logic
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── services/        # API services
│   │   └── App.js           # Main app
│   └── package.json         # Node dependencies
└── README.md
```

## 🚀 Deployment

### Deploy to Vercel (Frontend)
See [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md) for detailed instructions.

### Deploy Backend
Recommended platforms:
- **Render**: Easy Python deployment
- **Railway**: Simple setup with database
- **Heroku**: Classic PaaS option

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the MIT License.

## 👨‍💻 Author

**Vasanth**
- GitHub: [@Vasanth-44](https://github.com/Vasanth-44)

## 🙏 Acknowledgments

- FastAPI for the amazing Python framework
- React team for the excellent UI library
- Tailwind CSS for the utility-first CSS framework
- All open-source contributors

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

⭐ Star this repo if you find it helpful!
