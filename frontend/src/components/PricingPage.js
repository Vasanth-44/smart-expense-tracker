import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Check, Zap, Crown, ArrowRight } from 'lucide-react';
import { subscriptionAPI } from '../services/groupAPI';
import GlassCard from './ui/GlassCard';
import Button from './ui/Button';
import { useSubscription } from '../context/SubscriptionContext';
import toast from 'react-hot-toast';

export default function PricingPage() {
  const { subscription, isPro, refresh } = useSubscription();
  const [loading, setLoading] = useState(false);

  const handleUpgrade = async () => {
    setLoading(true);
    try {
      const res = await subscriptionAPI.subscribe('pro');
      
      if (res.data.checkout_url) {
        toast.success('Redirecting to payment...');
        // In production, redirect to actual payment gateway
        // window.location.href = res.data.checkout_url;
        
        // For demo, show message
        toast('Payment integration not configured. This is a demo.', {
          icon: '💳',
          duration: 5000
        });
      }
    } catch (error) {
      console.error('Error upgrading:', error);
      toast.error('Failed to initiate upgrade');
    } finally {
      setLoading(false);
    }
  };

  const plans = [
    {
      name: 'FREE',
      price: '₹0',
      period: 'forever',
      description: 'Perfect for getting started',
      icon: Zap,
      color: 'from-gray-500 to-gray-600',
      features: [
        'Basic expense tracking',
        'Budget management',
        'AI categorization',
        '1 month forecasting',
        'Up to 3 financial goals',
        'Basic analytics',
        'CSV import/export',
        'SMS auto-import'
      ],
      limitations: [
        'No group finance',
        'Limited insights',
        'No anomaly detection',
        'No advanced analytics'
      ]
    },
    {
      name: 'PRO',
      price: '₹999',
      period: 'per month',
      description: 'For power users and teams',
      icon: Crown,
      color: 'from-indigo-500 to-purple-600',
      popular: true,
      features: [
        'Everything in FREE',
        'Group/household finance',
        'Expense splitting',
        'Unlimited forecasting (12 months)',
        'Unlimited financial goals',
        'Advanced AI insights',
        'Anomaly detection',
        'Behavioral analysis',
        'Financial health score',
        'Net worth tracking',
        'Priority support'
      ],
      limitations: []
    }
  ];

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center">
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-4xl md:text-5xl font-bold text-white mb-4"
        >
          Choose Your Plan
        </motion.h1>
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="text-xl text-gray-400"
        >
          Unlock powerful features to take control of your finances
        </motion.p>
      </div>

      {/* Current Plan Badge */}
      {subscription && (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center"
        >
          <div className="inline-flex items-center gap-2 px-6 py-3 bg-indigo-500/20 border border-indigo-500/30 rounded-full">
            <Crown className="text-indigo-400" size={20} />
            <span className="text-white font-medium">
              Current Plan: <span className="text-indigo-400 uppercase">{subscription.plan_type}</span>
            </span>
          </div>
        </motion.div>
      )}

      {/* Pricing Cards */}
      <div className="grid md:grid-cols-2 gap-8">
        {plans.map((plan, index) => {
          const Icon = plan.icon;
          const isCurrentPlan = subscription?.plan_type?.toLowerCase() === plan.name.toLowerCase();
          
          return (
            <motion.div
              key={plan.name}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="relative"
            >
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2 z-10">
                  <div className="px-4 py-1 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-full text-white text-sm font-medium">
                    Most Popular
                  </div>
                </div>
              )}

              <GlassCard className={`h-full ${plan.popular ? 'border-2 border-indigo-500/50' : ''}`}>
                <div className="space-y-6">
                  {/* Header */}
                  <div>
                    <div className={`inline-flex p-3 rounded-xl bg-gradient-to-br ${plan.color} mb-4`}>
                      <Icon className="text-white" size={28} />
                    </div>
                    <h3 className="text-2xl font-bold text-white mb-2">{plan.name}</h3>
                    <p className="text-gray-400">{plan.description}</p>
                  </div>

                  {/* Price */}
                  <div>
                    <div className="flex items-baseline gap-2">
                      <span className="text-5xl font-bold text-white">{plan.price}</span>
                      <span className="text-gray-400">/ {plan.period}</span>
                    </div>
                  </div>

                  {/* Features */}
                  <div className="space-y-3">
                    {plan.features.map((feature, i) => (
                      <div key={i} className="flex items-start gap-3">
                        <Check className="text-green-400 flex-shrink-0 mt-0.5" size={20} />
                        <span className="text-gray-300">{feature}</span>
                      </div>
                    ))}
                  </div>

                  {/* CTA Button */}
                  <div className="pt-4">
                    {isCurrentPlan ? (
                      <Button disabled className="w-full">
                        Current Plan
                      </Button>
                    ) : plan.name === 'PRO' ? (
                      <Button
                        onClick={handleUpgrade}
                        loading={loading}
                        className="w-full bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700"
                      >
                        Upgrade to PRO
                        <ArrowRight size={20} className="ml-2" />
                      </Button>
                    ) : (
                      <Button variant="secondary" disabled className="w-full">
                        Current Plan
                      </Button>
                    )}
                  </div>
                </div>
              </GlassCard>
            </motion.div>
          );
        })}
      </div>

      {/* FAQ Section */}
      <GlassCard>
        <h2 className="text-2xl font-bold text-white mb-6">Frequently Asked Questions</h2>
        <div className="space-y-4">
          <div>
            <h3 className="text-lg font-semibold text-white mb-2">Can I cancel anytime?</h3>
            <p className="text-gray-400">
              Yes! You can cancel your PRO subscription at any time. You'll continue to have access until the end of your billing period.
            </p>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white mb-2">What payment methods do you accept?</h3>
            <p className="text-gray-400">
              We accept all major credit/debit cards, UPI, and net banking through our secure payment partners.
            </p>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white mb-2">Is my data secure?</h3>
            <p className="text-gray-400">
              Absolutely! We use bank-level encryption and never share your financial data with third parties.
            </p>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white mb-2">Can I upgrade from FREE to PRO later?</h3>
            <p className="text-gray-400">
              Yes! You can upgrade to PRO at any time. All your existing data will be preserved.
            </p>
          </div>
        </div>
      </GlassCard>
    </div>
  );
}
