"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { DollarSign, Edit, ShoppingBag } from 'lucide-react';
import { useState, useEffect } from 'react';
import { useAuthContext } from '@/contexts/AuthContext';
import { doc, getDoc } from 'firebase/firestore';
import { db } from '@/lib/firebase/config';

interface SpendingRangesCardProps {
  onEdit?: () => void;
}

const CATEGORY_LABELS: Record<string, string> = {
  tops: "Tops",
  pants: "Pants & Bottoms",
  shoes: "Shoes",
  jackets: "Jackets & Outerwear",
  dresses: "Dresses",
  accessories: "Accessories",
  undergarments: "Undergarments",
  swimwear: "Swimwear"
};

const CATEGORY_ICONS: Record<string, string> = {
  tops: "👕",
  pants: "👖",
  shoes: "👟",
  jackets: "🧥",
  dresses: "👗",
  accessories: "👜",
  undergarments: "🩲",
  swimwear: "🩱"
};

export default function SpendingRangesCard({ onEdit }: SpendingRangesCardProps) {
  const { user } = useAuthContext();
  const [spendingRanges, setSpendingRanges] = useState<Record<string, string> | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) {
      setLoading(false);
      return;
    }

    const fetchSpendingRanges = async () => {
      try {
        setLoading(true);
        const userRef = doc(db, 'users', user.uid);
        const userDoc = await getDoc(userRef);
        
        if (userDoc.exists()) {
          const userData = userDoc.data();
          const ranges = userData.spending_ranges;
          
          console.log('📊 Spending ranges from Firestore:', ranges);
          setSpendingRanges(ranges || null);
        }
      } catch (error) {
        console.error('Error fetching spending ranges:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchSpendingRanges();
  }, [user]);

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ShoppingBag className="w-5 h-5" />
            Spending Ranges
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {[1, 2, 3].map(i => (
              <div key={i} className="h-10 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  const hasSpendingData = spendingRanges && Object.values(spendingRanges).some(v => v !== "unknown");

  if (!hasSpendingData) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ShoppingBag className="w-5 h-5 text-gray-400" />
            Spending Ranges
          </CardTitle>
          <CardDescription>
            Help us calculate accurate Cost Per Wear
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
            No spending ranges set. This helps us calculate how much value you're getting from your wardrobe.
          </p>
          {onEdit && (
            <button
              onClick={onEdit}
              className="text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400 flex items-center gap-1"
            >
              <Edit className="w-3 h-3" />
              Set Spending Ranges
            </button>
          )}
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="bg-gradient-to-r from-emerald-50 to-green-50 dark:from-emerald-900/20 dark:to-green-900/20">
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <ShoppingBag className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
            Spending Ranges
          </div>
          {onEdit && (
            <button
              onClick={onEdit}
              className="text-sm text-gray-600 hover:text-gray-700 dark:text-gray-400 flex items-center gap-1"
            >
              <Edit className="w-4 h-4" />
              Edit
            </button>
          )}
        </CardTitle>
        <CardDescription>
          Annual spending by category
        </CardDescription>
      </CardHeader>
      <CardContent className="pt-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {Object.entries(CATEGORY_LABELS).map(([key, label]) => {
            const range = spendingRanges?.[key] || "unknown";
            const isSet = range !== "unknown";
            
            return (
              <div
                key={key}
                className="flex items-center justify-between p-3 rounded-lg bg-gray-50 dark:bg-gray-800/50"
              >
                <div className="flex items-center gap-2">
                  <span className="text-xl">{CATEGORY_ICONS[key]}</span>
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    {label}
                  </span>
                </div>
                {isSet ? (
                  <Badge variant="outline" className="text-emerald-700 border-emerald-300 dark:text-emerald-400">
                    {range}
                  </Badge>
                ) : (
                  <Badge variant="outline" className="text-gray-500 border-gray-300">
                    Not set
                  </Badge>
                )}
              </div>
            );
          })}
        </div>
        
        <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
          <p className="text-xs text-blue-700 dark:text-blue-300">
            💡 These ranges help calculate your Cost Per Wear (CPW) and show how much value you're getting from your wardrobe.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}

