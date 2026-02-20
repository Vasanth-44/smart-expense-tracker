import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Edit2, Trash2, Calendar, Tag, TrendingUp } from 'lucide-react';
import axios from 'axios';
import GlassCard from './ui/GlassCard';
import Button from './ui/Button';
import toast from 'react-hot-toast';
import { API_BASE_URL } from '../services/api';

export default function IncomeList({ refresh, onEdit }) {
  const [incomes, setIncomes] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadIncomes();
  }, [refresh]);

  const loadIncomes = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_BASE_URL}/incomes`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setIncomes(response.data);
    } catch (error) {
      console.error('Error loading incomes:', error);
      toast.error('Failed to load incomes');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this income?')) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      await axios.delete(`${API_BASE_URL}/incomes/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Income deleted successfully');
      loadIncomes();
    } catch (error) {
      console.error('Error deleting income:', error);
      toast.error('Failed to delete income');
    }
  };

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-32 bg-white/5 rounded-2xl animate-pulse" />
        ))}
      </div>
    );
  }

  if (incomes.length === 0) {
    return (
      <GlassCard className="text-center py-12">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
        >
          <div className="text-6xl mb-4">💰</div>
          <h3 className="text-xl font-semibold text-white mb-2">No income entries yet</h3>
          <p className="text-gray-400">Add your first income to get started</p>
        </motion.div>
      </GlassCard>
    );
  }

  const totalIncome = incomes.reduce((sum, income) => sum + income.amount, 0);

  return (
    <div className="space-y-4">
      <GlassCard className="mb-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
            <h2 className="text-xl font-semibold text-white">Income History</h2>
            <span className="ml-2 text-sm text-gray-400">{incomes.length} entries</span>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-400">Total Income</p>
            <p className="text-2xl font-bold text-green-400">₹{totalIncome.toFixed(2)}</p>
          </div>
        </div>
      </GlassCard>

      <div className="grid grid-cols-1 gap-4">
        <AnimatePresence>
          {incomes.map((income, index) => (
            <motion.div
              key={income.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, x: -100 }}
              transition={{ delay: index * 0.05 }}
            >
              <GlassCard className="hover-lift">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4 flex-1">
                    <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl flex items-center justify-center flex-shrink-0">
                      <TrendingUp size={24} className="text-white" />
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="text-lg font-semibold text-white truncate">
                          ₹{income.amount.toFixed(2)}
                        </h3>
                        <span className="px-2 py-1 bg-green-500/20 text-green-300 text-xs rounded-full">
                          {income.category}
                        </span>
                      </div>
                      
                      <div className="flex items-center gap-4 text-sm text-gray-400">
                        <span className="flex items-center gap-1">
                          <Calendar size={14} />
                          {new Date(income.date).toLocaleDateString()}
                        </span>
                        {income.note && (
                          <span className="truncate">{income.note}</span>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 flex-shrink-0">
                    <Button
                      onClick={() => onEdit && onEdit(income)}
                      variant="secondary"
                      className="!p-2"
                    >
                      <Edit2 size={16} />
                    </Button>
                    <Button
                      onClick={() => handleDelete(income.id)}
                      variant="secondary"
                      className="!p-2 hover:!bg-red-500/20 hover:!text-red-400"
                    >
                      <Trash2 size={16} />
                    </Button>
                  </div>
                </div>
              </GlassCard>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
}
