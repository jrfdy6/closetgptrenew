"use client";

import { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useChallenges } from '@/hooks/useGamificationStats';
import ChallengeCard from './ChallengeCard';
import { Skeleton } from '@/components/ui/skeleton';
import { useToast } from '@/components/ui/use-toast';

interface ChallengeListProps {
  featured?: boolean;
}

export default function ChallengeList({ featured = false }: ChallengeListProps) {
  const { activeChallenges, availableChallenges, loading, error, startChallenge } = useChallenges();
  const [startingChallenge, setStartingChallenge] = useState<string | null>(null);
  const { toast } = useToast();

  const handleStartChallenge = async (challengeId: string) => {
    setStartingChallenge(challengeId);
    try {
      const success = await startChallenge(challengeId);
      if (success) {
        toast({
          title: "Challenge Started!",
          description: "Good luck! Complete this challenge to earn rewards.",
        });
      } else {
        toast({
          title: "Failed to start challenge",
          description: "Please try again later.",
          variant: "destructive"
        });
      }
    } catch (err) {
      toast({
        title: "Error",
        description: "Something went wrong. Please try again.",
        variant: "destructive"
      });
    } finally {
      setStartingChallenge(null);
    }
  };

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {[1, 2, 3].map((i) => (
          <Skeleton key={i} className="h-64 w-full" />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center p-8">
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Unable to load challenges. Please try again later.
        </p>
      </div>
    );
  }

  // If featured mode, only show featured available challenges
  if (featured) {
    const featuredChallenges = availableChallenges.filter(c => c.featured);
    
    if (featuredChallenges.length === 0 && activeChallenges.length === 0) {
      return (
        <div className="text-center p-8 bg-gray-50 dark:bg-gray-800 rounded-lg">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            No challenges available right now. Check back next week!
          </p>
        </div>
      );
    }

    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* Active challenges first */}
        {activeChallenges.map((challenge) => (
          <ChallengeCard
            key={challenge.challenge_id}
            challenge={challenge}
            variant="active"
          />
        ))}
        
        {/* Featured available challenges */}
        {featuredChallenges.map((challenge) => (
          <ChallengeCard
            key={challenge.challenge_id}
            challenge={challenge}
            variant="available"
            onStart={handleStartChallenge}
          />
        ))}
      </div>
    );
  }

  // Full view with tabs
  return (
    <Tabs defaultValue="active" className="w-full">
      <TabsList className="grid w-full grid-cols-3">
        <TabsTrigger value="active">
          Active ({activeChallenges.length})
        </TabsTrigger>
        <TabsTrigger value="available">
          Available ({availableChallenges.length})
        </TabsTrigger>
        <TabsTrigger value="completed">
          Completed
        </TabsTrigger>
      </TabsList>

      <TabsContent value="active" className="mt-6">
        {activeChallenges.length === 0 ? (
          <div className="text-center p-8 bg-gradient-to-br from-[#D4A574]/30 to-[#C9956F]/30 dark:from-[#D4A574]/20 dark:to-[#C9956F]/20 rounded-lg">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              No active challenges. Start one to begin earning rewards!
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {activeChallenges.map((challenge) => (
              <ChallengeCard
                key={challenge.challenge_id}
                challenge={challenge}
                variant="active"
              />
            ))}
          </div>
        )}
      </TabsContent>

      <TabsContent value="available" className="mt-6">
        {availableChallenges.length === 0 ? (
          <div className="text-center p-8 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              All challenges are currently active or completed. Great job!
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {availableChallenges.map((challenge) => (
              <ChallengeCard
                key={challenge.challenge_id}
                challenge={challenge}
                variant="available"
                onStart={handleStartChallenge}
              />
            ))}
          </div>
        )}
      </TabsContent>

      <TabsContent value="completed" className="mt-6">
        <div className="text-center p-8 bg-gray-50 dark:bg-gray-800 rounded-lg">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Completed challenges will appear here. Keep going!
          </p>
        </div>
      </TabsContent>
    </Tabs>
  );
}

