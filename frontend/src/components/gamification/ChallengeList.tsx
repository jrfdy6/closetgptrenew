"use client";

import { useRef, useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useChallenges } from '@/hooks/useGamificationStats';
import ChallengeCard from './ChallengeCard';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { useToast } from '@/components/ui/use-toast';

interface ChallengeListProps {
  featured?: boolean;
}

export default function ChallengeList({ featured = false }: ChallengeListProps) {
  const { activeChallenges, availableChallenges, completedChallenges, historyError, loading, error, startChallenge, refetch } = useChallenges();
  const [startingChallenge, setStartingChallenge] = useState<string | null>(null);
  const { toast } = useToast();
  const startInFlight = useRef(false);

  const handleStartChallenge = async (challengeId: string) => {
    if (startInFlight.current) return;
    startInFlight.current = true;
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
          title: "Could not confirm challenge start",
          description: "Try again to check the same challenge.",
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
      startInFlight.current = false;
      setStartingChallenge(null);
    }
  };

  if (loading && activeChallenges.length === 0 && availableChallenges.length === 0 && completedChallenges.length === 0) {
    return (
      <div role="status" aria-label="Loading challenges" className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
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
          Unable to load challenges. Please try again.
        </p>
        <Button variant="outline" className="mt-4 min-h-11" onClick={() => void refetch()}>Try again</Button>
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
            No challenges available right now.
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
            starting={startingChallenge === challenge.challenge_id}
            startDisabled={startingChallenge !== null || loading}
          />
        ))}
      </div>
    );
  }

  // Full view with tabs
  return (
    <Tabs defaultValue="active" className="w-full" aria-busy={loading}>
      {loading && <p role="status" className="mb-3 text-xs text-muted-foreground">Refreshing challenges…</p>}
      <TabsList className="grid h-auto min-h-11 w-full grid-cols-3">
        <TabsTrigger className="min-h-11 px-1 text-xs sm:text-sm" value="active">
          Active ({activeChallenges.length})
        </TabsTrigger>
        <TabsTrigger className="min-h-11 px-1 text-xs sm:text-sm" value="available">
          Available ({availableChallenges.length})
        </TabsTrigger>
        <TabsTrigger className="min-h-11 px-1 text-xs sm:text-sm" value="completed">
          Completed{historyError ? '' : ` (${completedChallenges.length})`}
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
              No challenges are available to start right now.
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
                starting={startingChallenge === challenge.challenge_id}
                startDisabled={startingChallenge !== null || loading}
              />
            ))}
          </div>
        )}
      </TabsContent>

      <TabsContent value="completed" className="mt-6">
        {historyError ? (
          <div className="text-center p-8 rounded-lg bg-secondary">
            <p role="status" className="text-sm text-muted-foreground">{historyError}</p>
            <Button variant="outline" className="mt-4 min-h-11" onClick={() => void refetch()}>Try again</Button>
          </div>
        ) : completedChallenges.length === 0 ? (
          <div className="text-center p-8 rounded-lg bg-secondary">
            <p className="text-sm text-muted-foreground">No completed challenges yet. Your finished challenges will appear here.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {completedChallenges.map((challenge, index) => (
              <ChallengeCard key={`${challenge.instance_id || challenge.challenge_id}:${challenge.completed_at || index}`} challenge={challenge} variant="completed" />
            ))}
          </div>
        )}
      </TabsContent>
    </Tabs>
  );
}

