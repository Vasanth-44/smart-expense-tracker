import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Users, DollarSign, TrendingUp, Activity, Crown, UserCheck } from 'lucide-react';
import { adminAPI } from '../services/groupAPI';
import GlassCard from './ui/GlassCard';
import AnimatedCounter from './ui/AnimatedCounter';
import toast from 'react-hot-toast';

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAdminData();
  }, []);

  const loadAdminData = async () => {
    try {
      const [statsRes, analyticsRes, usersRes] = await Promise.all([
        adminAPI.getStats(),
        adminAPI.getAnalytics(),
        adminAPI.getUsers(0, 50)
      ]);

      setStats(statsRes.data);
      setAnalytics(analyticsRes.data);
      setUsers(usersRes.data.users);
    } catch (error) {
      console.error('Error loading admin data:', error);
      if (error.response?.status === 403) {
        toast.error('Admin access required');
      } else {
        toast.error('Failed to load admin data');
      }
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500"></div>
      </div>
    );
  }

  if (!stats) {
    return (
      <GlassCard>
        <div className="text-center py-12">
          <p className="text-xl text-gray-400">Failed to load admin dashboard</p>
        </div>
      </GlassCard>
    );
  }

  const kpiCards = [
    {
      title: 'Total Users',
      value: stats.total_users,
      icon: Users,
      color: 'from-blue-500 to-cyan-500',
      change: analytics?.user_growth?.new_users_last_30_days || 0,
      changeLabel: 'new this month'
    },
    {
      title: 'PRO Users',
      value: stats.pro_users,
      icon: Crown,
      color: 'from-purple-500 to-pink-500',
      change: analytics?.subscription_stats?.conversion_rate || 0,
      changeLabel: 'conversion rate',
      isPercentage: true
    },
    {
      title: 'Monthly Revenue',
      value: stats.monthly_revenue,
      icon: DollarSign,
      color: 'from-green-500 to-emerald-500',
      prefix: '₹',
      change: analytics?.revenue_stats?.new_pro_this_month || 0,
      changeLabel: 'new PRO this month'
    },
    {
      title: 'Total Expenses',
      value: stats.total_expenses,
      icon: Activity,
      color: 'from-orange-500 to-red-500',
      change: stats.total_groups,
      changeLabel: 'active groups'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Admin Dashboard</h1>
          <p className="text-gray-400 mt-1">System overview and analytics</p>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {kpiCards.map((card, index) => {
          const Icon = card.icon;
          return (
            <motion.div
              key={card.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <GlassCard>
                <div className="flex items-start justify-between mb-4">
                  <div className={`p-3 rounded-xl bg-gradient-to-br ${card.color}`}>
                    <Icon className="text-white" size={24} />
                  </div>
                </div>
                <h3 className="text-sm font-medium text-gray-400 mb-1">{card.title}</h3>
                <div className="flex items-baseline gap-2 mb-2">
                  {card.prefix && <span className="text-2xl font-bold text-white">{card.prefix}</span>}
                  <AnimatedCounter
                    value={card.value}
                    className="text-3xl font-bold text-white"
                  />
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <TrendingUp className="text-green-400" size={16} />
                  <span className="text-green-400 font-medium">
                    {card.change}{card.isPercentage ? '%' : ''}
                  </span>
                  <span className="text-gray-400">{card.changeLabel}</span>
                </div>
              </GlassCard>
            </motion.div>
          );
        })}
      </div>

      {/* Subscription Stats */}
      {analytics?.subscription_stats && (
        <GlassCard>
          <h2 className="text-xl font-semibold text-white mb-6">Subscription Overview</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-4 bg-white/5 rounded-xl border border-white/10">
              <div className="flex items-center gap-3 mb-3">
                <Users className="text-gray-400" size={20} />
                <span className="text-gray-400">Free Users</span>
              </div>
              <p className="text-3xl font-bold text-white">
                {analytics.subscription_stats.free_users}
              </p>
            </div>
            <div className="p-4 bg-white/5 rounded-xl border border-white/10">
              <div className="flex items-center gap-3 mb-3">
                <Crown className="text-purple-400" size={20} />
                <span className="text-gray-400">PRO Users</span>
              </div>
              <p className="text-3xl font-bold text-white">
                {analytics.subscription_stats.pro_users}
              </p>
            </div>
            <div className="p-4 bg-white/5 rounded-xl border border-white/10">
              <div className="flex items-center gap-3 mb-3">
                <UserCheck className="text-green-400" size={20} />
                <span className="text-gray-400">Active Subscriptions</span>
              </div>
              <p className="text-3xl font-bold text-white">
                {analytics.subscription_stats.active_subscriptions}
              </p>
            </div>
          </div>
        </GlassCard>
      )}

      {/* Revenue Stats */}
      {analytics?.revenue_stats && (
        <GlassCard>
          <h2 className="text-xl font-semibold text-white mb-6">Revenue Analytics</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="p-6 bg-gradient-to-br from-green-500/10 to-emerald-500/10 rounded-xl border border-green-500/20">
              <p className="text-gray-400 mb-2">Monthly Recurring Revenue</p>
              <p className="text-4xl font-bold text-white mb-1">
                ₹{analytics.revenue_stats.monthly_revenue.toLocaleString()}
              </p>
              <p className="text-sm text-gray-400">
                from {analytics.revenue_stats.active_pro_users} PRO users
              </p>
            </div>
            <div className="p-6 bg-gradient-to-br from-blue-500/10 to-cyan-500/10 rounded-xl border border-blue-500/20">
              <p className="text-gray-400 mb-2">Annual Recurring Revenue</p>
              <p className="text-4xl font-bold text-white mb-1">
                ₹{analytics.revenue_stats.annual_revenue.toLocaleString()}
              </p>
              <p className="text-sm text-gray-400">
                projected annual revenue
              </p>
            </div>
          </div>
        </GlassCard>
      )}

      {/* Recent Users */}
      <GlassCard>
        <h2 className="text-xl font-semibold text-white mb-6">Recent Users</h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-white/10">
                <th className="text-left py-3 px-4 text-gray-400 font-medium">Email</th>
                <th className="text-left py-3 px-4 text-gray-400 font-medium">Plan</th>
                <th className="text-left py-3 px-4 text-gray-400 font-medium">Status</th>
                <th className="text-left py-3 px-4 text-gray-400 font-medium">Joined</th>
              </tr>
            </thead>
            <tbody>
              {users.slice(0, 10).map((user, index) => (
                <motion.tr
                  key={user.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="border-b border-white/5 hover:bg-white/5 transition-colors"
                >
                  <td className="py-3 px-4 text-white">{user.email}</td>
                  <td className="py-3 px-4">
                    <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium ${
                      user.plan_type === 'pro'
                        ? 'bg-purple-500/20 text-purple-400 border border-purple-500/30'
                        : 'bg-gray-500/20 text-gray-400 border border-gray-500/30'
                    }`}>
                      {user.plan_type === 'pro' && <Crown size={12} />}
                      {user.plan_type.toUpperCase()}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <span className="inline-flex px-3 py-1 rounded-full text-xs font-medium bg-green-500/20 text-green-400 border border-green-500/30">
                      {user.subscription_status}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-gray-400">
                    {user.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      </GlassCard>

      {/* Feature Usage */}
      {analytics?.feature_usage && (
        <GlassCard>
          <h2 className="text-xl font-semibold text-white mb-6">Feature Usage</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center p-6 bg-white/5 rounded-xl border border-white/10">
              <Activity className="mx-auto text-indigo-400 mb-3" size={32} />
              <p className="text-3xl font-bold text-white mb-2">
                {analytics.feature_usage.total_expenses}
              </p>
              <p className="text-gray-400">Total Expenses Tracked</p>
            </div>
            <div className="text-center p-6 bg-white/5 rounded-xl border border-white/10">
              <Users className="mx-auto text-purple-400 mb-3" size={32} />
              <p className="text-3xl font-bold text-white mb-2">
                {analytics.feature_usage.total_groups}
              </p>
              <p className="text-gray-400">Groups Created</p>
            </div>
            <div className="text-center p-6 bg-white/5 rounded-xl border border-white/10">
              <UserCheck className="mx-auto text-green-400 mb-3" size={32} />
              <p className="text-3xl font-bold text-white mb-2">
                {analytics.feature_usage.users_with_groups}
              </p>
              <p className="text-gray-400">Users with Groups</p>
            </div>
          </div>
        </GlassCard>
      )}
    </div>
  );
}
