import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../services/api';

const SubscriptionContext = createContext();

export const useSubscription = () => {
  const context = useContext(SubscriptionContext);
  if (!context) {
    throw new Error('useSubscription must be used within SubscriptionProvider');
  }
  return context;
};

export const SubscriptionProvider = ({ children }) => {
  const [subscription, setSubscription] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchSubscription = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setLoading(false);
        return;
      }

      const response = await axios.get(`${API_BASE_URL}/subscription/status`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setSubscription(response.data);
    } catch (error) {
      console.error('Error fetching subscription:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSubscription();
  }, []);

  const isPro = () => {
    return subscription?.plan_type === 'pro';
  };

  const isFree = () => {
    return subscription?.plan_type === 'free' || !subscription;
  };

  const hasFeature = (feature) => {
    if (!subscription || !subscription.features) return false;
    return subscription.features[feature] === true;
  };

  const getLimit = (feature) => {
    if (!subscription || !subscription.features) return 0;
    return subscription.features[feature] || 0;
  };

  const refresh = () => {
    fetchSubscription();
  };

  return (
    <SubscriptionContext.Provider
      value={{
        subscription,
        loading,
        isPro,
        isFree,
        hasFeature,
        getLimit,
        refresh
      }}
    >
      {children}
    </SubscriptionContext.Provider>
  );
};
