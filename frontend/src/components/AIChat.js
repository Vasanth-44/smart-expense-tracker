import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageCircle, X, Send, Sparkles, Loader } from 'lucide-react';
import axios from 'axios';
import GlassCard from './ui/GlassCard';
import Button from './ui/Button';
import toast from 'react-hot-toast';
import { API_BASE_URL } from '../services/api';

export default function AIChat() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const [typingMessage, setTypingMessage] = useState('');
  const messagesEndRef = useRef(null);

  useEffect(() => {
    loadSuggestions();
    // Add welcome message
    if (messages.length === 0) {
      setMessages([{
        type: 'ai',
        content: "👋 Hi! I'm your AI spending assistant. How can I help you manage your finances today?",
        timestamp: new Date()
      }]);
    }
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, typingMessage]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadSuggestions = async () => {
    try {
      const token = localStorage.getItem('token');
      const res = await axios.get(`${API_BASE_URL}/ai/suggestions`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSuggestions(res.data.suggestions);
    } catch (error) {
      console.error('Error loading suggestions:', error);
    }
  };

  const sendMessage = async (messageText) => {
    const text = messageText || input.trim();
    if (!text) return;

    // Add user message
    const userMessage = {
      type: 'user',
      content: text,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const token = localStorage.getItem('token');
      const res = await axios.post(
        `${API_BASE_URL}/ai/chat`,
        { message: text },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      // Simulate typing effect
      const aiResponse = res.data;
      await simulateTyping(aiResponse);

    } catch (error) {
      console.error('Error sending message:', error);
      toast.error('Failed to get AI response');
      setMessages(prev => [...prev, {
        type: 'ai',
        content: "Sorry, I couldn't process that request. Please try again.",
        timestamp: new Date()
      }]);
    } finally {
      setLoading(false);
    }
  };

  const simulateTyping = async (response) => {
    // Format the response
    let fullMessage = `${response.message}\n\n`;
    
    if (response.insights && response.insights.length > 0) {
      fullMessage += "**Insights:**\n";
      response.insights.forEach(insight => {
        fullMessage += `• ${insight}\n`;
      });
      fullMessage += "\n";
    }

    if (response.suggested_actions && response.suggested_actions.length > 0) {
      fullMessage += "**Suggested Actions:**\n";
      response.suggested_actions.forEach(action => {
        fullMessage += `✓ ${action}\n`;
      });
    }

    // Typing animation
    const words = fullMessage.split(' ');
    let currentText = '';
    
    for (let i = 0; i < words.length; i++) {
      currentText += words[i] + ' ';
      setTypingMessage(currentText);
      await new Promise(resolve => setTimeout(resolve, 30));
    }

    // Add final message
    setMessages(prev => [...prev, {
      type: 'ai',
      content: fullMessage,
      data: response.data,
      timestamp: new Date()
    }]);
    setTypingMessage('');
  };

  const handleSuggestionClick = (suggestion) => {
    sendMessage(suggestion);
  };

  return (
    <>
      {/* Floating Chat Button */}
      <AnimatePresence>
        {!isOpen && (
          <motion.button
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            onClick={() => setIsOpen(true)}
            className="fixed bottom-8 right-8 w-16 h-16 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-full shadow-2xl flex items-center justify-center z-50 animate-glow"
          >
            <MessageCircle size={28} className="text-white" />
            <motion.div
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
              className="absolute -top-1 -right-1 w-4 h-4 bg-green-400 rounded-full border-2 border-white"
            />
          </motion.button>
        )}
      </AnimatePresence>

      {/* Chat Modal */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            className="fixed bottom-8 right-8 w-96 h-[600px] z-50"
          >
            <GlassCard className="h-full flex flex-col p-0 overflow-hidden border-indigo-500/30">
              {/* Header */}
              <div className="bg-gradient-to-r from-indigo-500 to-purple-600 p-4 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Sparkles className="text-white" size={20} />
                  <div>
                    <h3 className="text-white font-semibold">AI Assistant</h3>
                    <p className="text-white/80 text-xs">Powered by ExpenseAI</p>
                  </div>
                </div>
                <button
                  onClick={() => setIsOpen(false)}
                  className="text-white/80 hover:text-white transition-colors"
                >
                  <X size={20} />
                </button>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map((message, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[80%] p-3 rounded-2xl ${
                        message.type === 'user'
                          ? 'bg-gradient-to-r from-indigo-500 to-purple-600 text-white'
                          : 'bg-white/10 text-gray-200'
                      }`}
                    >
                      <p className="text-sm whitespace-pre-line">{message.content}</p>
                      <p className="text-xs opacity-60 mt-1">
                        {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </p>
                    </div>
                  </motion.div>
                ))}

                {/* Typing indicator */}
                {typingMessage && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="flex justify-start"
                  >
                    <div className="max-w-[80%] p-3 rounded-2xl bg-white/10 text-gray-200">
                      <p className="text-sm whitespace-pre-line">{typingMessage}</p>
                    </div>
                  </motion.div>
                )}

                {loading && !typingMessage && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="flex justify-start"
                  >
                    <div className="bg-white/10 p-3 rounded-2xl flex items-center gap-2">
                      <Loader size={16} className="animate-spin text-indigo-400" />
                      <span className="text-sm text-gray-300">Thinking...</span>
                    </div>
                  </motion.div>
                )}

                <div ref={messagesEndRef} />
              </div>

              {/* Quick Suggestions */}
              {messages.length <= 1 && suggestions.length > 0 && (
                <div className="px-4 pb-2">
                  <p className="text-xs text-gray-400 mb-2">Quick suggestions:</p>
                  <div className="flex flex-wrap gap-2">
                    {suggestions.map((suggestion, index) => (
                      <motion.button
                        key={index}
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: index * 0.1 }}
                        onClick={() => handleSuggestionClick(suggestion)}
                        className="px-3 py-1.5 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-xs text-gray-300 transition-all"
                      >
                        {suggestion}
                      </motion.button>
                    ))}
                  </div>
                </div>
              )}

              {/* Input */}
              <div className="p-4 border-t border-white/10">
                <form
                  onSubmit={(e) => {
                    e.preventDefault();
                    sendMessage();
                  }}
                  className="flex gap-2"
                >
                  <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Ask me anything..."
                    className="flex-1 px-4 py-2 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 text-sm"
                    disabled={loading}
                  />
                  <Button
                    type="submit"
                    disabled={loading || !input.trim()}
                    size="sm"
                    icon={Send}
                  />
                </form>
              </div>
            </GlassCard>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
