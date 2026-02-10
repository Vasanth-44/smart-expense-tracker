import React, { useEffect, useState } from 'react';
import { budgetAPI, categoriesAPI } from '../services/api';

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
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.category || !formData.amount || formData.amount <= 0) {
      return;
    }

    setLoading(true);
    try {
      await budgetAPI.set(formData);
      setFormData({ category: '', amount: '' });
      loadData();
    } catch (error) {
      console.error('Error setting budget:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-md p-6">
      <h2 className="text-xl font-semibold mb-4 text-gray-800">Budget Manager</h2>
      
      <form onSubmit={handleSubmit} className="mb-6 flex gap-3">
        <select
          value={formData.category}
          onChange={(e) => setFormData({ ...formData, category: e.target.value })}
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          required
        >
          <option value="">Select category</option>
          {categories.map((cat) => (
            <option key={cat} value={cat}>{cat}</option>
          ))}
        </select>
        
        <input
          type="number"
          step="0.01"
          value={formData.amount}
          onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
          placeholder="Budget amount"
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          required
        />
        
        <button
          type="submit"
          disabled={loading}
          className="bg-green-500 hover:bg-green-600 text-white font-medium px-6 py-2 rounded-lg transition disabled:opacity-50"
        >
          {loading ? 'Saving...' : 'Set Budget'}
        </button>
      </form>

      {budgets.length > 0 ? (
        <div className="space-y-3">
          {budgets.map((budget) => (
            <div key={budget.id} className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
              <span className="font-medium text-gray-800">{budget.category}</span>
              <span className="text-gray-600">₹{budget.amount.toFixed(0)} / month</span>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-gray-400 text-center py-6">No budgets set yet</p>
      )}
    </div>
  );
}
