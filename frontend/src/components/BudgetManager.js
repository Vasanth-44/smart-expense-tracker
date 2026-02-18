import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Wallet, TrendingUp, Plus } from 'lucide-react';
import { budgetAPI, categoriesAPI } from '../services/api';
import GlassCard from './ui/GlassCard';
import Button from './ui/Button';
import Input from './ui/Input';
import toast from 'react-hot-toast';

export default function BudgetManager() {
  const [budgets, setBudgets] = useState([]);
  const [categories, setCategories] = useState([]);
  const [formData, setFormData] = useState({ category: '', amount: '' });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [budgetsRes, categoriesRes] = await Promise.all([
        budgetAPI.getAll(),
        categoriesAPI.getAll()
      ]);
      setBudgets(budgetsRes.data);
      setCategories(categoriesRes.data.categories);
    } catch (error) {
      console.error('Error loading budgets:', error);
      toast.error('Failed to load budgets');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.category || !formData.amount || formData.amount <= 0) {
      toast.error('Please fill in all fields');
      return;
    }

    setLoading(true);
    try {
      await budgetAPI.set(formData);
      toast.success('Budget set successfully!');
      setFormData({ category: '', amount: '' });
      loadData();
    } catch (error) {
      console.error('Error setting budget:', error);
      toast.error('Failed to set budget');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <GlassCard className="max-w-2xl mx-auto">
        <h2 className="text-2xl font-bold mb-6 text-white flex items-center gap-2">
          <Wallet className="text-indigo-400" />
          Set Budget
        </h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Category
              </label>
              <select
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500/50 transition-all duration-200 appearance-none cursor-pointer"
                required
              >
                <option value="" className="bg-slate-900">Select category</option>
                {categories.map((cat) => (
                  <option key={cat} value={cat} className="bg-slate-900">{cat}</option>
                ))}
              </select>
            </div>
            
            <Input
              label="Budget Amount (₹)"
              type="number"
              step="0.01"
              value={formData.amount}
              onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
              placeholder="0.00"
              required
            />
          </div>
          
          <Button
            type="submit"
            loading={loading}
            icon={Plus}
            className="w-full"
          >
            Set Budget
          </Button>
        </form>
      </GlassCard>

      {budgets.length > 0 ? (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {budgets.map((budget, index) => (
            <motion.div
              key={budget.id}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.1 }}
            >
              <GlassCard className="border-indigo-500/30">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-semibold text-white">{budget.category}</h3>
                  <TrendingUp className="text-indigo-400" size={20} />
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between items-baseline">
                    <span className="text-sm text-gray-400">Monthly Budget</span>
                    <span className="text-2xl font-bold text-white">
                      ₹{budget.amount.toFixed(0)}
                    </span>
                  </div>
                  <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: '100%' }}
                      transition={{ duration: 1, delay: index * 0.1 }}
                      className="h-full bg-gradient-to-r from-indigo-500 to-purple-500"
                    />
                  </div>
                </div>
              </GlassCard>
            </motion.div>
          ))}
        </div>
      ) : (
        <GlassCard className="text-center py-12">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
          >
            <div className="text-6xl mb-4">💰</div>
            <h3 className="text-xl font-semibold text-white mb-2">No budgets set yet</h3>
            <p className="text-gray-400">Set your first budget to track spending</p>
          </motion.div>
        </GlassCard>
      )}
    </div>
  );
}
