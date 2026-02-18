import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Toaster } from 'react-hot-toast';
import Dashboard from './components/Dashboard';
import ExpenseForm from './components/ExpenseForm';
import ExpenseList from './components/ExpenseList';
import BudgetManager from './components/BudgetManager';
import Login from './components/Login';
import Signup from './components/Signup';
import Sidebar from './components/ui/Sidebar';
import AIChat from './components/AIChat';
import AnimatedBackground from './components/ui/AnimatedBackground';
import SMSImport from './components/SMSImport';
import IncomeForm from './components/IncomeForm';
import IncomeList from './components/IncomeList';
import FinancialSummary from './components/FinancialSummary';
import ForecastDashboard from './components/ForecastDashboard';
import NetWorthDashboard from './components/NetWorthDashboard';
import FinancialHealthScore from './components/FinancialHealthScore';
import GoalsPlanner from './components/GoalsPlanner';
import InsightsDashboard from './components/InsightsDashboard';
import GroupDashboard from './components/GroupDashboard';
import PricingPage from './components/PricingPage';
import AdminDashboard from './components/AdminDashboard';
import { SubscriptionProvider } from './context/SubscriptionContext';

function App() {
  const [user, setUser] = useState(null);
  const [showSignup, setShowSignup] = useState(false);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [refreshKey, setRefreshKey] = useState(0);
  const [editExpense, setEditExpense] = useState(null);
  const [editIncome, setEditIncome] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem('token');
    const savedUser = localStorage.getItem('user');
    if (token && savedUser) {
      setUser(JSON.parse(savedUser));
    }
  }, []);

  const handleLogin = (userData) => {
    setUser(userData);
  };

  const handleSignup = (userData) => {
    setUser(userData);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
    setActiveTab('dashboard');
  };

  const handleExpenseSuccess = () => {
    setRefreshKey(prev => prev + 1);
    setEditExpense(null);
    if (activeTab === 'add') {
      setActiveTab('expenses');
    }
  };

  const handleEdit = (expense) => {
    setEditExpense(expense);
    setActiveTab('add');
  };

  const handleCancelEdit = () => {
    setEditExpense(null);
  };

  const handleEditIncome = (income) => {
    setEditIncome(income);
    setActiveTab('add-income');
  };

  const handleCancelIncomeEdit = () => {
    setEditIncome(null);
  };

  // Show login/signup if not authenticated
  if (!user) {
    if (showSignup) {
      return (
        <>
          <Signup onSignup={handleSignup} onSwitchToLogin={() => setShowSignup(false)} />
          <Toaster position="top-right" />
        </>
      );
    }
    return (
      <>
        <Login onLogin={handleLogin} onSwitchToSignup={() => setShowSignup(true)} />
        <Toaster position="top-right" />
      </>
    );
  }

  return (
    <SubscriptionProvider>
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900/20 to-slate-900">
        {/* Animated Particle Background */}
        <AnimatedBackground />
        {/* Animated background */}
        <div className="fixed inset-0 overflow-hidden pointer-events-none">
          <motion.div
            animate={{
              scale: [1, 1.2, 1],
              opacity: [0.3, 0.5, 0.3],
            }}
            transition={{ duration: 20, repeat: Infinity }}
            className="absolute top-0 left-1/4 w-96 h-96 bg-indigo-500/20 rounded-full blur-3xl"
          />
          <motion.div
            animate={{
              scale: [1.2, 1, 1.2],
              opacity: [0.5, 0.3, 0.5],
            }}
            transition={{ duration: 15, repeat: Infinity }}
            className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl"
          />
        </div>

        {/* Sidebar */}
        <Sidebar
          activeTab={activeTab}
          setActiveTab={(tab) => {
            setActiveTab(tab);
            if (tab !== 'add') {
              setEditExpense(null);
            }
          }}
          onLogout={handleLogout}
          user={user}
        />

        {/* Main Content */}
        <div className="ml-64 p-8 relative z-10">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
            >
              {activeTab === 'dashboard' && <Dashboard key={refreshKey} />}
              
              {activeTab === 'add' && (
                <ExpenseForm
                  onSuccess={handleExpenseSuccess}
                  editExpense={editExpense}
                  onCancel={handleCancelEdit}
                />
              )}
              
              {activeTab === 'expenses' && (
                <ExpenseList refresh={refreshKey} onEdit={handleEdit} />
              )}
              
              {activeTab === 'sms' && (
                <SMSImport onImportSuccess={handleExpenseSuccess} />
              )}
              
              {activeTab === 'add-income' && (
                <IncomeForm
                  onSuccess={handleExpenseSuccess}
                  editIncome={editIncome}
                  onCancel={handleCancelIncomeEdit}
                />
              )}
              
              {activeTab === 'income-list' && (
                <IncomeList refresh={refreshKey} onEdit={handleEditIncome} />
              )}
              
              {activeTab === 'financial-summary' && (
                <FinancialSummary />
              )}
              
              {activeTab === 'forecast' && (
                <ForecastDashboard />
              )}
              
              {activeTab === 'networth' && (
                <NetWorthDashboard />
              )}
              
              {activeTab === 'health-score' && (
                <FinancialHealthScore />
              )}
              
              {activeTab === 'goals' && (
                <GoalsPlanner />
              )}
              
              {activeTab === 'insights' && (
                <InsightsDashboard />
              )}
              
              {activeTab === 'groups' && (
                <GroupDashboard />
              )}
              
              {activeTab === 'pricing' && (
                <PricingPage />
              )}
              
              {activeTab === 'admin' && (
                <AdminDashboard />
              )}
              
              {activeTab === 'budget' && <BudgetManager />}
            </motion.div>
          </AnimatePresence>
        </div>

        {/* AI Chat Assistant */}
        <AIChat />

        {/* Toast Notifications */}
        <Toaster
          position="top-right"
          toastOptions={{
            style: {
              background: 'rgba(15, 23, 42, 0.9)',
              color: '#fff',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: '12px',
              backdropFilter: 'blur(10px)',
            },
            success: {
              iconTheme: {
                primary: '#10b981',
                secondary: '#fff',
              },
            },
            error: {
              iconTheme: {
                primary: '#ef4444',
                secondary: '#fff',
              },
            },
          }}
        />
      </div>
    </SubscriptionProvider>
  );
}

export default App;
