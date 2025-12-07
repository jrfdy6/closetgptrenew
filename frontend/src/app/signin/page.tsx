"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ArrowLeft, Mail, Lock, Eye, EyeOff, AlertCircle } from "lucide-react";
import { signIn, signInWithGoogle, getSignInMethods } from "@/lib/auth";
import PasswordLinkPrompt from "@/components/PasswordLinkPrompt";
import PasswordLinkBanner from "@/components/PasswordLinkBanner";

export default function SignIn() {
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const router = useRouter();
  const [fromQuiz, setFromQuiz] = useState(false);
  const [showPasswordLinkPrompt, setShowPasswordLinkPrompt] = useState(false);
  const [googleSignInEmail, setGoogleSignInEmail] = useState("");
  const [showPasswordLinkBanner, setShowPasswordLinkBanner] = useState(false);
  const [googleSignInSuccess, setGoogleSignInSuccess] = useState(false);
  const [hasBothMethods, setHasBothMethods] = useState(false);
  const [checkedEmail, setCheckedEmail] = useState("");

  useEffect(() => {
    if (typeof window !== "undefined") {
      const params = new URLSearchParams(window.location.search);
      setFromQuiz(params.get("from") === "quiz");
    }
  }, []);

  // Check if email has both password and Google methods
  useEffect(() => {
    const checkEmailMethods = async () => {
      if (email && email.includes("@") && email !== checkedEmail) {
        try {
          const methodsResult = await getSignInMethods(email);
          if (methodsResult.success && methodsResult.methods) {
            const methods = methodsResult.methods;
            const hasPassword = methods.includes("password");
            const hasGoogle = methods.includes("google.com");
            
            // Hide form if both methods exist, OR if methods array is empty (Google account not linked)
            // Empty array indicates Google account exists but password isn't linked
            if ((hasPassword && hasGoogle) || (methods.length === 0)) {
              setHasBothMethods(true);
              setCheckedEmail(email);
              setError(""); // Clear any error when both methods detected
            } else {
              setHasBothMethods(false);
              setCheckedEmail(email);
            }
          } else {
            // If methods check fails, assume it might be a Google account
            // We'll let the error handler catch it if password sign-in fails
            setHasBothMethods(false);
            setCheckedEmail(email);
          }
        } catch (error) {
          setHasBothMethods(false);
          setCheckedEmail(email);
        }
      } else if (!email) {
        setHasBothMethods(false);
        setCheckedEmail("");
      }
    };

    // Debounce the check
    const timeoutId = setTimeout(() => {
      checkEmailMethods();
    }, 500);

    return () => clearTimeout(timeoutId);
  }, [email, checkedEmail]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Prevent submission if both methods are detected
    if (hasBothMethods) {
      setError("Please use Google sign-in for this account. After signing in, you can link your password in your profile settings.");
      return;
    }
    
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
        // Check if error indicates Google account - if so, hide the form
        if (result.error && (
          result.error.includes('Google account') || 
          result.error.includes('sign in with Google')
        )) {
          setHasBothMethods(true);
        }
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

  const handleGoogleSignIn = async () => {
    setIsLoading(true);
    setError("");
    
    try {
      const result = await signInWithGoogle();
      
      if (result.success && result.user) {
        console.log("Google signin successful:", result.user.email);

        // Check if password linking is needed
        if (result.needsPasswordLinking && result.user.email) {
          setGoogleSignInEmail(result.user.email);
          setShowPasswordLinkPrompt(true);
          setIsLoading(false);
          return; // Don't navigate yet - wait for password linking
        }

        // If password linking prompt didn't show, show banner instead
        // (in case password account exists but wasn't detected, or user skipped)
        if (result.user.email) {
          setGoogleSignInEmail(result.user.email);
          setGoogleSignInSuccess(true);
          setShowPasswordLinkBanner(true);
        }

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
            console.error("Failed to submit pending quiz after Google signin:", quizError);
          }

          router.push("/style-persona?from=quiz");
        } else {
          router.push("/dashboard");
        }
      } else {
        setError(result.error || "Google sign in failed");
        console.error("Google signin error:", result.error);
      }
    } catch (err: any) {
      setError(err.message || "An unexpected error occurred");
      console.error("Google signin exception:", err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <Card className="w-full max-w-md bg-card/85 dark:bg-card/85 border border-border/60 dark:border-border/70 rounded-3xl shadow-2xl shadow-amber-500/10 backdrop-blur-xl">
        <CardHeader className="text-center space-y-4 pb-8">
          <Link href="/" className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground mb-6 font-medium transition-colors">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Home
          </Link>
          <CardTitle className="text-3xl font-display font-semibold text-card-foreground">
            Welcome back
          </CardTitle>
          <CardDescription className="text-muted-foreground font-light text-lg">
            {hasBothMethods 
              ? "Your account is connected with Google. Please sign in with Google to continue."
              : "Sign in to your Easy Outfit account"
            }
          </CardDescription>
          {hasBothMethods && (
            <div className="mt-4 p-3 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg">
              <p className="text-xs text-amber-800 dark:text-amber-200 text-center">
                After signing in with Google, you can link your password in your profile settings to use both sign-in methods.
              </p>
            </div>
          )}
        </CardHeader>
        <CardContent>
          {error && (
            <div className={`mb-4 p-4 rounded-lg border ${
              error.includes('Google account') || error.includes('sign in with Google')
                ? 'bg-amber-50 dark:bg-amber-900/20 border-amber-200 dark:border-amber-800'
                : 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800'
            }`}>
              <div className="flex items-start space-x-3">
                <AlertCircle className={`h-5 w-5 mt-0.5 ${
                  error.includes('Google account') || error.includes('sign in with Google')
                    ? 'text-amber-600 dark:text-amber-400'
                    : 'text-red-600 dark:text-red-400'
                }`} />
                <div className="flex-1">
                  <p className={`text-sm font-medium ${
                    error.includes('Google account') || error.includes('sign in with Google')
                      ? 'text-amber-800 dark:text-amber-200'
                      : 'text-red-800 dark:text-red-200'
                  }`}>
                    {error}
                  </p>
                  {(error.includes('Google account') || error.includes('sign in with Google')) && (
                    <div className="mt-3">
                      <Button
                        type="button"
                        variant="outline"
                        className="w-full border-2 border-amber-300 dark:border-amber-700 text-amber-700 dark:text-amber-300 px-4 py-2 rounded-xl font-medium text-sm hover:bg-amber-100 dark:hover:bg-amber-900/30 transition-colors"
                        onClick={handleGoogleSignIn}
                        disabled={isLoading}
                      >
                        <svg className="mr-2 h-4 w-4" viewBox="0 0 24 24">
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
                        Sign in with Google instead
                      </Button>
                      <p className="mt-2 text-xs text-amber-700 dark:text-amber-300">
                        After signing in, you can link your password in your profile settings.
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {hasBothMethods && (
            <div className="mb-4 p-4 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg">
              <p className="text-sm text-amber-800 dark:text-amber-200">
                Your account is connected with Google. Please use the Google sign-in button above to continue.
              </p>
            </div>
          )}
          
          <Button
            type="button"
            variant="outline"
            className="w-full border-2 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 px-6 py-4 rounded-2xl font-semibold text-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors mb-6"
            onClick={handleGoogleSignIn}
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
            Sign in with Google
          </Button>

          {!hasBothMethods && (
            <>
              <div className="relative my-6">
                <div className="absolute inset-0 flex items-center">
                  <span className="w-full border-t border-gray-300 dark:border-gray-600" />
                </div>
                <div className="relative flex justify-center text-xs uppercase">
                  <span className="bg-card/85 dark:bg-card/85 px-2 text-muted-foreground">
                    Or continue with email
                  </span>
                </div>
              </div>
              
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

            <div className="flex items-center justify-between">
              <Link
                href="/forgot-password"
                className="text-sm text-primary hover:text-primary/90 transition-colors"
              >
                Forgot password?
              </Link>
            </div>

            <Button
              type="submit"
              className="w-full bg-gradient-to-r from-primary to-accent text-primary-foreground px-6 py-4 rounded-2xl font-semibold text-lg shadow-lg shadow-amber-500/25 transition-transform duration-200 hover:scale-[1.02] active:scale-[0.98]"
              disabled={isLoading}
            >
              {isLoading ? "Signing in..." : "Sign in"}
            </Button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm text-muted-foreground">
              Don't have an account?{" "}
              <Link 
                href="/signup" 
                className="font-medium text-primary hover:text-primary/90"
              >
                Sign up
              </Link>
            </p>
          </div>
          </>
          )}
        </CardContent>
      </Card>

      <PasswordLinkPrompt
        email={googleSignInEmail}
        open={showPasswordLinkPrompt}
        onClose={() => {
          setShowPasswordLinkPrompt(false);
          // Navigate after closing prompt
          if (fromQuiz) {
            router.push("/style-persona?from=quiz");
          } else {
            router.push("/dashboard");
          }
        }}
        onSuccess={() => {
          setShowPasswordLinkPrompt(false);
          setShowPasswordLinkBanner(false);
          // Navigate after successful linking
          if (fromQuiz) {
            router.push("/style-persona?from=quiz");
          } else {
            router.push("/dashboard");
          }
        }}
      />

      {showPasswordLinkBanner && googleSignInSuccess && (
        <PasswordLinkBanner
          email={googleSignInEmail}
          onLinkClick={() => {
            setShowPasswordLinkBanner(false);
            setShowPasswordLinkPrompt(true);
          }}
        />
      )}
    </div>
  );
}
