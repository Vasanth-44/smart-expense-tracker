import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Target, TrendingUp, Calendar, DollarSign, CheckCircle, AlertCircle, Plus } from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';

const GoalsPlanner = () => {
  const [goals, setGoals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);

  useEffect(() => {
    fetchGoals();
  }, []);

  const fetchGoals = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('http://127.0.0.1:8000/goals', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setGoals(response.data.goals);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching goals:', error);
      setLoading(false);
    }
  };

  const handleAddGoal = async (goalData) => {
    try {
      const token = localStorage.getItem('token');
      await axios.post('http://127.0.0.1:8000/goals', goalData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Goal created successfully!');
      fetchGoals();
      setShowForm(false);
    } catch (error) {
      toast.error('Failed to create goal');
      console.error('Error creating goal:', error);
    }
  };

  const handleUpdateProgress = async (goalId, currentAmount) => {
    try {
      const token = localStorage.getItem('token');
      const goal = goals.find(g => g.goal.id === goalId);
      await axios.put(`http://127.0.0.1:8000/goals/${goalId}`, {
        ...goal.goal,
        current_amount: parseFloat(currentAmount)
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Progress updated!');
      fetchGoals();
    } catch (error) {
      toast.error('Failed to update progress');
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
    </div>;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 p-6">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold text-white mb-2">Financial Goals</h1>
            <p className="text-gray-400">Track and achieve your financial objectives</p>
          </div>
          <button onClick={() => setShowForm(true)} className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg text-white font-semibold hover:shadow-lg transition">
            <Plus className="w-5 h-5" />
            New Goal
          </button>
        </div>

        {/* Goals Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {goals.map((goalData, idx) => (
            <GoalCard key={goalData.goal.id} goalData={goalData} onUpdateProgress={handleUpdateProgress} delay={idx * 0.1} />
          ))}
        </div>

        {goals.length === 0 && (
          <div className="text-center py-20">
            <Target className="w-20 h-20 text-gray-600 mx-auto mb-4" />
            <p className="text-gray-400 text-lg">No goals yet. Create your first financial goal!</p>
          </div>
        )}

        {showForm && <GoalForm onClose={() => setShowForm(false)} onSubmit={handleAddGoal} />}
      </motion.div>
    </div>
  );
};

const GoalCard = ({ goalData, onUpdateProgress, delay }) => {
  const { goal, progress_percent, remaining_amount, days_remaining, required_monthly_savings, average_monthly_savings, on_track, status_message } = goalData;
  const [showUpdateForm, setShowUpdateForm] = useState(false);
  const [newAmount, setNewAmount] = useState(goal.current_amount);

  const handleUpdate = () => {
    onUpdateProgress(goal.id, newAmount);
    setShowUpdateForm(false);
  };

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay }} className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-2xl font-bold text-white mb-1">{goal.name}</h3>
          <span className="px-3 py-1 bg-purple-500/30 rounded-full text-purple-300 text-sm">{goal.category}</span>
        </div>
        <div className={`flex items-center gap-2 px-3 py-1 rounded-full ${on_track ? 'bg-green-500/20 text-green-300' : 'bg-orange-500/20 text-orange-300'}`}>
          {on_track ? <CheckCircle className="w-4 h-4" /> : <AlertCircle className="w-4 h-4" />}
          <span className="text-sm font-semibold">{status_message}</span>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-gray-300 text-sm">Progress</span>
          <span className="text-white font-bold">{progress_percent}%</span>
        </div>
        <div className="w-full bg-gray-700 rounded-full h-4 overflow-hidden">
          <motion.div initial={{ width: 0 }} animate={{ width: `${progress_percent}%` }} transition={{ duration: 1, delay: delay + 0.2 }} className="bg-gradient-to-r from-purple-500 to-pink-500 h-4 rounded-full"></motion.div>
        </div>
        <div className="flex items-center justify-between mt-2">
          <span className="text-gray-400 text-sm">₹{goal.current_amount.toLocaleString()}</span>
          <span className="text-gray-400 text-sm">₹{goal.target_amount.toLocaleString()}</span>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="bg-white/5 rounded-lg p-3">
          <div className="flex items-center gap-2 mb-1">
            <DollarSign className="w-4 h-4 text-purple-400" />
            <span className="text-gray-400 text-xs">Remaining</span>
          </div>
          <p className="text-white font-bold">₹{remaining_amount.toLocaleString()}</p>
        </div>
        <div className="bg-white/5 rounded-lg p-3">
          <div className="flex items-center gap-2 mb-1">
            <Calendar className="w-4 h-4 text-blue-400" />
            <span className="text-gray-400 text-xs">Days Left</span>
          </div>
          <p className="text-white font-bold">{days_remaining}</p>
        </div>
        <div className="bg-white/5 rounded-lg p-3">
          <div className="flex items-center gap-2 mb-1">
            <Target className="w-4 h-4 text-green-400" />
            <span className="text-gray-400 text-xs">Required/Month</span>
          </div>
          <p className="text-white font-bold">₹{required_monthly_savings.toLocaleString()}</p>
        </div>
        <div className="bg-white/5 rounded-lg p-3">
          <div className="flex items-center gap-2 mb-1">
            <TrendingUp className="w-4 h-4 text-yellow-400" />
            <span className="text-gray-400 text-xs">Avg Savings</span>
          </div>
          <p className="text-white font-bold">₹{average_monthly_savings.toLocaleString()}</p>
        </div>
      </div>

      {/* Update Button */}
      {!showUpdateForm ? (
        <button onClick={() => setShowUpdateForm(true)} className="w-full px-4 py-2 bg-purple-500 hover:bg-purple-600 rounded-lg text-white transition">
          Update Progress
        </button>
      ) : (
        <div className="flex gap-2">
          <input type="number" value={newAmount} onChange={(e) => setNewAmount(e.target.value)} className="flex-1 px-4 py-2 bg-gray-700 text-white rounded-lg" placeholder="Current amount" />
          <button onClick={handleUpdate} className="px-4 py-2 bg-green-500 hover:bg-green-600 rounded-lg text-white transition">Save</button>
          <button onClick={() => setShowUpdateForm(false)} className="px-4 py-2 bg-gray-600 hover:bg-gray-700 rounded-lg text-white transition">Cancel</button>
        </div>
      )}
    </motion.div>
  );
};

const GoalForm = ({ onClose, onSubmit }) => {
  const [formData, setFormData] = useState({
    name: '',
    target_amount: '',
    deadline: '',
    category: 'Savings'
  });

  const categories = ['Savings', 'Emergency Fund', 'Vacation', 'House', 'Car', 'Education', 'Retirement', 'Other'];

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({ ...formData, target_amount: parseFloat(formData.target_amount) });
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
      <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="bg-gray-800 rounded-2xl p-6 max-w-md w-full mx-4">
        <h3 className="text-2xl font-bold text-white mb-4">Create Financial Goal</h3>
        <form onSubmit={handleSubmit} className="space-y-4">
          <input type="text" placeholder="Goal Name" value={formData.name} onChange={(e) => setFormData({ ...formData, name: e.target.value })} className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg" required />
          <input type="number" placeholder="Target Amount" value={formData.target_amount} onChange={(e) => setFormData({ ...formData, target_amount: e.target.value })} className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg" required />
          <select value={formData.category} onChange={(e) => setFormData({ ...formData, category: e.target.value })} className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg">
            {categories.map(cat => <option key={cat} value={cat}>{cat}</option>)}
          </select>
          <input type="date" value={formData.deadline} onChange={(e) => setFormData({ ...formData, deadline: e.target.value })} className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg" required />
          <div className="flex gap-3">
            <button type="submit" className="flex-1 px-4 py-2 bg-purple-500 hover:bg-purple-600 rounded-lg text-white transition">Create Goal</button>
            <button type="button" onClick={onClose} className="flex-1 px-4 py-2 bg-gray-600 hover:bg-gray-700 rounded-lg text-white transition">Cancel</button>
          </div>
        </form>
      </motion.div>
    </div>
  );
};

export default GoalsPlanner;
