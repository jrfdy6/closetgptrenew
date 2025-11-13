"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ArrowLeft, Mail, Lock, Eye, EyeOff, AlertCircle } from "lucide-react";
import { signIn } from "@/lib/auth";

export default function SignIn() {
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const router = useRouter();
  const [fromQuiz, setFromQuiz] = useState(false);

  useEffect(() => {
    if (typeof window !== "undefined") {
      const params = new URLSearchParams(window.location.search);
      setFromQuiz(params.get("from") === "quiz");
    }
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");
    
    try {
      const result = await signIn(email, password);
      
      if (result.success && result.user) {
        console.log("Signin successful:", result.user.email);

        if (fromQuiz && typeof window !== "undefined") {
          try {
            const pendingRaw = sessionStorage.getItem("pendingQuizSubmission");
            if (pendingRaw) {
              const pending = JSON.parse(pendingRaw);
              const token = await result.user.getIdToken();
              const submissionPayload = {
                userId: result.user.uid,
                token,
                answers: pending.answers || [],
                colorAnalysis: pending.colorAnalysis || null,
                stylePreferences: pending.stylePreferences || [],
                colorPreferences: pending.colorPreferences || []
              };

              await fetch("/api/style-quiz/submit", {
                method: "POST",
                headers: {
                  "Content-Type": "application/json",
                  "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify(submissionPayload)
              });

              sessionStorage.removeItem("pendingQuizSubmission");
            }
          } catch (quizError) {
            console.error("Failed to submit pending quiz after signin:", quizError);
          }

          router.push("/style-persona?from=quiz");
        } else {
          router.push("/dashboard");
        }
      } else {
        setError(result.error || "Sign in failed");
        console.error("Signin error:", result.error);
      }
    } catch (err: any) {
      setError(err.message || "An unexpected error occurred");
      console.error("Signin exception:", err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#FAFAF9] dark:bg-[#1A1510] flex items-center justify-center p-4">
      <Card className="w-full max-w-md bg-white/85 dark:bg-[#2C2119]/85 border border-[#F5F0E8]/60 dark:border-[#3D2F24]/80 rounded-3xl shadow-2xl shadow-amber-500/10 backdrop-blur-xl">
        <CardHeader className="text-center space-y-4 pb-8">
          <Link href="/" className="inline-flex items-center text-sm text-[#57534E] hover:text-[#1C1917] dark:text-[#C4BCB4] dark:hover:text-[#F8F5F1] mb-6 font-medium transition-colors">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Home
          </Link>
          <CardTitle className="text-3xl font-display font-semibold text-[#1C1917] dark:text-[#F8F5F1]">
            Welcome back
          </CardTitle>
          <CardDescription className="text-[#57534E] dark:text-[#C4BCB4] font-light text-lg">
            Sign in to your Easy Outfit account
          </CardDescription>
        </CardHeader>
        <CardContent>
          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md flex items-center space-x-2">
              <AlertCircle className="h-4 w-4 text-red-500" />
              <span className="text-sm text-red-700">{error}</span>
            </div>
          )}
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email" className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Email
              </Label>
              <div className="relative">
                <Mail className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input
                  id="email"
                  type="email"
                  placeholder="Enter your email"
                  className="pl-10"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="password" className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Password
              </Label>
              <div className="relative">
                <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  placeholder="Enter your password"
                  className="pl-10 pr-10"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? (
                    <EyeOff className="h-4 w-4 text-gray-400" />
                  ) : (
                    <Eye className="h-4 w-4 text-gray-400" />
                  )}
                </Button>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <Link
                href="/forgot-password"
                className="text-sm text-amber-700 hover:text-amber-800 dark:text-[#FFCC66] dark:hover:text-[#FFB84C] transition-colors"
              >
                Forgot password?
              </Link>
            </div>

            <Button
              type="submit"
              className="w-full bg-gradient-to-r from-[#FFB84C] to-[#FF9400] text-[#1A1510] dark:text-white px-6 py-4 rounded-2xl font-semibold text-lg shadow-lg shadow-amber-500/25 transition-transform duration-200 hover:scale-[1.02] active:scale-[0.98]"
              disabled={isLoading}
            >
              {isLoading ? "Signing in..." : "Sign in"}
            </Button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm text-[#57534E] dark:text-[#C4BCB4]">
              Don't have an account?{" "}
              <Link 
                href="/signup" 
                className="font-medium text-amber-700 hover:text-amber-800 dark:text-[#FFCC66] dark:hover:text-[#FFB84C]"
              >
                Sign up
              </Link>
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
