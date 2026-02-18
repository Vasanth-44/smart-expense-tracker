import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Users, Plus, Settings, TrendingUp, DollarSign, UserPlus, LogOut } from 'lucide-react';
import { groupAPI, splitAPI } from '../services/groupAPI';
import GlassCard from './ui/GlassCard';
import Button from './ui/Button';
import Modal from './ui/Modal';
import toast from 'react-hot-toast';

export default function GroupDashboard() {
  const [groups, setGroups] = useState([]);
  const [selectedGroup, setSelectedGroup] = useState(null);
  const [groupDetails, setGroupDetails] = useState(null);
  const [balances, setBalances] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [newGroupName, setNewGroupName] = useState('');
  const [newGroupDesc, setNewGroupDesc] = useState('');
  const [inviteEmail, setInviteEmail] = useState('');

  useEffect(() => {
    loadGroups();
  }, []);

  useEffect(() => {
    if (selectedGroup) {
      loadGroupDetails(selectedGroup);
      loadBalances(selectedGroup);
    }
  }, [selectedGroup]);

  const loadGroups = async () => {
    try {
      const res = await groupAPI.listGroups();
      setGroups(res.data.groups);
      if (res.data.groups.length > 0 && !selectedGroup) {
        setSelectedGroup(res.data.groups[0].id);
      }
    } catch (error) {
      console.error('Error loading groups:', error);
      if (error.response?.status === 403) {
        toast.error('Upgrade to PRO to use group finance features');
      }
    } finally {
      setLoading(false);
    }
  };

  const loadGroupDetails = async (groupId) => {
    try {
      const res = await groupAPI.getGroup(groupId);
      setGroupDetails(res.data);
    } catch (error) {
      console.error('Error loading group details:', error);
    }
  };

  const loadBalances = async (groupId) => {
    try {
      const res = await splitAPI.getGroupBalances(groupId);
      setBalances(res.data.balances);
    } catch (error) {
      console.error('Error loading balances:', error);
    }
  };

  const handleCreateGroup = async () => {
    if (!newGroupName.trim()) {
      toast.error('Please enter a group name');
      return;
    }

    try {
      await groupAPI.createGroup({
        name: newGroupName,
        description: newGroupDesc
      });
      toast.success('Group created successfully!');
      setShowCreateModal(false);
      setNewGroupName('');
      setNewGroupDesc('');
      loadGroups();
    } catch (error) {
      console.error('Error creating group:', error);
      if (error.response?.status === 403) {
        toast.error('Upgrade to PRO to create groups');
      } else {
        toast.error('Failed to create group');
      }
    }
  };

  const handleInviteMember = async () => {
    if (!inviteEmail.trim()) {
      toast.error('Please enter an email address');
      return;
    }

    try {
      const res = await groupAPI.inviteMember(selectedGroup, inviteEmail);
      toast.success(`Invitation sent to ${inviteEmail}`);
      setShowInviteModal(false);
      setInviteEmail('');
      
      // Show invite link
      const inviteLink = `${window.location.origin}/groups/join?token=${res.data.token}`;
      navigator.clipboard.writeText(inviteLink);
      toast.success('Invite link copied to clipboard!');
    } catch (error) {
      console.error('Error inviting member:', error);
      toast.error(error.response?.data?.detail || 'Failed to send invitation');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500"></div>
      </div>
    );
  }

  if (groups.length === 0) {
    return (
      <GlassCard>
        <div className="text-center py-12">
          <Users className="mx-auto h-16 w-16 text-gray-400 mb-4" />
          <h3 className="text-xl font-semibold text-white mb-2">No Groups Yet</h3>
          <p className="text-gray-400 mb-6">Create your first finance group to get started</p>
          <Button onClick={() => setShowCreateModal(true)}>
            <Plus size={20} className="mr-2" />
            Create Group
          </Button>
        </div>

        <Modal isOpen={showCreateModal} onClose={() => setShowCreateModal(false)} title="Create New Group">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Group Name</label>
              <input
                type="text"
                value={newGroupName}
                onChange={(e) => setNewGroupName(e.target.value)}
                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
                placeholder="e.g., Roommates, Family, Team"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Description (Optional)</label>
              <textarea
                value={newGroupDesc}
                onChange={(e) => setNewGroupDesc(e.target.value)}
                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 resize-none"
                placeholder="What is this group for?"
                rows="3"
              />
            </div>
            <Button onClick={handleCreateGroup} className="w-full">
              Create Group
            </Button>
          </div>
        </Modal>
      </GlassCard>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-white">Group Finance</h1>
        <Button onClick={() => setShowCreateModal(true)}>
          <Plus size={20} className="mr-2" />
          New Group
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Group List */}
        <div className="lg:col-span-1">
          <GlassCard>
            <h2 className="text-xl font-semibold text-white mb-4">Your Groups</h2>
            <div className="space-y-2">
              {groups.map((group) => (
                <motion.button
                  key={group.id}
                  onClick={() => setSelectedGroup(group.id)}
                  whileHover={{ x: 5 }}
                  className={`w-full text-left p-4 rounded-xl transition-all ${
                    selectedGroup === group.id
                      ? 'bg-indigo-500/20 border border-indigo-500/30'
                      : 'bg-white/5 border border-white/10 hover:bg-white/10'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Users size={20} className="text-indigo-400" />
                    <div className="flex-1">
                      <p className="font-medium text-white">{group.name}</p>
                      {group.description && (
                        <p className="text-sm text-gray-400">{group.description}</p>
                      )}
                    </div>
                  </div>
                </motion.button>
              ))}
            </div>
          </GlassCard>
        </div>

        {/* Group Details */}
        <div className="lg:col-span-2 space-y-6">
          {groupDetails && (
            <>
              {/* Group Info */}
              <GlassCard>
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h2 className="text-2xl font-bold text-white">{groupDetails.name}</h2>
                    {groupDetails.description && (
                      <p className="text-gray-400 mt-1">{groupDetails.description}</p>
                    )}
                  </div>
                  <Button onClick={() => setShowInviteModal(true)} variant="secondary">
                    <UserPlus size={20} className="mr-2" />
                    Invite
                  </Button>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 bg-white/5 rounded-xl border border-white/10">
                    <Users className="text-indigo-400 mb-2" size={24} />
                    <p className="text-2xl font-bold text-white">{groupDetails.member_count}</p>
                    <p className="text-sm text-gray-400">Members</p>
                  </div>
                  <div className="p-4 bg-white/5 rounded-xl border border-white/10">
                    <TrendingUp className="text-green-400 mb-2" size={24} />
                    <p className="text-2xl font-bold text-white">{groupDetails.expense_count}</p>
                    <p className="text-sm text-gray-400">Expenses</p>
                  </div>
                </div>
              </GlassCard>

              {/* Members */}
              <GlassCard>
                <h3 className="text-xl font-semibold text-white mb-4">Members</h3>
                <div className="space-y-3">
                  {groupDetails.members.map((member) => (
                    <div
                      key={member.id}
                      className="flex items-center justify-between p-3 bg-white/5 rounded-xl border border-white/10"
                    >
                      <div>
                        <p className="font-medium text-white">{member.email}</p>
                        <p className="text-sm text-gray-400 capitalize">{member.role}</p>
                      </div>
                      {member.role !== 'owner' && groupDetails.user_role === 'owner' && (
                        <Button variant="secondary" size="sm">
                          <Settings size={16} />
                        </Button>
                      )}
                    </div>
                  ))}
                </div>
              </GlassCard>

              {/* Balances */}
              <GlassCard>
                <h3 className="text-xl font-semibold text-white mb-4">Balances</h3>
                <div className="space-y-3">
                  {balances.map((balance) => (
                    <div
                      key={balance.user_id}
                      className="p-4 bg-white/5 rounded-xl border border-white/10"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <p className="font-medium text-white">{balance.email}</p>
                        <div className={`text-lg font-bold ${
                          balance.net_balance > 0 ? 'text-green-400' : 
                          balance.net_balance < 0 ? 'text-red-400' : 'text-gray-400'
                        }`}>
                          ₹{Math.abs(balance.net_balance).toFixed(2)}
                        </div>
                      </div>
                      <div className="flex items-center gap-4 text-sm">
                        <span className="text-green-400">Owed: ₹{balance.total_owed}</span>
                        <span className="text-red-400">Owes: ₹{balance.total_owes}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </GlassCard>
            </>
          )}
        </div>
      </div>

      {/* Modals */}
      <Modal isOpen={showCreateModal} onClose={() => setShowCreateModal(false)} title="Create New Group">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Group Name</label>
            <input
              type="text"
              value={newGroupName}
              onChange={(e) => setNewGroupName(e.target.value)}
              className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
              placeholder="e.g., Roommates, Family, Team"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Description (Optional)</label>
            <textarea
              value={newGroupDesc}
              onChange={(e) => setNewGroupDesc(e.target.value)}
              className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 resize-none"
              placeholder="What is this group for?"
              rows="3"
            />
          </div>
          <Button onClick={handleCreateGroup} className="w-full">
            Create Group
          </Button>
        </div>
      </Modal>

      <Modal isOpen={showInviteModal} onClose={() => setShowInviteModal(false)} title="Invite Member">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Email Address</label>
            <input
              type="email"
              value={inviteEmail}
              onChange={(e) => setInviteEmail(e.target.value)}
              className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
              placeholder="member@example.com"
            />
          </div>
          <Button onClick={handleInviteMember} className="w-full">
            Send Invitation
          </Button>
        </div>
      </Modal>
    </div>
  );
}
