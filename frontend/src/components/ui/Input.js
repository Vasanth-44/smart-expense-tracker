import React from 'react';
import { motion } from 'framer-motion';

export default function Input({ 
  label, 
  error, 
  icon: Icon,
  className = '',
  ...props 
}) {
  return (
    <div className="space-y-2">
      {label && (
        <label className="block text-sm font-medium text-gray-300">
          {label}
        </label>
      )}
      <div className="relative">
        {Icon && (
          <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
            <Icon size={18} />
          </div>
        )}
        <motion.input
          whileFocus={{ scale: 1.01 }}
          className={`
            w-full px-4 py-3 ${Icon ? 'pl-10' : ''}
            bg-white/5 border border-white/10
            rounded-xl text-white placeholder-gray-500
            focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500/50
            transition-all duration-200
            ${error ? 'border-red-500/50 focus:ring-red-500/50' : ''}
            ${className}
          `}
          {...props}
        />
      </div>
      {error && (
        <motion.p
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-sm text-red-400"
        >
          {error}
        </motion.p>
      )}
    </div>
  );
}
