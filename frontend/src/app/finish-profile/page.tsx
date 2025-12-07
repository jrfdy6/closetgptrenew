"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import Navigation from "@/components/Navigation";
import ClientOnlyNav from "@/components/ClientOnlyNav";
import { Button } from "@/components/ui/button";
import { Sparkles, ArrowRight, ShieldCheck } from "lucide-react";

interface PendingQuizPersona {
  id?: string;
  name?: string;
  tagline?: string;
}

interface PendingQuizSubmission {
  persona?: PendingQuizPersona;
  createdAt?: number;
}

export default function FinishProfilePage() {
  const router = useRouter();
  const [pendingData, setPendingData] = useState<PendingQuizSubmission | null>(null);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    if (typeof window === "undefined") return;

    try {
      const raw = sessionStorage.getItem("pendingQuizSubmission");
      if (!raw) {
        router.replace("/onboarding?mode=guest");
        return;
      }

      const parsed = JSON.parse(raw) as PendingQuizSubmission;
      setPendingData(parsed);
    } catch (error) {
      console.error("Failed to parse pending quiz submission:", error);
      sessionStorage.removeItem("pendingQuizSubmission");
      router.replace("/onboarding?mode=guest");
      return;
    } finally {
      setIsReady(true);
    }
  }, [router]);

  if (!isReady) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-amber-50 via-stone-50 to-orange-50 dark:from-amber-950 dark:via-amber-900 dark:to-orange-950 flex flex-col">
        <Navigation />
        <div className="flex-1 flex items-center justify-center px-6 py-16">
          <div className="text-center text-muted-foreground">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-amber-500 mx-auto mb-4"></div>
            Preparing your style journey...
          </div>
        </div>
        <ClientOnlyNav />
      </div>
    );
  }

  const personaName = pendingData?.persona?.name || "Your Signature Style";
  const personaTagline = pendingData?.persona?.tagline || "Let's finish setting things up.";

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-stone-50 to-orange-50 dark:from-amber-950 dark:via-amber-900 dark:to-orange-950 flex flex-col">
      <Navigation />

      <main className="flex-1">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="glass-float rounded-3xl p-8 sm:p-12 glass-shadow">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-6 mb-8">
              <div>
                <div className="inline-flex items-center px-3 py-1 rounded-full bg-amber-100 text-amber-800 dark:bg-amber-900/60 dark:text-amber-200 text-sm font-medium">
                  <ShieldCheck className="h-4 w-4 mr-2" />
                  Finish profile setup
                </div>
                <h1 className="mt-4 text-3xl sm:text-4xl font-serif font-semibold text-card-foreground leading-snug">
                  You're moments away from {personaName}
                </h1>
                <p className="mt-3 text-base sm:text-lg text-muted-foreground leading-relaxed">
                  {personaTagline} Complete your profile so we can unlock your personalized style persona and wardrobe plan.
                </p>
              </div>
              <div className="hidden sm:flex items-center justify-center w-24 h-24 rounded-full bg-gradient-to-br from-amber-200 to-orange-200 dark:from-amber-900/50 dark:to-orange-900/50">
                <Sparkles className="h-10 w-10 text-amber-600 dark:text-amber-300" />
              </div>
            </div>

            <div className="bg-card/70 dark:bg-card/80 border border-border/60 dark:border-border/70 rounded-2xl p-6 sm:p-8 space-y-6">
              <div className="space-y-3">
                <h2 className="text-xl font-semibold text-card-foreground">
                  Here's what's next
                </h2>
                <ul className="space-y-3 text-muted-foreground text-sm sm:text-base">
                  <li className="flex items-start gap-3">
                    <span className="mt-1 h-2 w-2 rounded-full bg-amber-500" />
                    Create your Easy Outfit account so we can save your results securely.
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="mt-1 h-2 w-2 rounded-full bg-amber-500" />
                    We'll instantly sync your quiz insights to your new profile.
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="mt-1 h-2 w-2 rounded-full bg-amber-500" />
                    You'll land directly on your personalized style persona dashboard.
                  </li>
                </ul>
              </div>

              <div className="flex flex-col sm:flex-row gap-3 sm:items-center sm:justify-between">
                <Button
                  asChild
                  className="w-full sm:w-auto bg-gradient-to-r from-primary to-accent hover:from-primary hover:to-accent/90 text-primary-foreground px-6 py-3 rounded-2xl font-semibold shadow-lg shadow-amber-500/20 transition-transform hover:scale-[1.02]"
                >
                  <Link href="/signup?from=quiz">
                    Finish profile & unlock my persona
                    <ArrowRight className="h-4 w-4 ml-2" />
                  </Link>
                </Button>

                <Link
                  href="/signin?from=quiz"
                  className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors text-center sm:text-left"
                >
                  Already have an account? Sign in instead
                </Link>
              </div>
            </div>

            <div className="mt-8 text-center">
              <button
                onClick={() => router.push("/onboarding?mode=guest")}
                className="inline-flex items-center text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
              >
                <ArrowRight className="h-4 w-4 mr-2 rotate-180" />
                Want to adjust your answers? Retake the quiz
              </button>
            </div>
          </div>
        </div>
      </main>

      <ClientOnlyNav />
    </div>
  );
}


