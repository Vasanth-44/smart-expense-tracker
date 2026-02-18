import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { TrendingUp, TrendingDown, DollarSign, CreditCard, PiggyBank, Target } from 'lucide-react';
import axios from 'axios';
import CountUp from 'react-countup';

const NetWorthDashboard = () => {
  const [netWorthData, setNetWorthData] = useState(null);
  const [assets, setAssets] = useState([]);
  const [liabilities, setLiabilities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAssetForm, setShowAssetForm] = useState(false);
  const [showLiabilityForm, setShowLiabilityForm] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };

      const [networth, assetsRes, liabilitiesRes] = await Promise.all([
        axios.get('http://127.0.0.1:8000/networth/dashboard', { headers }),
        axios.get('http://127.0.0.1:8000/assets', { headers }),
        axios.get('http://127.0.0.1:8000/liabilities', { headers })
      ]);

      setNetWorthData(networth.data);
      setAssets(assetsRes.data);
      setLiabilities(liabilitiesRes.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching net worth data:', error);
      setLoading(false);
    }
  };

  const handleAddAsset = async (assetData) => {
    try {
      const token = localStorage.getItem('token');
      await axios.post('http://127.0.0.1:8000/assets', assetData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchData();
      setShowAssetForm(false);
    } catch (error) {
      console.error('Error adding asset:', error);
    }
  };

  const handleAddLiability = async (liabilityData) => {
    try {
      const token = localStorage.getItem('token');
      await axios.post('http://127.0.0.1:8000/liabilities', liabilityData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchData();
      setShowLiabilityForm(false);
    } catch (error) {
      console.error('Error adding liability:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
      </div>
    );
  }

  // Prepare pie chart data
  const assetChartData = Object.entries(netWorthData?.assets_breakdown || {}).map(([name, value]) => ({
    name,
    value
  }));

  const liabilityChartData = Object.entries(netWorthData?.liabilities_breakdown || {}).map(([name, value]) => ({
    name,
    value
  }));

  const COLORS = ['#8b5cf6', '#ec4899', '#3b82f6', '#10b981', '#f59e0b', '#ef4444'];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 p-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-7xl mx-auto"
      >
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Net Worth Dashboard</h1>
          <p className="text-gray-400">Track your complete financial picture</p>
        </div>

        {/* Main Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Net Worth */}
          <motion.div
            whileHover={{ scale: 1.02 }}
            className="bg-gradient-to-br from-purple-600 to-pink-600 rounded-2xl p-6 shadow-2xl"
          >
            <div className="flex items-center justify-between mb-2">
              <DollarSign className="w-8 h-8 text-white" />
              {netWorthData?.growth_direction === 'up' ? (
                <TrendingUp className="w-6 h-6 text-green-300" />
              ) : (
                <TrendingDown className="w-6 h-6 text-red-300" />
              )}
            </div>
            <p className="text-white/80 text-sm mb-1">Net Worth</p>
            <p className="text-4xl font-bold text-white">
              ₹<CountUp end={netWorthData?.net_worth || 0} duration={2} separator="," />
            </p>
            <p className="text-sm text-white/70 mt-2">
              {netWorthData?.monthly_growth > 0 ? '+' : ''}{netWorthData?.monthly_growth}% this month
            </p>
          </motion.div>

          {/* Total Assets */}
          <motion.div
            whileHover={{ scale: 1.02 }}
            className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20"
          >
            <PiggyBank className="w-8 h-8 text-green-400 mb-2" />
            <p className="text-gray-300 text-sm mb-1">Total Assets</p>
            <p className="text-3xl font-bold text-white">
              ₹<CountUp end={netWorthData?.total_assets || 0} duration={2} separator="," />
            </p>
          </motion.div>

          {/* Total Liabilities */}
          <motion.div
            whileHover={{ scale: 1.02 }}
            className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20"
          >
            <CreditCard className="w-8 h-8 text-red-400 mb-2" />
            <p className="text-gray-300 text-sm mb-1">Total Liabilities</p>
            <p className="text-3xl font-bold text-white">
              ₹<CountUp end={netWorthData?.total_liabilities || 0} duration={2} separator="," />
            </p>
          </motion.div>

          {/* Savings Rate */}
          <motion.div
            whileHover={{ scale: 1.02 }}
            className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20"
          >
            <Target className="w-8 h-8 text-blue-400 mb-2" />
            <p className="text-gray-300 text-sm mb-1">Savings Rate</p>
            <p className="text-3xl font-bold text-white">
              <CountUp end={netWorthData?.savings_rate || 0} duration={2} decimals={1} />%
            </p>
          </motion.div>
        </div>

        {/* Cash Flow Summary */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 mb-8 border border-white/20"
        >
          <h3 className="text-xl font-bold text-white mb-4">Monthly Cash Flow - {netWorthData?.month}</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-green-500/20 rounded-xl p-4 border border-green-500/30">
              <p className="text-green-300 text-sm mb-1">Income</p>
              <p className="text-2xl font-bold text-white">₹{netWorthData?.monthly_income?.toLocaleString()}</p>
            </div>
            <div className="bg-red-500/20 rounded-xl p-4 border border-red-500/30">
              <p className="text-red-300 text-sm mb-1">Expenses</p>
              <p className="text-2xl font-bold text-white">₹{netWorthData?.monthly_expenses?.toLocaleString()}</p>
            </div>
            <div className={`rounded-xl p-4 border ${netWorthData?.monthly_net >= 0 ? 'bg-blue-500/20 border-blue-500/30' : 'bg-orange-500/20 border-orange-500/30'}`}>
              <p className={`text-sm mb-1 ${netWorthData?.monthly_net >= 0 ? 'text-blue-300' : 'text-orange-300'}`}>Net</p>
              <p className="text-2xl font-bold text-white">₹{netWorthData?.monthly_net?.toLocaleString()}</p>
            </div>
          </div>
        </motion.div>

        {/* Assets & Liabilities Breakdown */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Assets Breakdown */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20"
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold text-white">Assets Breakdown</h3>
              <button
                onClick={() => setShowAssetForm(true)}
                className="px-4 py-2 bg-green-500 hover:bg-green-600 rounded-lg text-white text-sm transition"
              >
                + Add Asset
              </button>
            </div>
            {assetChartData.length > 0 ? (
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={assetChartData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {assetChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-gray-400 text-center py-8">No assets added yet</p>
            )}
          </motion.div>

          {/* Liabilities Breakdown */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20"
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold text-white">Liabilities Breakdown</h3>
              <button
                onClick={() => setShowLiabilityForm(true)}
                className="px-4 py-2 bg-red-500 hover:bg-red-600 rounded-lg text-white text-sm transition"
              >
                + Add Liability
              </button>
            </div>
            {liabilityChartData.length > 0 ? (
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={liabilityChartData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {liabilityChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-gray-400 text-center py-8">No liabilities added yet</p>
            )}
          </motion.div>
        </div>

        {/* Asset Form Modal */}
        {showAssetForm && (
          <AssetForm onClose={() => setShowAssetForm(false)} onSubmit={handleAddAsset} />
        )}

        {/* Liability Form Modal */}
        {showLiabilityForm && (
          <LiabilityForm onClose={() => setShowLiabilityForm(false)} onSubmit={handleAddLiability} />
        )}
      </motion.div>
    </div>
  );
};

// Asset Form Component
const AssetForm = ({ onClose, onSubmit }) => {
  const [formData, setFormData] = useState({
    name: '',
    value: '',
    category: 'Cash',
    date: new Date().toISOString().split('T')[0],
    note: ''
  });

  const categories = ['Cash', 'Investment', 'Property', 'Vehicle', 'Savings', 'Other'];

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({ ...formData, value: parseFloat(formData.value) });
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        className="bg-gray-800 rounded-2xl p-6 max-w-md w-full mx-4"
      >
        <h3 className="text-2xl font-bold text-white mb-4">Add Asset</h3>
        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="text"
            placeholder="Asset Name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg"
            required
          />
          <input
            type="number"
            placeholder="Value"
            value={formData.value}
            onChange={(e) => setFormData({ ...formData, value: e.target.value })}
            className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg"
            required
          />
          <select
            value={formData.category}
            onChange={(e) => setFormData({ ...formData, category: e.target.value })}
            className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg"
          >
            {categories.map(cat => <option key={cat} value={cat}>{cat}</option>)}
          </select>
          <input
            type="date"
            value={formData.date}
            onChange={(e) => setFormData({ ...formData, date: e.target.value })}
            className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg"
          />
          <textarea
            placeholder="Note (optional)"
            value={formData.note}
            onChange={(e) => setFormData({ ...formData, note: e.target.value })}
            className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg"
            rows="2"
          />
          <div className="flex gap-3">
            <button type="submit" className="flex-1 px-4 py-2 bg-green-500 hover:bg-green-600 rounded-lg text-white transition">
              Add Asset
            </button>
            <button type="button" onClick={onClose} className="flex-1 px-4 py-2 bg-gray-600 hover:bg-gray-700 rounded-lg text-white transition">
              Cancel
            </button>
          </div>
        </form>
      </motion.div>
    </div>
  );
};

// Liability Form Component
const LiabilityForm = ({ onClose, onSubmit }) => {
  const [formData, setFormData] = useState({
    name: '',
    amount: '',
    category: 'Loan',
    interest_rate: '0',
    date: new Date().toISOString().split('T')[0],
    note: ''
  });

  const categories = ['Loan', 'Credit Card', 'Mortgage', 'Personal Loan', 'Other'];

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({
      ...formData,
      amount: parseFloat(formData.amount),
      interest_rate: parseFloat(formData.interest_rate)
    });
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        className="bg-gray-800 rounded-2xl p-6 max-w-md w-full mx-4"
      >
        <h3 className="text-2xl font-bold text-white mb-4">Add Liability</h3>
        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="text"
            placeholder="Liability Name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg"
            required
          />
          <input
            type="number"
            placeholder="Amount"
            value={formData.amount}
            onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
            className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg"
            required
          />
          <select
            value={formData.category}
            onChange={(e) => setFormData({ ...formData, category: e.target.value })}
            className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg"
          >
            {categories.map(cat => <option key={cat} value={cat}>{cat}</option>)}
          </select>
          <input
            type="number"
            step="0.1"
            placeholder="Interest Rate (%)"
            value={formData.interest_rate}
            onChange={(e) => setFormData({ ...formData, interest_rate: e.target.value })}
            className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg"
          />
          <input
            type="date"
            value={formData.date}
            onChange={(e) => setFormData({ ...formData, date: e.target.value })}
            className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg"
          />
          <textarea
            placeholder="Note (optional)"
            value={formData.note}
            onChange={(e) => setFormData({ ...formData, note: e.target.value })}
            className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg"
            rows="2"
          />
          <div className="flex gap-3">
            <button type="submit" className="flex-1 px-4 py-2 bg-red-500 hover:bg-red-600 rounded-lg text-white transition">
              Add Liability
            </button>
            <button type="button" onClick={onClose} className="flex-1 px-4 py-2 bg-gray-600 hover:bg-gray-700 rounded-lg text-white transition">
              Cancel
            </button>
          </div>
        </form>
      </motion.div>
    </div>
  );
};

export default NetWorthDashboard;
