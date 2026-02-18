import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, TrendingUp, TrendingDown, AlertCircle, CheckCircle, Activity } from 'lucide-react';
import axios from 'axios';

const InsightsDashboard = () => {
  const [anomalies, setAnomalies] = useState(null);
  const [insights, setInsights] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchInsights();
  }, []);

  const fetchInsights = async () => {
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };

      const [anomaliesRes, insightsRes] = await Promise.all([
        axios.get('http://127.0.0.1:8000/anomalies/all', { headers }),
        axios.get('http://127.0.0.1:8000/insights/behavioral', { headers })
      ]);

      setAnomalies(anomaliesRes.data);
      setInsights(insightsRes.data.insights);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching insights:', error);
      setLoading(false);
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
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Financial Insights</h1>
          <p className="text-gray-400">AI-powered analysis of your spending patterns</p>
        </div>

        {/* Anomaly Summary */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <motion.div whileHover={{ scale: 1.02 }} className="bg-gradient-to-br from-red-600 to-orange-600 rounded-2xl p-6 shadow-2xl">
            <AlertTriangle className="w-8 h-8 text-white mb-2" />
            <p className="text-white/80 text-sm mb-1">Total Anomalies</p>
            <p className="text-4xl font-bold text-white">{anomalies?.total_anomalies || 0}</p>
          </motion.div>
          <motion.div whileHover={{ scale: 1.02 }} className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
            <AlertCircle className="w-8 h-8 text-red-400 mb-2" />
            <p className="text-gray-300 text-sm mb-1">High Severity</p>
            <p className="text-3xl font-bold text-white">{anomalies?.high_severity || 0}</p>
          </motion.div>
          <motion.div whileHover={{ scale: 1.02 }} className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
            <Activity className="w-8 h-8 text-yellow-400 mb-2" />
            <p className="text-gray-300 text-sm mb-1">Medium Severity</p>
            <p className="text-3xl font-bold text-white">{anomalies?.medium_severity || 0}</p>
          </motion.div>
        </div>

        {/* Behavioral Insights */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 mb-6 border border-white/20">
          <h3 className="text-xl font-bold text-white mb-4">Behavioral Insights</h3>
          <div className="space-y-3">
            {insights.map((insight, idx) => (
              <motion.div key={idx} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: idx * 0.05 }} className={`p-4 rounded-lg border ${insight.type === 'budget_exceeded' ? 'bg-red-500/10 border-red-500/30' : insight.type === 'increase' ? 'bg-orange-500/10 border-orange-500/30' : 'bg-green-500/10 border-green-500/30'}`}>
                <p className="text-white">{insight.message}</p>
                {insight.category && (
                  <div className="mt-2 flex items-center gap-4 text-sm">
                    {insight.current_amount && <span className="text-gray-300">Current: ₹{insight.current_amount.toLocaleString()}</span>}
                    {insight.previous_amount && <span className="text-gray-400">Previous: ₹{insight.previous_amount.toLocaleString()}</span>}
                  </div>
                )}
              </motion.div>
            ))}
            {insights.length === 0 && (
              <div className="text-center py-8">
                <CheckCircle className="w-12 h-12 text-green-400 mx-auto mb-2" />
                <p className="text-gray-400">No unusual patterns detected. Great job!</p>
              </div>
            )}
          </div>
        </motion.div>

        {/* Unusual Transactions */}
        {anomalies?.unusual_transactions?.length > 0 && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 mb-6 border border-white/20">
            <h3 className="text-xl font-bold text-white mb-4">Unusual Transactions</h3>
            <div className="space-y-3">
              {anomalies.unusual_transactions.map((transaction, idx) => (
                <div key={idx} className={`p-4 rounded-lg border ${transaction.severity === 'high' ? 'bg-red-500/10 border-red-500/30' : 'bg-yellow-500/10 border-yellow-500/30'}`}>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-white font-semibold">₹{transaction.amount.toLocaleString()}</span>
                    <span className={`px-2 py-1 rounded text-xs ${transaction.severity === 'high' ? 'bg-red-500 text-white' : 'bg-yellow-500 text-black'}`}>
                      {transaction.severity.toUpperCase()}
                    </span>
                  </div>
                  <p className="text-gray-300 text-sm">{transaction.category} - {transaction.date}</p>
                  <p className="text-gray-400 text-sm mt-1">{transaction.reason}</p>
                  {transaction.note && <p className="text-gray-500 text-xs mt-1">Note: {transaction.note}</p>}
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Category Anomalies */}
        {anomalies?.category_anomalies?.length > 0 && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 mb-6 border border-white/20">
            <h3 className="text-xl font-bold text-white mb-4">Category Spending Alerts</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {anomalies.category_anomalies.map((cat, idx) => (
                <div key={idx} className="bg-orange-500/10 rounded-lg p-4 border border-orange-500/30">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-white font-semibold">{cat.category}</span>
                    <TrendingUp className="w-5 h-5 text-orange-400" />
                  </div>
                  <p className="text-2xl font-bold text-orange-400">+{cat.percent_increase}%</p>
                  <p className="text-sm text-gray-300 mt-1">₹{cat.current_spending.toLocaleString()} vs ₹{cat.average_spending.toLocaleString()}</p>
                  <p className="text-xs text-gray-400 mt-2">{cat.reason}</p>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Spending Spikes */}
        {anomalies?.spending_spikes?.length > 0 && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }} className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
            <h3 className="text-xl font-bold text-white mb-4">Spending Spikes</h3>
            <div className="space-y-3">
              {anomalies.spending_spikes.map((spike, idx) => (
                <div key={idx} className="bg-red-500/10 rounded-lg p-4 border border-red-500/30">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-white font-semibold">{spike.period}</p>
                      <p className="text-gray-300 text-sm mt-1">{spike.reason}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-2xl font-bold text-red-400">+{spike.percent_increase}%</p>
                      <p className="text-sm text-gray-400">₹{spike.daily_average.toLocaleString()}/day</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </motion.div>
    </div>
  );
};

export default InsightsDashboard;
