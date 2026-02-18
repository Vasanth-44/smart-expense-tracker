import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Edit2, Trash2, Calendar, Tag, Upload } from 'lucide-react';
import { expenseAPI } from '../services/api';
import GlassCard from './ui/GlassCard';
import Button from './ui/Button';
import CSVImport from './CSVImport';
import toast from 'react-hot-toast';

export default function ExpenseList({ refresh, onEdit }) {
  const [expenses, setExpenses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showImport, setShowImport] = useState(false);

  useEffect(() => {
    loadExpenses();
  }, [refresh]);

  const loadExpenses = async () => {
    try {
      const res = await expenseAPI.getAll();
      setExpenses(res.data);
    } catch (error) {
      console.error('Error loading expenses:', error);
      toast.error('Failed to load expenses');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this expense?')) {
      try {
        await expenseAPI.delete(id);
        toast.success('Expense deleted successfully!');
        loadExpenses();
      } catch (error) {
        console.error('Error deleting expense:', error);
        toast.error('Failed to delete expense');
      }
    }
  };

  if (loading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-24 bg-white/5 rounded-2xl animate-pulse" />
        ))}
      </div>
    );
  }

  if (expenses.length === 0) {
    return (
      <GlassCard className="text-center py-12">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
        >
          <div className="text-6xl mb-4">📝</div>
          <h3 className="text-xl font-semibold text-white mb-2">No expenses yet</h3>
          <p className="text-gray-400">Add your first expense to get started</p>
        </motion.div>
      </GlassCard>
    );
  }

  return (
    <div className="space-y-4">
      <GlassCard className="mb-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-indigo-400 rounded-full animate-pulse" />
            <h2 className="text-xl font-semibold text-white">Recent Expenses</h2>
            <span className="ml-2 text-sm text-gray-400">{expenses.length} total</span>
          </div>
          <Button
            onClick={() => setShowImport(true)}
            variant="secondary"
            size="sm"
            icon={Upload}
          >
            Import CSV
          </Button>
        </div>
      </GlassCard>

      <AnimatePresence>
        {expenses.map((expense, index) => (
          <motion.div
            key={expense.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, x: -100 }}
            transition={{ delay: index * 0.05 }}
          >
            <GlassCard className="hover:border-indigo-500/30 transition-all">
              <div className="flex items-center justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="px-3 py-1 text-xs font-medium rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                      {expense.category}
                    </span>
                    <div className="flex items-center gap-1 text-xs text-gray-400">
                      <Calendar size={14} />
                      {new Date(expense.date).toLocaleDateString()}
                    </div>
                  </div>
                  <p className="text-gray-300 text-sm truncate">
                    {expense.note || 'No description'}
                  </p>
                </div>

                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <p className="text-2xl font-bold text-white">
                      ₹{expense.amount.toFixed(2)}
                    </p>
                  </div>

                  <div className="flex gap-2">
                    <Button
                      onClick={() => onEdit(expense)}
                      variant="ghost"
                      size="sm"
                      icon={Edit2}
                      className="text-blue-400 hover:text-blue-300"
                    />
                    <Button
                      onClick={() => handleDelete(expense.id)}
                      variant="ghost"
                      size="sm"
                      icon={Trash2}
                      className="text-red-400 hover:text-red-300"
                    />
                  </div>
                </div>
              </div>
            </GlassCard>
          </motion.div>
        ))}
      </AnimatePresence>

      {/* CSV Import Modal */}
      <CSVImport
        isOpen={showImport}
        onClose={() => setShowImport(false)}
        onSuccess={loadExpenses}
      />
    </div>
  );
}
