"use client";

import { useState, useEffect } from 'react';
import { useFirebase } from '@/lib/firebase-context';
import { Calendar } from '@/components/outfit-history/Calendar';
import { OutfitDetailsModal } from '@/components/outfit-history/OutfitDetailsModal';
import { OutfitHistoryStats } from '@/components/outfit-history/OutfitHistoryStats';
import { TimelineView } from '@/components/outfit-history/TimelineView';
import { YearlyArchive } from '@/components/outfit-history/YearlyArchive';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { CalendarIcon, BarChart3Icon, ClockIcon, ArchiveIcon } from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';

interface OutfitHistoryEntry {
  id: string;
  outfitId: string;
  outfitName: string;
  outfitImage: string;
  dateWorn: string;
  weather: {
    temperature: number;
    condition: string;
    humidity: number;
  };
  occasion: string;
  mood: string;
  notes: string;
  tags: string[];
  createdAt: string;
  updatedAt: string;
}

export default function OutfitHistoryPage() {
  const { user } = useFirebase();
  const { toast } = useToast();
  const [outfitHistory, setOutfitHistory] = useState<OutfitHistoryEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedEntry, setSelectedEntry] = useState<OutfitHistoryEntry | null>(null);
  const [currentView, setCurrentView] = useState<'calendar' | 'timeline' | 'archive'>('calendar');
  const [selectedDate, setSelectedDate] = useState<Date>(new Date());

  useEffect(() => {
    if (user) {
      fetchOutfitHistory();
    }
  }, [user]);

  const fetchOutfitHistory = async () => {
    if (!user) return;

    try {
      setLoading(true);
      const response = await fetch('/api/outfit-history', {
        headers: {
          'Authorization': `Bearer ${await user.getIdToken()}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setOutfitHistory(data.outfitHistory || []);
      } else {
        throw new Error('Failed to fetch outfit history');
      }
    } catch (error) {
      console.error('Error fetching outfit history:', error);
      toast({
        title: "Error",
        description: "Failed to load outfit history",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleMarkAsWorn = async (outfitId: string, date: string) => {
    if (!user) return;

    try {
      const response = await fetch('/api/outfit-history/mark-worn', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${await user.getIdToken()}`,
        },
        body: JSON.stringify({
          outfitId,
          dateWorn: date,
        }),
      });

      if (response.ok) {
        toast({
          title: "Success",
          description: "Outfit marked as worn",
        });
        fetchOutfitHistory(); // Refresh data
      } else {
        throw new Error('Failed to mark outfit as worn');
      }
    } catch (error) {
      console.error('Error marking outfit as worn:', error);
      toast({
        title: "Error",
        description: "Failed to mark outfit as worn",
        variant: "destructive",
      });
    }
  };

  const handleUpdateEntry = async (entryId: string, updates: Partial<OutfitHistoryEntry>) => {
    if (!user) return;

    try {
      const response = await fetch(`/api/outfit-history/${entryId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${await user.getIdToken()}`,
        },
        body: JSON.stringify(updates),
      });

      if (response.ok) {
        toast({
          title: "Success",
          description: "Outfit history updated",
        });
        fetchOutfitHistory(); // Refresh data
        setSelectedEntry(null); // Close modal
      } else {
        throw new Error('Failed to update outfit history');
      }
    } catch (error) {
      console.error('Error updating outfit history:', error);
      toast({
        title: "Error",
        description: "Failed to update outfit history",
        variant: "destructive",
      });
    }
  };

  const handleDeleteEntry = async (entryId: string) => {
    if (!user) return;

    try {
      const response = await fetch(`/api/outfit-history/${entryId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${await user.getIdToken()}`,
        },
      });

      if (response.ok) {
        toast({
          title: "Success",
          description: "Outfit history entry deleted",
        });
        fetchOutfitHistory(); // Refresh data
        setSelectedEntry(null); // Close modal
      } else {
        throw new Error('Failed to delete outfit history entry');
      }
    } catch (error) {
      console.error('Error deleting outfit history entry:', error);
      toast({
        title: "Error",
        description: "Failed to delete outfit history entry",
        variant: "destructive",
      });
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Outfit History</h1>
        <p className="text-muted-foreground">
          Track your daily outfits and discover your style patterns
        </p>
      </div>

      {/* Stats Overview */}
      <OutfitHistoryStats outfitHistory={outfitHistory} />

      {/* View Tabs */}
      <Tabs value={currentView} onValueChange={(value) => setCurrentView(value as any)} className="mt-8">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="calendar" className="flex items-center gap-2">
            <CalendarIcon className="h-4 w-4" />
            Calendar
          </TabsTrigger>
          <TabsTrigger value="timeline" className="flex items-center gap-2">
            <ClockIcon className="h-4 w-4" />
            Timeline
          </TabsTrigger>
          <TabsTrigger value="archive" className="flex items-center gap-2">
            <ArchiveIcon className="h-4 w-4" />
            Archive
          </TabsTrigger>
        </TabsList>

        <TabsContent value="calendar" className="mt-6">
          <Calendar
            outfitHistory={outfitHistory}
            selectedDate={selectedDate}
            onDateSelect={setSelectedDate}
            onEntrySelect={setSelectedEntry}
            onMarkAsWorn={handleMarkAsWorn}
          />
        </TabsContent>

        <TabsContent value="timeline" className="mt-6">
          <TimelineView
            outfitHistory={outfitHistory}
            onEntrySelect={setSelectedEntry}
            onUpdateEntry={handleUpdateEntry}
            onDeleteEntry={handleDeleteEntry}
          />
        </TabsContent>

        <TabsContent value="archive" className="mt-6">
          <YearlyArchive
            outfitHistory={outfitHistory}
            onEntrySelect={setSelectedEntry}
            onUpdateEntry={handleUpdateEntry}
            onDeleteEntry={handleDeleteEntry}
          />
        </TabsContent>
      </Tabs>

      {/* Outfit Details Modal */}
      {selectedEntry && (
        <OutfitDetailsModal
          entry={selectedEntry}
          onClose={() => setSelectedEntry(null)}
          onUpdate={handleUpdateEntry}
          onDelete={handleDeleteEntry}
        />
      )}
    </div>
  );
} 