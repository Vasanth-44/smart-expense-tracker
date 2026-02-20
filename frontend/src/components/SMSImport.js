import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { MessageSquare, Send, CheckCircle, XCircle, Smartphone } from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';
import GlassCard from './ui/GlassCard';
import Button from './ui/Button';
import Input from './ui/Input';
import { API_BASE_URL } from '../services/api';

export default function SMSImport({ onImportSuccess }) {
  const [sender, setSender] = useState('');
  const [message, setMessage] = useState('');
  const [testing, setTesting] = useState(false);
  const [importing, setImporting] = useState(false);
  const [testResult, setTestResult] = useState(null);

  const handleTest = async () => {
    if (!message.trim()) {
      toast.error('Please enter SMS message');
      return;
    }

    setTesting(true);
    setTestResult(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/sms/test-parse`, {
        sender: sender || 'BANK',
        message: message
      });

      setTestResult(response.data);
      
      if (response.data.valid) {
        toast.success('SMS parsed successfully!');
      } else {
        toast.error('SMS could not be parsed');
      }
    } catch (error) {
      console.error('Test error:', error);
      toast.error('Failed to test SMS');
      setTestResult({ valid: false, message: 'Error testing SMS' });
    } finally {
      setTesting(false);
    }
  };

  const handleImport = async () => {
    if (!message.trim()) {
      toast.error('Please enter SMS message');
      return;
    }

    setImporting(true);

    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API_BASE_URL}/sms/webhook`,
        {
          sender: sender || 'BANK',
          message: message,
          timestamp: new Date().toISOString()
        },
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );

      if (response.data.status === 'success') {
        toast.success('Expense imported from SMS!');
        setSender('');
        setMessage('');
        setTestResult(null);
        if (onImportSuccess) onImportSuccess();
      } else if (response.data.status === 'duplicate') {
        toast.error('Duplicate transaction detected');
      }
    } catch (error) {
      console.error('Import error:', error);
      toast.error(error.response?.data?.detail || 'Failed to import SMS');
    } finally {
      setImporting(false);
    }
  };

  const exampleSMS = [
    "Rs 250.00 debited from A/c XX1234 on 10-02-2024 at SWIGGY BANGALORE",
    "Your A/c is debited with Rs.1,500.00 for payment to UBER INDIA via UPI",
    "You have paid Rs 300.00 to ZOMATO via PhonePe UPI on 10-02-2024"
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center"
      >
        <div className="flex items-center justify-center gap-3 mb-4">
          <Smartphone className="text-purple-400" size={32} />
          <h2 className="text-3xl font-bold gradient-text">SMS Import</h2>
        </div>
        <p className="text-gray-400">
          Paste transaction SMS to automatically import expenses
        </p>
      </motion.div>

      {/* Input Form */}
      <GlassCard>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Sender (Optional)
            </label>
            <Input
              type="text"
              placeholder="e.g., HDFCBK, ICICIB, PHONEPE"
              value={sender}
              onChange={(e) => setSender(e.target.value)}
            />
            <p className="text-xs text-gray-500 mt-1">
              Bank or UPI app sender ID
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              SMS Message *
            </label>
            <textarea
              className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl 
                       text-white placeholder-gray-500 focus:outline-none focus:border-purple-500
                       focus:ring-2 focus:ring-purple-500/20 transition-all resize-none"
              rows="4"
              placeholder="Paste your transaction SMS here..."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
            />
          </div>

          <div className="flex gap-3">
            <Button
              onClick={handleTest}
              disabled={testing || !message.trim()}
              variant="secondary"
              className="flex-1"
            >
              {testing ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent mr-2" />
                  Testing...
                </>
              ) : (
                <>
                  <MessageSquare size={18} className="mr-2" />
                  Test Parse
                </>
              )}
            </Button>

            <Button
              onClick={handleImport}
              disabled={importing || !message.trim()}
              className="flex-1"
            >
              {importing ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent mr-2" />
                  Importing...
                </>
              ) : (
                <>
                  <Send size={18} className="mr-2" />
                  Import Expense
                </>
              )}
            </Button>
          </div>
        </div>
      </GlassCard>

      {/* Test Result */}
      {testResult && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
        >
          <GlassCard className={testResult.valid ? 'border-green-500/30' : 'border-red-500/30'}>
            <div className="flex items-start gap-3">
              {testResult.valid ? (
                <CheckCircle className="text-green-400 flex-shrink-0 mt-1" size={24} />
              ) : (
                <XCircle className="text-red-400 flex-shrink-0 mt-1" size={24} />
              )}
              
              <div className="flex-1">
                <h3 className={`font-semibold mb-2 ${testResult.valid ? 'text-green-400' : 'text-red-400'}`}>
                  {testResult.message}
                </h3>
                
                {testResult.valid && testResult.parsed_data && (
                  <div className="space-y-2 text-sm">
                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <span className="text-gray-400">Amount:</span>
                        <span className="text-white ml-2 font-semibold">
                          ₹{testResult.parsed_data.amount}
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-400">Category:</span>
                        <span className="text-purple-400 ml-2 font-semibold">
                          {testResult.parsed_data.suggested_category}
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-400">Merchant:</span>
                        <span className="text-white ml-2">
                          {testResult.parsed_data.merchant}
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-400">Date:</span>
                        <span className="text-white ml-2">
                          {testResult.parsed_data.date}
                        </span>
                      </div>
                    </div>
                    <div className="pt-2 border-t border-white/10">
                      <span className="text-gray-400">Note:</span>
                      <p className="text-white text-xs mt-1">
                        {testResult.parsed_data.note}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </GlassCard>
        </motion.div>
      )}

      {/* Example SMS */}
      <GlassCard>
        <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
          <MessageSquare size={20} className="text-purple-400" />
          Example SMS Messages
        </h3>
        <div className="space-y-2">
          {exampleSMS.map((sms, idx) => (
            <button
              key={idx}
              onClick={() => setMessage(sms)}
              className="w-full text-left p-3 bg-white/5 hover:bg-white/10 rounded-lg 
                       border border-white/10 hover:border-purple-500/30 transition-all
                       text-sm text-gray-300 hover:text-white"
            >
              {sms}
            </button>
          ))}
        </div>
        <p className="text-xs text-gray-500 mt-3">
          Click any example to try it out
        </p>
      </GlassCard>

      {/* Info */}
      <GlassCard className="border-blue-500/30 bg-blue-500/5">
        <div className="flex items-start gap-3">
          <Smartphone className="text-blue-400 flex-shrink-0 mt-1" size={20} />
          <div className="text-sm text-blue-200">
            <p className="font-semibold mb-2">💡 Pro Tip: Automatic SMS Import</p>
            <p className="text-blue-300/80">
              Set up SMS forwarding to automatically import expenses! 
              Check <code className="px-2 py-1 bg-black/30 rounded">SMS_AUTO_IMPORT_GUIDE.md</code> for instructions.
            </p>
          </div>
        </div>
      </GlassCard>
    </div>
  );
}
