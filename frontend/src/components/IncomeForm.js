import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { DollarSign, Calendar, Tag, FileText, Save, X } from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';
import GlassCard from './ui/GlassCard';
import Button from './ui/Button';
import Input from './ui/Input';
import { API_BASE_URL } from '../services/api';

export default function IncomeForm({ onSuccess, editIncome, onCancel }) {
  const [amount, setAmount] = useState('');
  const [category, setCategory] = useState('');
  const [date, setDate] = useState(new Date().toISOString().split('T')[0]);
  const [note, setNote] = useState('');
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadCategories();
  }, []);

  useEffect(() => {
    if (editIncome) {
      setAmount(editIncome.amount.toString());
      setCategory(editIncome.category);
      setDate(editIncome.date);
      setNote(editIncome.note || '');
    }
  }, [editIncome]);

  const loadCategories = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/income-categories`);
      setCategories(response.data.categories);
      if (response.data.categories.length > 0 && !category) {
        setCategory(response.data.categories[0]);
      }
    } catch (error) {
      console.error('Error loading categories:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!amount || !category || !date) {
      toast.error('Please fill in all required fields');
      return;
    }

    setLoading(true);

    try {
      const token = localStorage.getItem('token');
      const incomeData = {
        amount: parseFloat(amount),
        category,
        date,
        note: note || null
      };

      if (editIncome) {
        await axios.put(
          `${API_BASE_URL}/incomes/${editIncome.id}`,
          incomeData,
          { headers: { Authorization: `Bearer ${token}` } }
        );
        toast.success('Income updated successfully!');
      } else {
        await axios.post(
          `${API_BASE_URL}/incomes`,
          incomeData,
          { headers: { Authorization: `Bearer ${token}` } }
        );
        toast.success('Income added successfully!');
      }

      // Reset form
      setAmount('');
      setCategory(categories[0] || '');
      setDate(new Date().toISOString().split('T')[0]);
      setNote('');

      if (onSuccess) onSuccess();
      if (onCancel) onCancel();
    } catch (error) {
      console.error('Error saving income:', error);
      toast.error(error.response?.data?.detail || 'Failed to save income');
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="max-w-2xl mx-auto"
    >
      <GlassCard>
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl flex items-center justify-center">
              <DollarSign size={24} className="text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white">
                {editIncome ? 'Edit Income' : 'Add Income'}
              </h2>
              <p className="text-gray-400 text-sm">Track money coming in</p>
            </div>
          </div>
          {editIncome && onCancel && (
            <Button onClick={onCancel} variant="secondary" className="!p-2">
              <X size={20} />
            </Button>
          )}
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Amount */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              <DollarSign size={16} className="inline mr-1" />
              Amount *
            </label>
            <Input
              type="number"
              step="0.01"
              placeholder="Enter amount"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              required
            />
          </div>

          {/* Category */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              <Tag size={16} className="inline mr-1" />
              Category *
            </label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl 
                       text-white focus:outline-none focus:border-green-500
                       focus:ring-2 focus:ring-green-500/20 transition-all"
              required
            >
              {categories.map((cat) => (
                <option key={cat} value={cat} className="bg-slate-800">
                  {cat}
                </option>
              ))}
            </select>
          </div>

          {/* Date */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              <Calendar size={16} className="inline mr-1" />
              Date *
            </label>
            <Input
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              required
            />
          </div>

          {/* Note */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              <FileText size={16} className="inline mr-1" />
              Note (Optional)
            </label>
            <textarea
              value={note}
              onChange={(e) => setNote(e.target.value)}
              placeholder="Add a note..."
              className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl 
                       text-white placeholder-gray-500 focus:outline-none focus:border-green-500
                       focus:ring-2 focus:ring-green-500/20 transition-all resize-none"
              rows="3"
            />
          </div>

          {/* Submit Button */}
          <Button
            type="submit"
            disabled={loading}
            className="w-full !bg-gradient-to-r !from-green-500 !to-emerald-600 hover:!from-green-600 hover:!to-emerald-700"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent mr-2" />
                Saving...
              </>
            ) : (
              <>
                <Save size={20} className="mr-2" />
                {editIncome ? 'Update Income' : 'Add Income'}
              </>
            )}
          </Button>
        </form>
      </GlassCard>
    </motion.div>
  );
}
