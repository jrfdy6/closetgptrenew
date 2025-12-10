'use client';

import React, { useEffect, useState } from 'react';
import { Card } from '@/components/ui/card';
import { motion } from 'framer-motion';
import { BarChart3, Lock, TrendingUp, Gift, AlertCircle } from 'lucide-react';

interface AuditData {
  plan: string;
  season_id: string;
  metrics: {
    total_items: number;
    items_worn: number;
    items_unworn: number;
  };
  wur?: number; // Wardrobe Utilization Rate (PRO+)
  estimated_waste?: number; // Estimated waste value (PREMIUM only)
  lock_message?: string;
  donation_manifest?: Array<{
    item_id: string;
    name: string;
    type: string;
    color: string;
    reason: string;
    wear_count: number;
  }>;
}

export const AuditReportCard = () => {
  const [auditData, setAuditData] = useState<AuditData | null>(null);
  const [loading, setLoading] = useState(true);
  const [showDonationList, setShowDonationList] = useState(false);

  useEffect(() => {
    const fetchAudit = async () => {
      try {
        const response = await fetch(`/api/audit/status`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`
          }
        });

        if (response.ok) {
          const data = await response.json();
          setAuditData(data.audit);
        }
      } catch (error) {
        console.error('Failed to fetch audit data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchAudit();
  }, []);

  if (loading) {
    return (
      <Card className="bg-[#F5F0E8] dark:bg-[#251D18] border-[#C9956F]/30 p-6">
        <div className="flex items-center gap-4">
          <BarChart3 className="w-6 h-6 text-[#C9956F] animate-pulse" />
          <div className="flex-1">
            <div className="h-4 bg-[#C9956F]/20 rounded w-1/3 mb-2"></div>
            <div className="h-3 bg-[#C9956F]/10 rounded w-1/2"></div>
          </div>
        </div>
      </Card>
    );
  }

  if (!auditData) {
    return null;
  }

  const { plan, metrics, wur, estimated_waste, lock_message, donation_manifest } = auditData;
  const utilizationPercentage = (metrics.items_worn / metrics.total_items) * 100 || 0;

  // Render based on subscription plan
  if (plan === 'FREE') {
    return (
      <Card className="bg-[#F5F0E8] dark:bg-[#251D18] border-[#C9956F]/30 p-6">
        <div className="space-y-4">
          {/* Header */}
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-[#C9956F]/10 rounded-lg">
                <BarChart3 className="w-5 h-5 text-[#C9956F]" />
              </div>
              <div>
                <h3 className="font-semibold text-[#251D18] dark:text-[#F5F0E8]">Wardrobe Audit</h3>
                <p className="text-xs text-[#C9956F]">Season Report 2025</p>
              </div>
            </div>
          </div>

          {/* Ghost Report - Numbers only */}
          <div className="grid grid-cols-3 gap-4 py-4 border-y border-[#C9956F]/20">
            <div className="text-center">
              <p className="text-2xl font-bold text-[#251D18] dark:text-[#F5F0E8]">
                {metrics.total_items}
              </p>
              <p className="text-xs text-[#C9956F]">Total Items</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-[#251D18] dark:text-[#F5F0E8]">
                {metrics.items_worn}
              </p>
              <p className="text-xs text-[#C9956F]">Items Worn</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-[#D4A574]">
                {metrics.items_unworn}
              </p>
              <p className="text-xs text-[#C9956F]">Not Worn</p>
            </div>
          </div>

          {/* Lock Message */}
          <div className="bg-[#C9956F]/5 border border-[#C9956F]/30 rounded-lg p-4 flex items-start gap-3">
            <Lock className="w-5 h-5 text-[#C9956F] flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-[#251D18] dark:text-[#F5F0E8] mb-1">
                Unlock Detailed Insights
              </p>
              <p className="text-xs text-[#C9956F]">
                See your Wardrobe Utilization Rate with PRO, or full financial analysis with PREMIUM.
              </p>
            </div>
          </div>
        </div>
      </Card>
    );
  }

  if (plan === 'PRO') {
    return (
      <Card className="bg-[#F5F0E8] dark:bg-[#251D18] border-[#C9956F]/30 p-6">
        <div className="space-y-4">
          {/* Header */}
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-[#C9956F]/10 rounded-lg">
                <BarChart3 className="w-5 h-5 text-[#C9956F]" />
              </div>
              <div>
                <h3 className="font-semibold text-[#251D18] dark:text-[#F5F0E8]">Wardrobe Audit (PRO)</h3>
                <p className="text-xs text-[#C9956F]">Utilization Analysis</p>
              </div>
            </div>
            <span className="text-xs font-medium text-[#C9956F] bg-[#C9956F]/10 px-2 py-1 rounded">
              PRO
            </span>
          </div>

          {/* WUR Visualization */}
          <div className="space-y-3 py-4 border-y border-[#C9956F]/20">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium text-[#251D18] dark:text-[#F5F0E8]">
                Wardrobe Utilization Rate
              </p>
              <p className="text-lg font-bold text-[#C9956F]">{wur?.toFixed(1)}%</p>
            </div>

            {/* Progress Bar */}
            <div className="w-full bg-[#C9956F]/10 rounded-full h-3 overflow-hidden">
              <motion.div
                className="h-full bg-gradient-to-r from-[#C9956F] to-[#D4A574]"
                initial={{ width: 0 }}
                animate={{ width: `${Math.min(wur || 0, 100)}%` }}
                transition={{ duration: 1, ease: 'easeOut' }}
              />
            </div>

            {/* Breakdown */}
            <div className="grid grid-cols-3 gap-3 pt-2">
              <div className="text-center p-3 bg-[#C9956F]/5 rounded-lg">
                <p className="text-lg font-bold text-[#251D18] dark:text-[#F5F0E8]">
                  {metrics.total_items}
                </p>
                <p className="text-xs text-[#C9956F]">Total Items</p>
              </div>
              <div className="text-center p-3 bg-[#C9956F]/5 rounded-lg">
                <p className="text-lg font-bold text-[#251D18] dark:text-[#F5F0E8]">
                  {metrics.items_worn}
                </p>
                <p className="text-xs text-[#C9956F]">Worn This Season</p>
              </div>
              <div className="text-center p-3 bg-[#D4A574]/10 rounded-lg">
                <p className="text-lg font-bold text-[#D4A574]">
                  {metrics.items_unworn}
                </p>
                <p className="text-xs text-[#C9956F]">Dormant</p>
              </div>
            </div>
          </div>

          {/* Upgrade to Premium */}
          <div className="bg-[#C9956F]/5 border border-[#C9956F]/30 rounded-lg p-4 flex items-start gap-3">
            <TrendingUp className="w-5 h-5 text-[#C9956F] flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-[#251D18] dark:text-[#F5F0E8] mb-1">
                See Financial Impact
              </p>
              <p className="text-xs text-[#C9956F]">
                Upgrade to PREMIUM to unlock estimated waste value and donation recommendations.
              </p>
            </div>
          </div>
        </div>
      </Card>
    );
  }

  // PREMIUM Plan
  return (
    <Card className="bg-[#F5F0E8] dark:bg-[#251D18] border-[#C9956F]/30 p-6">
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-[#C9956F]/10 rounded-lg">
              <BarChart3 className="w-5 h-5 text-[#C9956F]" />
            </div>
            <div>
              <h3 className="font-semibold text-[#251D18] dark:text-[#F5F0E8]">Wardrobe Audit (PREMIUM)</h3>
              <p className="text-xs text-[#C9956F]">Complete Financial Analysis</p>
            </div>
          </div>
          <span className="text-xs font-medium text-[#C9956F] bg-[#C9956F]/10 px-2 py-1 rounded">
            PREMIUM
          </span>
        </div>

        {/* WUR Visualization */}
        <div className="space-y-3 py-4 border-y border-[#C9956F]/20">
          <div className="flex items-center justify-between">
            <p className="text-sm font-medium text-[#251D18] dark:text-[#F5F0E8]">
              Wardrobe Utilization Rate
            </p>
            <p className="text-lg font-bold text-[#C9956F]">{wur?.toFixed(1)}%</p>
          </div>

          {/* Progress Bar */}
          <div className="w-full bg-[#C9956F]/10 rounded-full h-3 overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-[#C9956F] to-[#D4A574]"
              initial={{ width: 0 }}
              animate={{ width: `${Math.min(wur || 0, 100)}%` }}
              transition={{ duration: 1, ease: 'easeOut' }}
            />
          </div>

          {/* Breakdown Grid */}
          <div className="grid grid-cols-3 gap-3 pt-2">
            <div className="text-center p-3 bg-[#C9956F]/5 rounded-lg">
              <p className="text-lg font-bold text-[#251D18] dark:text-[#F5F0E8]">
                {metrics.total_items}
              </p>
              <p className="text-xs text-[#C9956F]">Total Items</p>
            </div>
            <div className="text-center p-3 bg-[#C9956F]/5 rounded-lg">
              <p className="text-lg font-bold text-[#251D18] dark:text-[#F5F0E8]">
                {metrics.items_worn}
              </p>
              <p className="text-xs text-[#C9956F]">Worn This Season</p>
            </div>
            <div className="text-center p-3 bg-[#D4A574]/10 rounded-lg">
              <p className="text-lg font-bold text-[#D4A574]">
                {metrics.items_unworn}
              </p>
              <p className="text-xs text-[#C9956F]">Dormant</p>
            </div>
          </div>
        </div>

        {/* Estimated Waste */}
        <div className="bg-[#D4A574]/10 border border-[#D4A574]/30 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm font-medium text-[#251D18] dark:text-[#F5F0E8]">
              Estimated Value at Risk
            </p>
            <p className="text-xl font-bold text-[#D4A574]">
              ${estimated_waste?.toFixed(2) || '0.00'}
            </p>
          </div>
          <p className="text-xs text-[#C9956F]">
            Potential savings if you donate items that haven't been worn this season.
          </p>
        </div>

        {/* Donation Manifest Button */}
        {donation_manifest && donation_manifest.length > 0 && (
          <button
            onClick={() => setShowDonationList(!showDonationList)}
            className="w-full bg-gradient-to-r from-[#C9956F] to-[#D4A574] text-white font-medium py-3 rounded-lg hover:opacity-90 transition flex items-center justify-center gap-2"
          >
            <Gift className="w-4 h-4" />
            <span>View Donation List ({donation_manifest.length} items)</span>
          </button>
        )}

        {/* Donation List (Expandable) */}
        {showDonationList && donation_manifest && donation_manifest.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="border-t border-[#C9956F]/20 pt-4 space-y-2"
          >
            {donation_manifest.slice(0, 5).map((item, idx) => (
              <div
                key={idx}
                className="bg-[#C9956F]/5 border border-[#C9956F]/20 rounded-lg p-3 flex items-start gap-3"
              >
                <AlertCircle className="w-4 h-4 text-[#D4A574] flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <p className="text-sm font-medium text-[#251D18] dark:text-[#F5F0E8]">
                    {item.name}
                  </p>
                  <p className="text-xs text-[#C9956F]">
                    {item.type} • {item.color} • {item.reason}
                  </p>
                </div>
              </div>
            ))}
            {donation_manifest.length > 5 && (
              <p className="text-xs text-center text-[#C9956F] pt-2">
                +{donation_manifest.length - 5} more items
              </p>
            )}
          </motion.div>
        )}
      </div>
    </Card>
  );
};

