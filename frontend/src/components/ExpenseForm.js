import React, { useState, useEffect } from 'react';
import { expenseAPI, categoriesAPI } from '../services/api';

export default function ExpenseForm({ onSuccess, editExpense, onCancel }) {
  const [formData, setFormData] = useState({
    amount: '',
    category: '',
    date: new Date().toISOString().split('T')[0],
    note: ''
  });
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
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

    // Auto-predict category
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
    setError('');

    if (!formData.amount || formData.amount <= 0) {
      setError('Please enter a valid amount');
      return;
    }

    if (!formData.category) {
      setError('Please select a category');
      return;
    }

    setLoading(true);
    try {
      if (editExpense) {
        await expenseAPI.update(editExpense.id, formData);
      } else {
        await expenseAPI.create(formData);
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
      setError('Failed to save expense. Please try again.');
      console.error('Error saving expense:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-md p-6">
      <h2 className="text-xl font-semibold mb-4 text-gray-800">
        {editExpense ? 'Edit Expense' : 'Add New Expense'}
      </h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Amount (₹) *
          </label>
          <input
            type="number"
            step="0.01"
            value={formData.amount}
            onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="0.00"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Note / Description
          </label>
          <input
            type="text"
            value={formData.note}
            onChange={handleNoteChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="e.g., Swiggy food order, Uber ride"
          />
          {predictedCategory && !editExpense && (
            <p className="text-sm text-green-600 mt-1">
              🤖 AI suggested: {predictedCategory}
            </p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Category *
          </label>
          <select
            value={formData.category}
            onChange={(e) => setFormData({ ...formData, category: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            required
          >
            <option value="">Select category</option>
            {categories.map((cat) => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Date *
          </label>
          <input
            type="date"
            value={formData.date}
            onChange={(e) => setFormData({ ...formData, date: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            required
          />
        </div>

        <div className="flex gap-3 pt-2">
          <button
            type="submit"
            disabled={loading}
            className="flex-1 bg-blue-500 hover:bg-blue-600 text-white font-medium py-2 px-4 rounded-lg transition disabled:opacity-50"
          >
            {loading ? 'Saving...' : editExpense ? 'Update' : 'Add Expense'}
          </button>
          {editExpense && (
            <button
              type="button"
              onClick={onCancel}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
            >
              Cancel
            </button>
          )}
        </div>
      </form>
    </div>
  );
}
