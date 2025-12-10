"use client";

import React from "react";
import { Lock } from "lucide-react";
import { useSubscriptionPlan } from "@/hooks/useSubscriptionPlan";
import { SubscriptionPlan } from "@/types/subscription";

interface WithSubscriptionGateProps {
  forceUnlock?: boolean;
}

/**
 * Wrap a component with subscription gating. When access is insufficient,
 * the wrapped content is blurred and an overlay prompts upgrade.
 */
export function withSubscriptionGate<P extends object>(
  WrappedComponent: React.ComponentType<P>,
  requiredPlan: SubscriptionPlan = SubscriptionPlan.PRO,
  blurAmount: string = "6px"
) {
  const GatedComponent = (props: P & WithSubscriptionGateProps) => {
    const { forceUnlock, ...rest } = props;
    const { canAccess, loading, plan } = useSubscriptionPlan();

    const hasAccess = forceUnlock || (!loading && canAccess(requiredPlan));

    if (hasAccess) {
      return <WrappedComponent {...(rest as P)} />;
    }

    // Blurred preview with rosegold/creme overlay
    return (
      <div className="relative w-full h-full overflow-hidden rounded-xl group border border-[#C9956F]/25 bg-[#F5F0E8] dark:bg-[#251D18]">
        <div
          style={{ filter: `blur(${blurAmount})` }}
          className="w-full h-full pointer-events-none select-none opacity-70 transition-all duration-500"
          aria-hidden="true"
        >
          <WrappedComponent {...(rest as P)} />
        </div>

        <div className="absolute inset-0 z-10 flex flex-col items-center justify-center bg-gradient-to-b from-[#F5F0E8]/70 via-[#F5F0E8]/80 to-[#F5F0E8]/90 dark:from-[#1A1410]/70 dark:via-[#1A1410]/80 dark:to-[#1A1410]/90 p-4 text-center backdrop-blur-sm">
          <div className="bg-white/80 dark:bg-[#251D18]/90 border border-[#C9956F]/40 shadow-xl rounded-2xl p-5 max-w-sm w-full">
            <div className="mx-auto w-12 h-12 rounded-full bg-[#C9956F]/15 text-[#C9956F] flex items-center justify-center mb-3">
              <Lock className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-semibold text-[#4A3327] dark:text-[#F5F0E8] mb-2">
              {requiredPlan} feature
            </h3>
            <p className="text-sm text-[#6B4A3A] dark:text-[#E8D8CB] mb-4">
              You're leveling up -- unlock the 'why' behind your gains with PRO analytics.
            </p>
            <button
              onClick={() => (window.location.href = "/upgrade")}
              className="w-full py-2.5 px-4 bg-gradient-to-r from-[#C9956F] to-[#D4A574] text-white font-semibold rounded-lg shadow-sm hover:opacity-95 transition"
            >
              Upgrade to {requiredPlan === SubscriptionPlan.PRO ? "PRO" : "PREMIUM"}
            </button>
            <p className="mt-2 text-xs text-[#6B4A3A] dark:text-[#C7B4A6]">
              Current plan: {plan}
            </p>
          </div>
        </div>
      </div>
    );
  };

  GatedComponent.displayName = `WithSubscriptionGate(${WrappedComponent.displayName || WrappedComponent.name || "Component"})`;

  return GatedComponent;
}

