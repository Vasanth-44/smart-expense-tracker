import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area, AreaChart } from 'recharts';
import { TrendingUp, TrendingDown, Activity, AlertCircle } from 'lucide-react';
import axios from 'axios';

const ForecastDashboard = () => {
  const [forecastData, setForecastData] = useState(null);
  const [categoryForecast, setCategoryForecast] = useState(null);
  const [trendData, setTrendData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchForecastData();
  }, []);

  const fetchForecastData = async () => {
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };

      const [nextMonth, byCategory, trend] = await Promise.all([
        axios.get('http://127.0.0.1:8000/forecast/next-month', { headers }),
        axios.get('http://127.0.0.1:8000/forecast/by-category', { headers }),
        axios.get('http://127.0.0.1:8000/forecast/trend', { headers })
      ]);

      setForecastData(nextMonth.data);
      setCategoryForecast(byCategory.data);
      setTrendData(trend.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching forecast:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
      </div>
    );
  }

  // Prepare chart data
  const chartData = forecastData?.historical_data?.map(item => ({
    month: item.month.substring(5),
    amount: item.amount
  })) || [];

  // Add prediction to chart
  if (forecastData) {
    chartData.push({
      month: 'Next',
      amount: forecastData.prediction,
      isPrediction: true
    });
  }

  const confidenceColor = {
    high: 'text-green-400',
    medium: 'text-yellow-400',
    low: 'text-orange-400'
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 p-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-7xl mx-auto"
      >
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Expense Forecast</h1>
          <p className="text-gray-400">AI-powered predictions for your future spending</p>
        </div>

        {/* Main Prediction Card */}
        <motion.div
          initial={{ scale: 0.95 }}
          animate={{ scale: 1 }}
          className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 mb-6 border border-white/20"
        >
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-2xl font-bold text-white mb-2">
                Next Month Prediction
              </h2>
              <p className="text-gray-300">{forecastData?.next_month}</p>
            </div>
            <div className={`flex items-center gap-2 ${confidenceColor[forecastData?.confidence]}`}>
              <Activity className="w-6 h-6" />
              <span className="font-semibold capitalize">{forecastData?.confidence} Confidence</span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
            <div className="bg-purple-500/20 rounded-xl p-6 border border-purple-500/30">
              <p className="text-gray-300 text-sm mb-2">Lower Bound</p>
              <p className="text-3xl font-bold text-white">₹{forecastData?.lower_bound?.toLocaleString()}</p>
            </div>
            <div className="bg-gradient-to-br from-purple-600 to-pink-600 rounded-xl p-6 shadow-lg">
              <p className="text-white/80 text-sm mb-2">Predicted Amount</p>
              <p className="text-4xl font-bold text-white">₹{forecastData?.prediction?.toLocaleString()}</p>
            </div>
            <div className="bg-purple-500/20 rounded-xl p-6 border border-purple-500/30">
              <p className="text-gray-300 text-sm mb-2">Upper Bound</p>
              <p className="text-3xl font-bold text-white">₹{forecastData?.upper_bound?.toLocaleString()}</p>
            </div>
          </div>

          <div className="mt-6 p-4 bg-blue-500/10 rounded-lg border border-blue-500/30">
            <p className="text-blue-300 flex items-center gap-2">
              <AlertCircle className="w-5 h-5" />
              {forecastData?.message}
            </p>
          </div>
        </motion.div>

        {/* Trend Analysis */}
        {trendData && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 mb-6 border border-white/20"
          >
            <h3 className="text-xl font-bold text-white mb-4">Spending Trend</h3>
            <div className="flex items-center gap-4">
              {trendData.trend === 'increasing' ? (
                <TrendingUp className="w-12 h-12 text-red-400" />
              ) : trendData.trend === 'decreasing' ? (
                <TrendingDown className="w-12 h-12 text-green-400" />
              ) : (
                <Activity className="w-12 h-12 text-blue-400" />
              )}
              <div>
                <p className="text-2xl font-bold text-white capitalize">{trendData.trend}</p>
                <p className="text-gray-300">{trendData.message}</p>
                <p className="text-sm text-gray-400 mt-1">
                  Change: {trendData.change_percent > 0 ? '+' : ''}{trendData.change_percent}%
                </p>
              </div>
            </div>
          </motion.div>
        )}

        {/* Historical + Prediction Chart */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 mb-6 border border-white/20"
        >
          <h3 className="text-xl font-bold text-white mb-4">Spending Trend & Forecast</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id="colorAmount" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#ffffff20" />
              <XAxis dataKey="month" stroke="#fff" />
              <YAxis stroke="#fff" />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'rgba(0,0,0,0.8)',
                  border: '1px solid rgba(255,255,255,0.2)',
                  borderRadius: '8px'
                }}
              />
              <Area
                type="monotone"
                dataKey="amount"
                stroke="#8b5cf6"
                strokeWidth={3}
                fillOpacity={1}
                fill="url(#colorAmount)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Category Forecast */}
        {categoryForecast?.categories?.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20"
          >
            <h3 className="text-xl font-bold text-white mb-4">Category-wise Forecast</h3>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={categoryForecast.categories}>
                <CartesianGrid strokeDasharray="3 3" stroke="#ffffff20" />
                <XAxis dataKey="category" stroke="#fff" />
                <YAxis stroke="#fff" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'rgba(0,0,0,0.8)',
                    border: '1px solid rgba(255,255,255,0.2)',
                    borderRadius: '8px'
                  }}
                />
                <Legend />
                <Bar dataKey="prediction" fill="#8b5cf6" name="Predicted" radius={[8, 8, 0, 0]} />
                <Bar dataKey="historical_average" fill="#ec4899" name="Historical Avg" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>

            <div className="mt-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {categoryForecast.categories.slice(0, 6).map((cat, idx) => (
                <div key={idx} className="bg-white/5 rounded-lg p-4 border border-white/10">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-white font-semibold">{cat.category}</span>
                    <span className={`text-sm ${cat.trend === 'increasing' ? 'text-red-400' : 'text-green-400'}`}>
                      {cat.trend === 'increasing' ? '↑' : '↓'}
                    </span>
                  </div>
                  <p className="text-2xl font-bold text-purple-400">₹{cat.prediction.toLocaleString()}</p>
                  <p className="text-sm text-gray-400">Avg: ₹{cat.historical_average.toLocaleString()}</p>
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </motion.div>
    </div>
  );
};

export default ForecastDashboard;
