import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, DollarSign, PiggyBank, BarChart3 } from 'lucide-react';
import axios from 'axios';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, BarChart, Bar, XAxis, YAxis } from 'recharts';
import GlassCard from './ui/GlassCard';
import AnimatedCounter from './ui/AnimatedCounter';
import { API_BASE_URL } from '../services/api';
const COLORS = ['#10b981', '#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b'];

export default function FinancialSummary() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSummary();
  }, []);

  const loadSummary = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_BASE_URL}/analytics/financial-summary`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSummary(response.data);
    } catch (error) {
      console.error('Error loading financial summary:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-48 bg-white/5 rounded-2xl animate-pulse" />
        ))}
      </div>
    );
  }

  if (!summary) {
    return null;
  }

  const comparisonData = [
    { name: 'Income', value: summary.total_income, color: '#10b981' },
    { name: 'Expenses', value: summary.total_expenses, color: '#ef4444' }
  ];

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {/* Total Income */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <GlassCard className="border-green-500/30 bg-green-500/5">
            <div className="flex items-center justify-between mb-2">
              <p className="text-gray-400 text-sm">Total Income</p>
              <TrendingUp className="text-green-400" size={20} />
            </div>
            <p className="text-3xl font-bold text-green-400">
              <AnimatedCounter end={summary.total_income} prefix="₹" decimals={0} />
            </p>
            <p className="text-xs text-gray-500 mt-1">{summary.month}</p>
          </GlassCard>
        </motion.div>

        {/* Total Expenses */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <GlassCard className="border-red-500/30 bg-red-500/5">
            <div className="flex items-center justify-between mb-2">
              <p className="text-gray-400 text-sm">Total Expenses</p>
              <TrendingDown className="text-red-400" size={20} />
            </div>
            <p className="text-3xl font-bold text-red-400">
              <AnimatedCounter end={summary.total_expenses} prefix="₹" decimals={0} />
            </p>
            <p className="text-xs text-gray-500 mt-1">{summary.month}</p>
          </GlassCard>
        </motion.div>

        {/* Net Balance */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <GlassCard className={`border-${summary.net_balance >= 0 ? 'blue' : 'orange'}-500/30 bg-${summary.net_balance >= 0 ? 'blue' : 'orange'}-500/5`}>
            <div className="flex items-center justify-between mb-2">
              <p className="text-gray-400 text-sm">Net Balance</p>
              <DollarSign className={`text-${summary.net_balance >= 0 ? 'blue' : 'orange'}-400`} size={20} />
            </div>
            <p className={`text-3xl font-bold text-${summary.net_balance >= 0 ? 'blue' : 'orange'}-400`}>
              <AnimatedCounter end={summary.net_balance} prefix="₹" decimals={0} />
            </p>
            <p className="text-xs text-gray-500 mt-1">
              {summary.net_balance >= 0 ? 'Savings' : 'Deficit'}
            </p>
          </GlassCard>
        </motion.div>

        {/* Savings Rate */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <GlassCard className="border-purple-500/30 bg-purple-500/5">
            <div className="flex items-center justify-between mb-2">
              <p className="text-gray-400 text-sm">Savings Rate</p>
              <PiggyBank className="text-purple-400" size={20} />
            </div>
            <p className="text-3xl font-bold text-purple-400">
              <AnimatedCounter end={summary.savings_rate} suffix="%" decimals={1} />
            </p>
            <p className="text-xs text-gray-500 mt-1">
              {summary.savings_rate >= 20 ? 'Great!' : summary.savings_rate >= 10 ? 'Good' : 'Improve'}
            </p>
          </GlassCard>
        </motion.div>
      </div>

      {/* Charts */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Income vs Expenses Bar Chart */}
        <GlassCard>
          <h3 className="text-lg font-semibold mb-4 text-white flex items-center gap-2">
            <BarChart3 size={20} className="text-indigo-400" />
            Income vs Expenses
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={comparisonData}>
              <XAxis dataKey="name" tick={{ fill: '#9ca3af', fontSize: 12 }} />
              <YAxis tick={{ fill: '#9ca3af', fontSize: 12 }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'rgba(15, 23, 42, 0.9)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: '12px',
                  color: 'white'
                }}
                formatter={(value) => `₹${value.toFixed(0)}`}
              />
              <Bar dataKey="value" radius={[8, 8, 0, 0]}>
                {comparisonData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </GlassCard>

        {/* Income Breakdown Pie Chart */}
        <GlassCard>
          <h3 className="text-lg font-semibold mb-4 text-white flex items-center gap-2">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
            Income Sources
          </h3>
          {summary.income_breakdown && summary.income_breakdown.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={summary.income_breakdown}
                  dataKey="amount"
                  nameKey="category"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  label={(entry) => entry.category}
                >
                  {summary.income_breakdown.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'rgba(15, 23, 42, 0.9)',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    borderRadius: '12px',
                    color: 'white'
                  }}
                  formatter={(value) => `₹${value.toFixed(0)}`}
                />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-gray-400 text-center py-12">No income data yet</p>
          )}
        </GlassCard>
      </div>

      {/* Financial Health Indicator */}
      <GlassCard className="border-indigo-500/30">
        <h3 className="text-lg font-semibold mb-4 text-white">Financial Health</h3>
        <div className="space-y-3">
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-400">Savings Rate</span>
              <span className="text-white font-semibold">{summary.savings_rate.toFixed(1)}%</span>
            </div>
            <div className="w-full bg-white/10 rounded-full h-2">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${Math.min(summary.savings_rate, 100)}%` }}
                transition={{ duration: 1, delay: 0.5 }}
                className={`h-2 rounded-full ${
                  summary.savings_rate >= 20 ? 'bg-green-500' :
                  summary.savings_rate >= 10 ? 'bg-yellow-500' :
                  'bg-red-500'
                }`}
              />
            </div>
          </div>
          
          <div className="grid grid-cols-3 gap-4 mt-4 text-center">
            <div>
              <p className="text-xs text-gray-400">Target</p>
              <p className="text-lg font-bold text-green-400">20%+</p>
            </div>
            <div>
              <p className="text-xs text-gray-400">Good</p>
              <p className="text-lg font-bold text-yellow-400">10-20%</p>
            </div>
            <div>
              <p className="text-xs text-gray-400">Improve</p>
              <p className="text-lg font-bold text-red-400">&lt;10%</p>
            </div>
          </div>
        </div>
      </GlassCard>
    </div>
  );
}
