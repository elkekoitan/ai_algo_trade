import React from 'react';
import { motion } from 'framer-motion';
import { Loader2, Zap } from 'lucide-react';

interface LoadingProps {
  message?: string;
  fullScreen?: boolean;
  size?: 'small' | 'medium' | 'large';
  variant?: 'default' | 'logo';
}

export const Loading: React.FC<LoadingProps> = ({ 
  message = 'Loading...', 
  fullScreen = false,
  size = 'medium',
  variant = 'default'
}) => {
  const sizeMap = {
    small: {
      container: 'h-20',
      icon: 'h-6 w-6',
      text: 'text-sm'
    },
    medium: {
      container: 'h-40',
      icon: 'h-10 w-10',
      text: 'text-base'
    },
    large: {
      container: 'h-60',
      icon: 'h-16 w-16',
      text: 'text-lg'
    }
  };
  
  const selectedSize = sizeMap[size];
  
  const containerClasses = fullScreen 
    ? 'fixed inset-0 flex items-center justify-center bg-gray-900/80 backdrop-blur-sm z-50' 
    : `flex items-center justify-center ${selectedSize.container}`;
  
  return (
    <div className={containerClasses}>
      <div className="text-center">
        {variant === 'default' ? (
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
            className={`mx-auto mb-4 text-blue-500 ${selectedSize.icon}`}
          >
            <Loader2 className="w-full h-full" />
          </motion.div>
        ) : (
          <motion.div
            className="relative mx-auto mb-4"
            initial={{ scale: 0.8 }}
            animate={{ scale: 1 }}
            transition={{ 
              repeat: Infinity, 
              repeatType: "reverse", 
              duration: 0.8,
            }}
          >
            <Zap className={`text-blue-500 ${selectedSize.icon}`} />
            <motion.div 
              className="absolute inset-0 rounded-full bg-blue-500/30"
              animate={{ scale: [1, 1.5, 1], opacity: [1, 0, 1] }}
              transition={{ 
                duration: 2, 
                repeat: Infinity,
                ease: "easeInOut" 
              }}
            />
          </motion.div>
        )}
        
        <motion.p 
          className={`text-gray-300 ${selectedSize.text}`}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          {message}
        </motion.p>
      </div>
    </div>
  );
};

export default Loading; 