import React from 'react';
import { motion } from 'framer-motion';

export default function GlassCard({ children, className = '', hover = true, ...props }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      whileHover={hover ? { y: -5, transition: { duration: 0.2 } } : {}}
      className={`
        bg-white/5 backdrop-blur-xl border border-white/10 
        rounded-2xl shadow-2xl p-6
        ${className}
      `}
      {...props}
    >
      {children}
    </motion.div>
  );
}
