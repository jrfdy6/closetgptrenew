"use client";

import { Button } from '@/components/ui/button';
import { Shuffle, Sparkles } from 'lucide-react';
import { motion } from 'framer-motion';
import { useState } from 'react';
import { useAuthContext } from '@/contexts/AuthContext';
import { useToast } from '@/components/ui/use-toast';

interface ShuffleButtonProps {
  size?: 'default' | 'sm' | 'lg';
  variant?: 'default' | 'outline' | 'secondary';
  onShuffle?: (outfit: any) => void;
  occasion?: string;
}

export default function ShuffleButton({ 
  size = 'lg',
  variant = 'default',
  onShuffle,
  occasion = 'casual'
}: ShuffleButtonProps) {
  const { user } = useAuthContext();
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);

  const handleShuffle = async () => {
    if (!user) {
      toast({
        title: "Sign in required",
        description: "Please sign in to use the shuffle feature.",
        variant: "destructive"
      });
      return;
    }

    setLoading(true);
    
    try {
      const token = await user.getIdToken();
      const response = await fetch('/api/shuffle', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ occasion })
      });

      if (!response.ok) {
        throw new Error('Failed to generate shuffle outfit');
      }

      const data = await response.json();
      
      if (data.success) {
        // Show XP toast
        if (data.xp_earned) {
          toast({
            title: `+${data.xp_earned} XP`,
            description: "Outfit generated!",
          });
        }
        
        // Call parent callback with outfit data
        if (onShuffle) {
          onShuffle(data.outfit);
        }
      } else {
        throw new Error(data.error || 'Failed to generate outfit');
      }
    } catch (error) {
      console.error('Shuffle error:', error);
      toast({
        title: "Shuffle failed",
        description: "Unable to generate outfit. Please try again.",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div 
      whileTap={{ scale: 0.95 }}
      whileHover={{ scale: 1.02 }}
    >
      <Button
        onClick={handleShuffle}
        size={size}
        variant={variant}
        disabled={loading}
        className="relative overflow-hidden"
      >
        <motion.div
          animate={loading ? {
            rotate: 360
          } : {}}
          transition={{
            duration: 1,
            repeat: loading ? Infinity : 0,
            ease: "linear"
          }}
        >
          <Shuffle className="w-5 h-5 mr-2" />
        </motion.div>
        <span>
          {loading ? 'Generating...' : 'Dress Me'}
        </span>
        
        {!loading && (
          <motion.div
            className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent"
            animate={{
              x: ['-100%', '200%']
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: "linear",
              repeatDelay: 1
            }}
          />
        )}
        
        <Sparkles className="w-4 h-4 ml-2 text-amber-400" />
      </Button>
    </motion.div>
  );
}

