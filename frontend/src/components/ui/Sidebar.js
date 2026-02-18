import React from 'react';
import { motion } from 'framer-motion';
import { LayoutDashboard, PlusCircle, Receipt, Wallet, LogOut, Smartphone, TrendingUp, DollarSign, PieChart } from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab, onLogout, user }) {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'financial-summary', label: 'Financial Summary', icon: PieChart },
    { id: 'add', label: 'Add Expense', icon: PlusCircle },
    { id: 'expenses', label: 'Expenses', icon: Receipt },
    { id: 'add-income', label: 'Add Income', icon: TrendingUp },
    { id: 'income-list', label: 'Income History', icon: DollarSign },
    { id: 'sms', label: 'SMS Import', icon: Smartphone },
    { id: 'budget', label: 'Budget', icon: Wallet },
  ];

  return (
    <motion.div
      initial={{ x: -100, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      className="fixed left-0 top-0 h-full w-64 bg-slate-900/50 backdrop-blur-xl border-r border-white/10 p-6 flex flex-col"
    >
      {/* Logo */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
          💰 ExpenseAI
        </h1>
        <p className="text-xs text-gray-400 mt-1">Smart Finance Tracker</p>
      </div>

      {/* User Info */}
      <div className="mb-6 p-3 bg-white/5 rounded-xl border border-white/10">
        <p className="text-sm text-gray-400">Logged in as</p>
        <p className="text-white font-medium truncate">{user?.email}</p>
      </div>

      {/* Menu Items */}
      <nav className="flex-1 space-y-2">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          
          return (
            <motion.button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              whileHover={{ x: 5 }}
              whileTap={{ scale: 0.98 }}
              className={`
                w-full flex items-center gap-3 px-4 py-3 rounded-xl
                transition-all duration-200
                ${isActive 
                  ? 'bg-gradient-to-r from-indigo-500/20 to-purple-500/20 text-white border border-indigo-500/30' 
                  : 'text-gray-400 hover:text-white hover:bg-white/5'
                }
              `}
            >
              <Icon size={20} />
              <span className="font-medium">{item.label}</span>
              {isActive && (
                <motion.div
                  layoutId="activeTab"
                  className="ml-auto w-2 h-2 bg-indigo-400 rounded-full"
                />
              )}
            </motion.button>
          );
        })}
      </nav>

      {/* Logout Button */}
      <motion.button
        onClick={onLogout}
        whileHover={{ x: 5 }}
        whileTap={{ scale: 0.98 }}
        className="flex items-center gap-3 px-4 py-3 rounded-xl text-red-400 hover:bg-red-500/10 transition-all"
      >
        <LogOut size={20} />
        <span className="font-medium">Logout</span>
      </motion.button>
    </motion.div>
  );
}
