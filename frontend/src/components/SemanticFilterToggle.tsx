import React from 'react';
import { useSemanticFlag } from '../hooks/useSemanticFlag';

interface SemanticFilterToggleProps {
  onToggle?: (enabled: boolean) => void;
  className?: string;
}

export const SemanticFilterToggle: React.FC<SemanticFilterToggleProps> = ({ 
  onToggle, 
  className = "" 
}) => {
  const { semanticFlag, toggleSemanticFlag } = useSemanticFlag();

  const handleToggle = () => {
    toggleSemanticFlag();
    onToggle?.(!semanticFlag);
  };

  return (
    <div className={`flex items-center space-x-3 ${className}`}>
      <label className="flex items-center cursor-pointer">
        <input
          type="checkbox"
          checked={semanticFlag}
          onChange={handleToggle}
          className="sr-only"
        />
        <div className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
          semanticFlag ? 'bg-blue-600' : 'bg-gray-200'
        }`}>
          <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
            semanticFlag ? 'translate-x-6' : 'translate-x-1'
          }`} />
        </div>
        <span className="ml-3 text-sm font-medium text-gray-700">
          Semantic Filtering
        </span>
      </label>
      <div className="text-xs text-gray-500">
        {semanticFlag ? 'Enhanced compatibility matching' : 'Exact matching only'}
      </div>
    </div>
  );
};

export default SemanticFilterToggle;
