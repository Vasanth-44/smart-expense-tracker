import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { CircularProgressbar, buildStyles } from 'react-circular-progressbar';
import 'react-circular-progressbar/dist/styles.css';
import { Shield, TrendingUp, Target, Activity, DollarSign } from 'lucide-react';
import axios from 'axios';

const FinancialHealthScore = () => {
  const [healthData, setHealthData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchHealthScore();
  }, []);

  const fetchHealthScore = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('http://127.0.0.1:8000/health/score', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setHealthData(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching health score:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
    </div>;
  }

  const colorMap = {
    green: { path: '#10b981', trail: '#10b98120', text: '#10b981' },
    yellow: { path: '#f59e0b', trail: '#f59e0b20', text: '#f59e0b' },
    orange: { path: '#f97316', trail: '#f9731620', text: '#f97316' },
    red: { path: '#ef4444', trail: '#ef444420', text: '#ef4444' }
  };

  const colors = colorMap[healthData?.color] || colorMap.green;

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 p-6">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Financial Health Score</h1>
          <p className="text-gray-400">Comprehensive analysis of your financial wellness</p>
        </div>

        {/* Main Score Card */}
        <motion.div initial={{ scale: 0.95 }} animate={{ scale: 1 }} className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 mb-6 border border-white/20">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="flex flex-col items-center justify-center">
              <div style={{ width: 250, height: 250 }}>
                <CircularProgressbar
                  value={healthData?.score || 0}
                  text={`${healthData?.score || 0}`}
                  styles={buildStyles({
                    pathColor: colors.path,
                    textColor: '#fff',
                    trailColor: colors.trail,
                    textSize: '24px'
                  })}
                />
              </div>
              <div className="mt-6 text-center">
                <p className="text-3xl font-bold text-white">{healthData?.rating}</p>
                <p className="text-gray-400 mt-2">Your Financial Health Rating</p>
              </div>
            </div>

            <div className="space-y-4">
              <h3 className="text-xl font-bold text-white mb-4">Score Breakdown</h3>
              {Object.entries(healthData?.breakdown || {}).map(([key, data]) => (
                <div key={key} className="bg-white/5 rounded-lg p-4 border border-white/10">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-white font-semibold">{data.label}</span>
                    <span className="text-purple-400 font-bold">{data.score}/100</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div className="bg-gradient-to-r from-purple-500 to-pink-500 h-2 rounded-full transition-all duration-500" style={{ width: `${data.score}%` }}></div>
                  </div>
                  <p className="text-xs text-gray-400 mt-1">Weight: {data.weight}%</p>
                </div>
              ))}
            </div>
          </div>
        </motion.div>

        {/* Insights */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
          <h3 className="text-xl font-bold text-white mb-4">Recommendations</h3>
          <div className="space-y-3">
            {healthData?.insights?.map((insight, idx) => (
              <motion.div key={idx} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: idx * 0.1 }} className="bg-white/5 rounded-lg p-4 border border-white/10">
                <p className="text-white">{insight}</p>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
};

export default FinancialHealthScore;
