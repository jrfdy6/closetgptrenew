"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ArrowLeft, Mail, Lock, Eye, EyeOff, User, CheckCircle, AlertCircle } from "lucide-react";
import { signUp, signInWithGoogle } from "@/lib/auth";

export default function SignUp() {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    email: "",
    password: "",
    confirmPassword: ""
  });
  const router = useRouter();
  const [fromQuiz, setFromQuiz] = useState(false);

  useEffect(() => {
    if (typeof window !== "undefined") {
      const params = new URLSearchParams(window.location.search);
      setFromQuiz(params.get("from") === "quiz");
    }
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.id]: e.target.value
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");
    
    try {
      const result = await signUp(formData.email, formData.password);
      
      if (result.success) {
        console.log("Signup successful:", result.user?.email);
        if (fromQuiz && typeof window !== "undefined") {
          try {
            const pendingRaw = sessionStorage.getItem("pendingQuizSubmission");
            if (pendingRaw && result.user) {
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
            console.error("Failed to submit pending quiz after signup:", quizError);
          }

          router.push("/style-persona?from=quiz");
        } else {
          // Redirect to onboarding
          router.push("/onboarding");
        }
      } else {
        setError(result.error || "Sign up failed");
        console.error("Signup error:", result.error);
      }
    } catch (err: any) {
      setError(err.message || "An unexpected error occurred");
      console.error("Signup exception:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const isFormValid = formData.firstName && formData.lastName && formData.email && 
                     formData.password && formData.password === formData.confirmPassword;

  const handleGoogleSignUp = async () => {
    setIsLoading(true);
    setError("");
    
    try {
      const result = await signInWithGoogle();
      
      if (result.success && result.user) {
        console.log("Google signup successful:", result.user.email);

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
            console.error("Failed to submit pending quiz after Google signup:", quizError);
          }

          router.push("/style-persona?from=quiz");
        } else {
          // Redirect to onboarding
          router.push("/onboarding");
        }
      } else {
        setError(result.error || "Google sign up failed");
        console.error("Google signup error:", result.error);
      }
    } catch (err: any) {
      setError(err.message || "An unexpected error occurred");
      console.error("Google signup exception:", err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#FAFAF9] dark:bg-[#0D0D0D] flex items-center justify-center p-4">
      <Card className="w-full max-w-md bg-white/85 dark:bg-[#1A1A1A]/85 border border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70 rounded-3xl shadow-2xl shadow-amber-500/10 backdrop-blur-xl">
        <CardHeader className="text-center space-y-4 pb-8">
          <Link href="/" className="inline-flex items-center text-sm text-[#57534E] hover:text-[#1C1917] dark:text-[#C4BCB4] dark:hover:text-[#F8F5F1] mb-6 font-medium transition-colors">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Home
          </Link>
          <CardTitle className="text-3xl font-display font-semibold text-[#1C1917] dark:text-[#F8F5F1]">
            Create Account
          </CardTitle>
          <CardDescription className="text-[#57534E] dark:text-[#C4BCB4] font-light text-lg">
            Join Easy Outfit and discover your perfect style
          </CardDescription>
        </CardHeader>
        <CardContent>
          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md flex items-center space-x-2">
              <AlertCircle className="h-4 w-4 text-red-500" />
              <span className="text-sm text-red-700">{error}</span>
            </div>
          )}
          
          <Button
            type="button"
            variant="outline"
            className="w-full border-2 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 px-6 py-4 rounded-2xl font-semibold text-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors mb-6"
            onClick={handleGoogleSignUp}
            disabled={isLoading}
          >
            <svg className="mr-2 h-5 w-5" viewBox="0 0 24 24">
              <path
                fill="currentColor"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                fill="currentColor"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="currentColor"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
              />
              <path
                fill="currentColor"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
              />
            </svg>
            Sign up with Google
          </Button>

          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t border-gray-300 dark:border-gray-600" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-white/85 dark:bg-[#2C2119]/85 px-2 text-gray-500 dark:text-gray-400">
                Or continue with email
              </span>
            </div>
          </div>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="firstName" className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  First Name
                </Label>
                <div className="relative">
                  <User className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    id="firstName"
                    type="text"
                    placeholder="First name"
                    className="pl-10"
                    value={formData.firstName}
                    onChange={handleInputChange}
                    required
                  />
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="lastName" className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Last Name
                </Label>
                <div className="relative">
                  <User className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    id="lastName"
                    type="text"
                    placeholder="Last name"
                    className="pl-10"
                    value={formData.lastName}
                    onChange={handleInputChange}
                    required
                  />
                </div>
              </div>
            </div>

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
                  value={formData.email}
                  onChange={handleInputChange}
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
                  placeholder="Create a password"
                  className="pl-10 pr-10"
                  value={formData.password}
                  onChange={handleInputChange}
                  required
                />
                <Button
                  type="button"
                  variant="ghost"
                  className="absolute right-0 top-0 h-full min-h-[44px] min-w-[44px] px-3 py-2 hover:bg-transparent"
                  onClick={() => setShowPassword(!showPassword)}
                  aria-label={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? (
                    <EyeOff className="h-5 w-5 text-gray-400" />
                  ) : (
                    <Eye className="h-5 w-5 text-gray-400" />
                  )}
                </Button>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="confirmPassword" className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Confirm Password
              </Label>
              <div className="relative">
                <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input
                  id="confirmPassword"
                  type={showConfirmPassword ? "text" : "password"}
                  placeholder="Confirm your password"
                  className="pl-10 pr-10"
                  value={formData.confirmPassword}
                  onChange={handleInputChange}
                  required
                />
                <Button
                  type="button"
                  variant="ghost"
                  className="absolute right-0 top-0 h-full min-h-[44px] min-w-[44px] px-3 py-2 hover:bg-transparent"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  aria-label={showConfirmPassword ? "Hide confirm password" : "Show confirm password"}
                >
                  {showConfirmPassword ? (
                    <EyeOff className="h-5 w-5 text-gray-400" />
                  ) : (
                    <Eye className="h-5 w-5 text-gray-400" />
                  )}
                </Button>
              </div>
            </div>

            {formData.password && formData.confirmPassword && (
              <div className={`flex items-center space-x-2 text-sm ${
                formData.password === formData.confirmPassword 
                  ? 'text-green-600 dark:text-green-400' 
                  : 'text-red-600 dark:text-red-400'
              }`}>
                {formData.password === formData.confirmPassword ? (
                  <CheckCircle className="h-4 w-4" />
                ) : (
                  <div className="w-4 h-4 rounded-full border-2 border-red-600 dark:border-red-400" />
                )}
                <span>
                  {formData.password === formData.confirmPassword 
                    ? 'Passwords match' 
                    : 'Passwords do not match'
                  }
                </span>
              </div>
            )}

            <Button
              type="submit"
              className="w-full bg-gradient-to-r from-[#FFB84C] to-[#FF9400] text-[#1A1510] dark:text-white px-6 py-4 rounded-2xl font-semibold text-lg shadow-lg shadow-amber-500/25 transition-transform duration-200 hover:scale-[1.02] active:scale-[0.98]"
              disabled={isLoading || !isFormValid}
            >
              {isLoading ? "Creating account..." : "Create account"}
            </Button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm text-[#57534E] dark:text-[#C4BCB4]">
              Already have an account?{" "}
              <Link 
                href="/signin" 
                className="font-medium text-amber-700 hover:text-amber-800 dark:text-[#FFCC66] dark:hover:text-[#FFB84C]"
              >
                Sign in
              </Link>
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
