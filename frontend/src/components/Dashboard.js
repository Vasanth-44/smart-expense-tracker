import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';
import { TrendingUp, TrendingDown, AlertCircle, Sparkles, DollarSign, AlertTriangle, Activity } from 'lucide-react';
import { analyticsAPI, API_BASE_URL } from '../services/api';
import axios from 'axios';
import GlassCard from './ui/GlassCard';
const COLORS = ['#6366f1', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#3b82f6', '#14b8a6'];

export default function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [insights, setInsights] = useState([]);
  const [prediction, setPrediction] = useState(null);
  const [anomalies, setAnomalies] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const token = localStorage.getItem('token');
      const [summaryRes, insightsRes, predictionRes, anomaliesRes] = await Promise.all([
        analyticsAPI.getSummary(),
        analyticsAPI.getInsights(),
        axios.get(`${API_BASE_URL}/ml/predict-next-month`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get(`${API_BASE_URL}/ml/anomalies`, {
          headers: { Authorization: `Bearer ${token}` }
        })
      ]);
      setSummary(summaryRes.data);
      setInsights(insightsRes.data.insights);
      setPrediction(predictionRes.data);
      setAnomalies(anomaliesRes.data);
    } catch (error) {
      console.error('Error loading dashboard:', error);
      // Show error message if API is not available
      if (error.code === 'ERR_NETWORK' || error.message?.includes('Network Error')) {
        console.error('Backend API is not reachable. Please check:', API_BASE_URL);
      }
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <div key={i} className="h-64 bg-white/5 rounded-2xl animate-pulse" />
        ))}
      </div>
    );
  }

  if (!summary) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-400">No data available</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Total Balance Card */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="relative overflow-hidden"
      >
        <div className="absolute inset-0 bg-gradient-to-r from-indigo-500/20 via-purple-500/20 to-pink-500/20 animate-glow rounded-2xl" />
        <GlassCard className="relative border-indigo-500/30">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm mb-2">Total Spending This Month</p>
              <motion.h2
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="text-5xl font-bold bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent"
              >
                ₹{summary.total_current_month.toFixed(0)}
              </motion.h2>
            </div>
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
              className="w-20 h-20 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center"
            >
              <DollarSign size={40} className="text-white" />
            </motion.div>
          </div>
        </GlassCard>
      </motion.div>

      {/* Budget Alerts */}
      {summary.budget_alerts && summary.budget_alerts.length > 0 && (
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
        >
          <GlassCard className="border-red-500/30 bg-red-500/5">
            <div className="flex items-start gap-3">
              <AlertCircle className="text-red-400 flex-shrink-0 mt-1" size={20} />
              <div className="flex-1">
                <h3 className="text-red-400 font-semibold mb-2">⚠️ Budget Alerts</h3>
                <div className="space-y-2">
                  {summary.budget_alerts.map((alert, idx) => (
                    <motion.div
                      key={idx}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.4 + idx * 0.1 }}
                      className="text-sm text-red-300"
                    >
                      <span className="font-medium">{alert.category}:</span> Exceeded by ₹{alert.exceeded.toFixed(0)}
                    </motion.div>
                  ))}
                </div>
              </div>
            </div>
          </GlassCard>
        </motion.div>
      )}

      {/* ML Prediction Card */}
      {prediction && prediction.predicted_amount > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <GlassCard className="border-purple-500/30 bg-purple-500/5">
            <div className="flex items-start gap-3">
              <Activity className="text-purple-400 flex-shrink-0 mt-1" size={20} />
              <div className="flex-1">
                <h3 className="text-purple-400 font-semibold mb-2">🔮 AI Prediction</h3>
                <div className="space-y-2">
                  <div className="flex items-baseline gap-2">
                    <span className="text-2xl font-bold text-white">
                      ₹{prediction.predicted_amount.toFixed(0)}
                    </span>
                    <span className="text-sm text-gray-400">predicted next month</span>
                  </div>
                  <p className="text-sm text-purple-300">{prediction.trend}</p>
                  <div className="flex items-center gap-2 mt-2">
                    <span className={`px-2 py-1 rounded-full text-xs ${
                      prediction.confidence === 'high' ? 'bg-green-500/20 text-green-300' :
                      prediction.confidence === 'medium' ? 'bg-yellow-500/20 text-yellow-300' :
                      'bg-gray-500/20 text-gray-300'
                    }`}>
                      {prediction.confidence} confidence
                    </span>
                    <span className="text-xs text-gray-400">{prediction.message}</span>
                  </div>
                </div>
              </div>
            </div>
          </GlassCard>
        </motion.div>
      )}

      {/* Anomaly Alerts */}
      {anomalies && anomalies.anomalies && anomalies.anomalies.length > 0 && (
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.5 }}
        >
          <GlassCard className="border-orange-500/30 bg-orange-500/5">
            <div className="flex items-start gap-3">
              <AlertTriangle className="text-orange-400 flex-shrink-0 mt-1" size={20} />
              <div className="flex-1">
                <h3 className="text-orange-400 font-semibold mb-2">🚨 Spending Anomalies Detected</h3>
                <div className="space-y-2">
                  {anomalies.anomalies.slice(0, 3).map((anomaly, idx) => (
                    <motion.div
                      key={idx}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.6 + idx * 0.1 }}
                      className={`p-3 rounded-lg ${
                        anomaly.severity === 'high' ? 'bg-red-500/10 border border-red-500/30' :
                        'bg-orange-500/10 border border-orange-500/30'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-medium text-white">{anomaly.category}</span>
                        <span className={`text-xs px-2 py-0.5 rounded-full ${
                          anomaly.severity === 'high' ? 'bg-red-500/20 text-red-300' :
                          'bg-orange-500/20 text-orange-300'
                        }`}>
                          {anomaly.severity}
                        </span>
                      </div>
                      <p className="text-sm text-gray-300">
                        ₹{anomaly.current_amount.toFixed(0)} vs avg ₹{anomaly.average_amount.toFixed(0)}
                        <span className="text-orange-300 ml-2">
                          (+{anomaly.percentage_increase}%)
                        </span>
                      </p>
                    </motion.div>
                  ))}
                </div>
              </div>
            </div>
          </GlassCard>
        </motion.div>
      )}

      {/* Charts Grid */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Category Breakdown */}
        <GlassCard>
          <h3 className="text-lg font-semibold mb-4 text-white flex items-center gap-2">
            <div className="w-2 h-2 bg-indigo-400 rounded-full animate-pulse" />
            Category Breakdown
          </h3>
          {summary.category_breakdown.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={summary.category_breakdown}
                  dataKey="amount"
                  nameKey="category"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  label={(entry) => `${entry.category}`}
                  animationBegin={0}
                  animationDuration={800}
                >
                  {summary.category_breakdown.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'rgba(15, 23, 42, 0.9)',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    borderRadius: '12px',
                    color: 'white'
                  }}
                  formatter={(value) => `₹${value.toFixed(0)}`}
                />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-gray-400 text-center py-12">No expenses yet</p>
          )}
        </GlassCard>

        {/* Spending Forecast */}
        {prediction && prediction.historical_data && prediction.historical_data.length > 0 && (
          <GlassCard>
            <h3 className="text-lg font-semibold mb-4 text-white flex items-center gap-2">
              <div className="w-2 h-2 bg-purple-400 rounded-full animate-pulse" />
              Spending Forecast
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={[
                ...prediction.historical_data,
                {
                  month: 'Next Month',
                  amount: prediction.predicted_amount,
                  isPrediction: true
                }
              ]}>
                <XAxis
                  dataKey="month"
                  tick={{ fill: '#9ca3af', fontSize: 12 }}
                  axisLine={{ stroke: 'rgba(255, 255, 255, 0.1)' }}
                />
                <YAxis
                  tick={{ fill: '#9ca3af', fontSize: 12 }}
                  axisLine={{ stroke: 'rgba(255, 255, 255, 0.1)' }}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'rgba(15, 23, 42, 0.9)',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    borderRadius: '12px',
                    color: 'white'
                  }}
                  formatter={(value) => `₹${value.toFixed(0)}`}
                />
                <Line
                  type="monotone"
                  dataKey="amount"
                  stroke="#8b5cf6"
                  strokeWidth={2}
                  dot={{ fill: '#8b5cf6', r: 4 }}
                  activeDot={{ r: 6 }}
                  animationBegin={0}
                  animationDuration={1000}
                />
                <defs>
                  <linearGradient id="lineGradient" x1="0" y1="0" x2="1" y2="0">
                    <stop offset="0%" stopColor="#6366f1" />
                    <stop offset="100%" stopColor="#8b5cf6" />
                  </linearGradient>
                </defs>
              </LineChart>
            </ResponsiveContainer>
          </GlassCard>
        )}

        {/* Monthly Trend - only show if no prediction */}
        {(!prediction || !prediction.historical_data || prediction.historical_data.length === 0) && (
          <GlassCard>
            <h3 className="text-lg font-semibold mb-4 text-white flex items-center gap-2">
              <div className="w-2 h-2 bg-purple-400 rounded-full animate-pulse" />
              Monthly Trend
            </h3>
            {summary.monthly_trend.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={summary.monthly_trend}>
                  <XAxis
                    dataKey="month"
                    tick={{ fill: '#9ca3af', fontSize: 12 }}
                    axisLine={{ stroke: 'rgba(255, 255, 255, 0.1)' }}
                  />
                  <YAxis
                    tick={{ fill: '#9ca3af', fontSize: 12 }}
                    axisLine={{ stroke: 'rgba(255, 255, 255, 0.1)' }}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'rgba(15, 23, 42, 0.9)',
                      border: '1px solid rgba(255, 255, 255, 0.1)',
                      borderRadius: '12px',
                      color: 'white'
                    }}
                    formatter={(value) => `₹${value.toFixed(0)}`}
                  />
                  <Bar
                    dataKey="amount"
                    fill="url(#colorGradient)"
                    radius={[8, 8, 0, 0]}
                    animationBegin={0}
                    animationDuration={800}
                  />
                  <defs>
                    <linearGradient id="colorGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#6366f1" />
                      <stop offset="100%" stopColor="#8b5cf6" />
                    </linearGradient>
                  </defs>
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-gray-400 text-center py-12">No data available</p>
            )}
          </GlassCard>
        )}
      </div>

      {/* AI Insights */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
      >
        <GlassCard className="border-purple-500/30">
          <div className="flex items-center gap-2 mb-4">
            <Sparkles className="text-purple-400" size={20} />
            <h3 className="text-lg font-semibold text-white">AI Insights</h3>
          </div>
          <div className="space-y-3">
            {insights.map((insight, idx) => {
              const isWarning = insight.type === 'budget_exceeded' || insight.type === 'increase_alert';
              const Icon = isWarning ? TrendingUp : TrendingDown;
              
              return (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.6 + idx * 0.1 }}
                  className={`
                    p-4 rounded-xl border flex items-start gap-3
                    ${isWarning 
                      ? 'bg-yellow-500/10 border-yellow-500/30' 
                      : 'bg-green-500/10 border-green-500/30'
                    }
                  `}
                >
                  <Icon
                    size={20}
                    className={isWarning ? 'text-yellow-400' : 'text-green-400'}
                  />
                  <p className={`text-sm ${isWarning ? 'text-yellow-200' : 'text-green-200'}`}>
                    {insight.message}
                  </p>
                </motion.div>
              );
            })}
          </div>
        </GlassCard>
      </motion.div>
    </div>
  );
}
