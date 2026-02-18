import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { DollarSign, Calendar, Tag, FileText, Sparkles } from 'lucide-react';
import { expenseAPI, categoriesAPI } from '../services/api';
import GlassCard from './ui/GlassCard';
import Button from './ui/Button';
import Input from './ui/Input';
import toast from 'react-hot-toast';

export default function ExpenseForm({ onSuccess, editExpense, onCancel }) {
  const [formData, setFormData] = useState({
    amount: '',
    category: '',
    date: new Date().toISOString().split('T')[0],
    note: ''
  });
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(false);
  const [predictedCategory, setPredictedCategory] = useState('');

  useEffect(() => {
    loadCategories();
    if (editExpense) {
      setFormData({
        amount: editExpense.amount,
        category: editExpense.category,
        date: editExpense.date,
        note: editExpense.note || ''
      });
    }
  }, [editExpense]);

  const loadCategories = async () => {
    try {
      const res = await categoriesAPI.getAll();
      setCategories(res.data.categories);
    } catch (error) {
      console.error('Error loading categories:', error);
    }
  };

  const handleNoteChange = async (e) => {
    const note = e.target.value;
    setFormData({ ...formData, note });

    if (note.length > 3 && !editExpense) {
      try {
        const res = await expenseAPI.predictCategory(note);
        setPredictedCategory(res.data.category);
        if (!formData.category) {
          setFormData(prev => ({ ...prev, category: res.data.category }));
        }
      } catch (error) {
        console.error('Error predicting category:', error);
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!formData.amount || formData.amount <= 0) {
      toast.error('Please enter a valid amount');
      return;
    }

    if (!formData.category) {
      toast.error('Please select a category');
      return;
    }

    setLoading(true);
    try {
      if (editExpense) {
        await expenseAPI.update(editExpense.id, formData);
        toast.success('Expense updated successfully!');
      } else {
        await expenseAPI.create(formData);
        toast.success('Expense added successfully!');
      }
      setFormData({
        amount: '',
        category: '',
        date: new Date().toISOString().split('T')[0],
        note: ''
      });
      setPredictedCategory('');
      onSuccess();
    } catch (error) {
      toast.error('Failed to save expense');
      console.error('Error saving expense:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <GlassCard className="max-w-2xl mx-auto">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h2 className="text-2xl font-bold mb-6 text-white flex items-center gap-2">
          {editExpense ? '✏️ Edit Expense' : '➕ Add New Expense'}
        </h2>
        
        <form onSubmit={handleSubmit} className="space-y-5">
          <Input
            label="Amount (₹)"
            type="number"
            step="0.01"
            value={formData.amount}
            onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
            placeholder="0.00"
            icon={DollarSign}
            required
          />

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Note / Description
            </label>
            <div className="relative">
              <FileText className="absolute left-3 top-3 text-gray-400" size={18} />
              <motion.textarea
                whileFocus={{ scale: 1.01 }}
                value={formData.note}
                onChange={handleNoteChange}
                className="w-full px-4 py-3 pl-10 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500/50 transition-all duration-200 resize-none"
                placeholder="e.g., Swiggy food order, Uber ride"
                rows="3"
              />
            </div>
            {predictedCategory && !editExpense && (
              <motion.p
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-sm text-green-400 mt-2 flex items-center gap-1"
              >
                <Sparkles size={14} />
                AI suggested: {predictedCategory}
              </motion.p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Category
            </label>
            <div className="relative">
              <Tag className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
              <select
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                className="w-full px-4 py-3 pl-10 bg-white/5 border border-white/10 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500/50 transition-all duration-200 appearance-none cursor-pointer"
                required
              >
                <option value="" className="bg-slate-900">Select category</option>
                {categories.map((cat) => (
                  <option key={cat} value={cat} className="bg-slate-900">{cat}</option>
                ))}
              </select>
            </div>
          </div>

          <Input
            label="Date"
            type="date"
            value={formData.date}
            onChange={(e) => setFormData({ ...formData, date: e.target.value })}
            icon={Calendar}
            required
          />

          <div className="flex gap-3 pt-4">
            <Button
              type="submit"
              loading={loading}
              className="flex-1"
            >
              {editExpense ? 'Update Expense' : 'Add Expense'}
            </Button>
            {editExpense && (
              <Button
                type="button"
                onClick={onCancel}
                variant="secondary"
              >
                Cancel
              </Button>
            )}
          </div>
        </form>
      </motion.div>
    </GlassCard>
  );
}
