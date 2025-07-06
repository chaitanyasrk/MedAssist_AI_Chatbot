import React from 'react';

interface LoadingIndicatorProps {
  type?: 'dots' | 'spinner' | 'pulse';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const LoadingIndicator: React.FC<LoadingIndicatorProps> = ({ 
  type = 'dots', 
  size = 'md',
  className = '' 
}) => {
  const sizeClasses = {
    sm: 'w-1.5 h-1.5',
    md: 'w-2 h-2',
    lg: 'w-3 h-3'
  };

  if (type === 'dots') {
    return (
      <div className={`flex space-x-1 ${className}`}>
        <div className={`${sizeClasses[size]} bg-primary-500 rounded-full animate-bounce-1`} />
        <div className={`${sizeClasses[size]} bg-primary-500 rounded-full animate-bounce-2`} />
        <div className={`${sizeClasses[size]} bg-primary-500 rounded-full animate-bounce-3`} />
      </div>
    );
  }

  if (type === 'spinner') {
    const spinnerSizes = {
      sm: 'w-4 h-4',
      md: 'w-6 h-6',
      lg: 'w-8 h-8'
    };

    return (
      <div className={`${spinnerSizes[size]} ${className}`}>
        <div className="animate-spin rounded-full border-2 border-primary-200 border-t-primary-600 w-full h-full" />
      </div>
    );
  }

  if (type === 'pulse') {
    const pulseSizes = {
      sm: 'w-4 h-4',
      md: 'w-6 h-6',
      lg: 'w-8 h-8'
    };

    return (
      <div className={`${pulseSizes[size]} bg-primary-500 rounded-full animate-pulse ${className}`} />
    );
  }

  return null;
};

export default LoadingIndicator;