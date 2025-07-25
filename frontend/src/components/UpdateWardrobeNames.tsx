import { useState } from 'react';
import { updateAllWardrobeItemNames } from '@/lib/firebase/wardrobeService';
import { useAuth } from '@/lib/hooks/useAuth';

export function UpdateWardrobeNames() {
  const [isUpdating, setIsUpdating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { user } = useAuth();

  const handleUpdate = async () => {
    if (!user) return;
    
    setIsUpdating(true);
    setError(null);
    
    try {
      const result = await updateAllWardrobeItemNames(user.uid);
      if (!result.success) {
        setError(result.error || 'Failed to update names');
      }
    } catch (err) {
      setError('An error occurred while updating names');
    } finally {
      setIsUpdating(false);
    }
  };

  return (
    <div className="flex flex-col items-center gap-4 p-4">
      <button
        onClick={handleUpdate}
        disabled={isUpdating}
        className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-blue-300"
      >
        {isUpdating ? 'Updating Names...' : 'Update All Item Names'}
      </button>
      {error && (
        <p className="text-red-500">{error}</p>
      )}
    </div>
  );
} 