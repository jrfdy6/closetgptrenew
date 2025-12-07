"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Trophy, Info, TrendingUp, DollarSign, Brain, Sparkles } from 'lucide-react';
import { motion } from 'framer-motion';
import { useState, useEffect } from 'react';
import { useAuthContext } from '@/contexts/AuthContext';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { ChevronDown } from 'lucide-react';

interface GWSData {
  total_gws: number;
  components: {
    utilization: {
      score: number;
      max: number;
      percentage: number;
      label: string;
    };
    cpw_improvement: {
      score: number;
      max: number;
      percentage: number;
      change: number;
      label: string;
    };
    ai_fit: {
      score: number;
      max: number;
      raw_score: number;
      label: string;
    };
    revived_items: {
      score: number;
      max: number;
      percentage: number;
      label: string;
    };
  };
  insights: string[];
}

export default function GWSCard() {
  const { user } = useAuthContext();
  const [gws, setGWS] = useState<GWSData | null>(null);
  const [loading, setLoading] = useState(true);
  const [showBreakdown, setShowBreakdown] = useState(false);

  useEffect(() => {
    if (!user) return;

    const fetchGWS = async () => {
      try {
        const token = await user.getIdToken();
        
        // For now, use mock data - replace with actual API call
        // TODO: Add /api/gamification/gws endpoint
        setGWS({
          total_gws: 72.5,
          components: {
            utilization: {
              score: 26.0,
              max: 40,
              percentage: 65,
              label: "Wardrobe Usage"
            },
            cpw_improvement: {
              score: 22.5,
              max: 30,
              percentage: 75,
              change: -8.5,
              label: "Value Optimization"
            },
            ai_fit: {
              score: 13.6,
              max: 20,
              raw_score: 68,
              label: "AI Understanding"
            },
            revived_items: {
              score: 10.4,
              max: 10,
              percentage: 40,
              label: "Item Revival"
            }
          },
          insights: [
            "Great progress! You're maximizing your wardrobe's potential.",
            "Your CPW is decreasing - excellent value optimization!",
            "The AI is learning your style well."
          ]
        });
      } catch (error) {
        console.error('Error fetching GWS:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchGWS();
  }, [user]);

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Trophy className="w-5 h-5" />
            Global Wardrobe Score
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-32 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
        </CardContent>
      </Card>
    );
  }

  if (!gws) return null;

  const score = gws.total_gws;
  const getScoreColor = (score: number) => {
    if (score >= 75) return 'text-green-600';
    if (score >= 50) return 'text-blue-600';
    if (score >= 25) return 'text-amber-600';
    return 'text-red-600';
  };

  const getScoreGrade = (score: number) => {
    if (score >= 90) return 'A+';
    if (score >= 80) return 'A';
    if (score >= 70) return 'B+';
    if (score >= 60) return 'B';
    if (score >= 50) return 'C';
    return 'D';
  };

  return (
    <Card className="overflow-hidden">
      <CardHeader className="bg-gradient-to-br from-[#E8C8A0]/10 to-[#C9956F]/10 dark:from-[#B8860B]/10 dark:to-[#C9956F]/10">
        <CardTitle className="flex items-center gap-2">
          <Trophy className="w-5 h-5 text-amber-600 dark:text-amber-400" />
          Global Wardrobe Score
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger>
                <Info className="w-4 h-4 text-gray-400" />
              </TooltipTrigger>
              <TooltipContent>
                <p className="max-w-xs text-sm">
                  Your overall wardrobe optimization score combining utilization,
                  value, AI learning, and item revival.
                </p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </CardTitle>
        <CardDescription>
          Overall wardrobe health
        </CardDescription>
      </CardHeader>
      <CardContent className="pt-6">
        <div className="space-y-6">
          {/* Main Score */}
          <div className="flex items-center justify-center gap-4">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", stiffness: 200 }}
              className={`text-6xl font-bold ${getScoreColor(score)}`}
            >
              {Math.round(score)}
            </motion.div>
            <div>
              <Badge className={`text-2xl px-4 py-2 ${
                score >= 75 ? 'bg-green-500' :
                score >= 50 ? 'bg-blue-500' :
                'bg-amber-500'
              } text-white`}>
                {getScoreGrade(score)}
              </Badge>
              <p className="text-xs text-gray-500 mt-1">out of 100</p>
            </div>
          </div>

          {/* Insights */}
          <div className="space-y-2">
            {gws.insights.slice(0, 2).map((insight, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 + index * 0.1 }}
                className="text-xs text-gray-600 dark:text-gray-400 flex items-start gap-1"
              >
                <Sparkles className="w-3 h-3 mt-0.5 flex-shrink-0 text-amber-500" />
                <span>{insight}</span>
              </motion.div>
            ))}
          </div>

          {/* Breakdown */}
          <Collapsible open={showBreakdown} onOpenChange={setShowBreakdown}>
            <CollapsibleTrigger className="w-full">
              <div className="flex items-center justify-between text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors">
                <span>View Breakdown</span>
                <ChevronDown className={`w-4 h-4 transition-transform ${showBreakdown ? 'rotate-180' : ''}`} />
              </div>
            </CollapsibleTrigger>
            <CollapsibleContent className="mt-4 space-y-3">
              {/* Utilization Component */}
              <div>
                <div className="flex items-center justify-between mb-1">
                  <div className="flex items-center gap-1 text-xs font-medium text-gray-700 dark:text-gray-300">
                    <TrendingUp className="w-3 h-3 text-emerald-500" />
                    {gws.components.utilization.label}
                  </div>
                  <span className="text-xs font-bold text-emerald-600">
                    {gws.components.utilization.score}/{gws.components.utilization.max}
                  </span>
                </div>
                <Progress value={(gws.components.utilization.score / gws.components.utilization.max) * 100} className="h-2" />
              </div>

              {/* CPW Component */}
              <div>
                <div className="flex items-center justify-between mb-1">
                  <div className="flex items-center gap-1 text-xs font-medium text-gray-700 dark:text-gray-300">
                    <DollarSign className="w-3 h-3 text-green-500" />
                    {gws.components.cpw_improvement.label}
                  </div>
                  <span className="text-xs font-bold text-green-600">
                    {gws.components.cpw_improvement.score}/{gws.components.cpw_improvement.max}
                  </span>
                </div>
                <Progress value={(gws.components.cpw_improvement.score / gws.components.cpw_improvement.max) * 100} className="h-2" />
              </div>

              {/* AI Fit Component */}
              <div>
                <div className="flex items-center justify-between mb-1">
                  <div className="flex items-center gap-1 text-xs font-medium text-gray-700 dark:text-gray-300">
                    <Brain className="w-3 h-3 text-blue-500" />
                    {gws.components.ai_fit.label}
                  </div>
                  <span className="text-xs font-bold text-blue-600">
                    {gws.components.ai_fit.score}/{gws.components.ai_fit.max}
                  </span>
                </div>
                <Progress value={(gws.components.ai_fit.score / gws.components.ai_fit.max) * 100} className="h-2" />
              </div>

              {/* Revived Items Component */}
              <div>
                <div className="flex items-center justify-between mb-1">
                  <div className="flex items-center gap-1 text-xs font-medium text-gray-700 dark:text-gray-300">
                    <Sparkles className="w-3 h-3 text-purple-500" />
                    {gws.components.revived_items.label}
                  </div>
                  <span className="text-xs font-bold text-purple-600">
                    {gws.components.revived_items.score}/{gws.components.revived_items.max}
                  </span>
                </div>
                <Progress value={(gws.components.revived_items.score / gws.components.revived_items.max) * 100} className="h-2" />
              </div>
            </CollapsibleContent>
          </Collapsible>
        </div>
      </CardContent>
    </Card>
  );
}

