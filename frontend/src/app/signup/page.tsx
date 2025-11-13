"use client";

import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ArrowLeft, Mail, Lock, Eye, EyeOff, User, CheckCircle, AlertCircle } from "lucide-react";
import { signUp } from "@/lib/auth";

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
  const searchParams = useSearchParams();
  const fromQuiz = searchParams?.get("from") === "quiz";

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
            }

            sessionStorage.removeItem("pendingQuizSubmission");
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

  return (
    <div className="min-h-screen bg-[#FAFAF9] dark:bg-[#1A1510] flex items-center justify-center p-4">
      <Card className="w-full max-w-md bg-white/85 dark:bg-[#2C2119]/85 border border-[#F5F0E8]/60 dark:border-[#3D2F24]/80 rounded-3xl shadow-2xl shadow-amber-500/10 backdrop-blur-xl">
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
                  size="sm"
                  className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                >
                  {showConfirmPassword ? (
                    <EyeOff className="h-4 w-4 text-gray-400" />
                  ) : (
                    <Eye className="h-4 w-4 text-gray-400" />
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
