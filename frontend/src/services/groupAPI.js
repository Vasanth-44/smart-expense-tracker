import axios from 'axios';

const API_URL = 'http://localhost:8000';

const getAuthHeader = () => {
  const token = localStorage.getItem('token');
  return { Authorization: `Bearer ${token}` };
};

export const groupAPI = {
  // Group management
  createGroup: (data) => 
    axios.post(`${API_URL}/groups/create`, data, { headers: getAuthHeader() }),
  
  listGroups: () => 
    axios.get(`${API_URL}/groups/list`, { headers: getAuthHeader() }),
  
  getGroup: (groupId) => 
    axios.get(`${API_URL}/groups/${groupId}`, { headers: getAuthHeader() }),
  
  deleteGroup: (groupId) => 
    axios.delete(`${API_URL}/groups/${groupId}`, { headers: getAuthHeader() }),
  
  // Invitations
  inviteMember: (groupId, email) => 
    axios.post(`${API_URL}/groups/${groupId}/invite`, { email }, { headers: getAuthHeader() }),
  
  joinGroup: (token) => 
    axios.post(`${API_URL}/groups/join`, { token }, { headers: getAuthHeader() }),
  
  // Group expenses
  getGroupExpenses: (groupId) => 
    axios.get(`${API_URL}/groups/${groupId}/expenses`, { headers: getAuthHeader() }),
  
  // Members
  removeMember: (groupId, memberId) => 
    axios.delete(`${API_URL}/groups/${groupId}/members/${memberId}`, { headers: getAuthHeader() }),
  
  updateMemberRole: (groupId, memberId, role) => 
    axios.put(`${API_URL}/groups/${groupId}/members/${memberId}/role`, { role }, { headers: getAuthHeader() }),
};

export const splitAPI = {
  // Expense splitting
  splitExpense: (expenseId, splitData) => 
    axios.post(`${API_URL}/expenses/${expenseId}/split`, splitData, { headers: getAuthHeader() }),
  
  settleSplit: (splitId) => 
    axios.post(`${API_URL}/splits/${splitId}/settle`, {}, { headers: getAuthHeader() }),
  
  getGroupBalances: (groupId) => 
    axios.get(`${API_URL}/groups/${groupId}/balances`, { headers: getAuthHeader() }),
  
  getMySplits: () => 
    axios.get(`${API_URL}/splits/my-splits`, { headers: getAuthHeader() }),
};

export const subscriptionAPI = {
  // Subscription management
  getStatus: () => 
    axios.get(`${API_URL}/subscription/status`, { headers: getAuthHeader() }),
  
  subscribe: (planType = 'pro') => 
    axios.post(`${API_URL}/subscribe`, { plan_type: planType }, { headers: getAuthHeader() }),
  
  cancel: () => 
    axios.post(`${API_URL}/subscription/cancel`, {}, { headers: getAuthHeader() }),
  
  getPaymentMethods: () => 
    axios.get(`${API_URL}/subscription/payment-methods`, { headers: getAuthHeader() }),
};

export const adminAPI = {
  // Admin endpoints
  getUsers: (skip = 0, limit = 100) => 
    axios.get(`${API_URL}/admin/users?skip=${skip}&limit=${limit}`, { headers: getAuthHeader() }),
  
  getSubscriptionStats: () => 
    axios.get(`${API_URL}/admin/subscriptions`, { headers: getAuthHeader() }),
  
  getRevenueStats: () => 
    axios.get(`${API_URL}/admin/revenue`, { headers: getAuthHeader() }),
  
  getAnalytics: () => 
    axios.get(`${API_URL}/admin/analytics`, { headers: getAuthHeader() }),
  
  getStats: () => 
    axios.get(`${API_URL}/admin/stats`, { headers: getAuthHeader() }),
};
