import { useState, useEffect } from 'react';
import { useOnboardingStore } from '@/lib/store/onboardingStore';
import { StepProps } from '@/components/onboarding/StepWizard';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent } from '@/components/ui/card';
import { useToast } from '@/components/ui/use-toast';
import { useFirebase } from '@/lib/firebase-context';

export function StepEmailInput({ onNext, onPrevious }: StepProps) {
  const { email, name, setBasicInfo } = useOnboardingStore();
  const { user } = useFirebase();
  const { toast } = useToast();
  const [firstName, setFirstName] = useState(name.split(' ')[0] || '');
  const [lastName, setLastName] = useState(name.split(' ').slice(1).join(' ') || '');
  const [emailInput, setEmailInput] = useState(email);

  // Auto-populate for authenticated users (but don't auto-advance)
  useEffect(() => {
    if (user && user.email && user.displayName && !firstName && !lastName) {
      // Auto-populate with Firebase user data
      const displayName = user.displayName || '';
      const nameParts = displayName.split(' ');
      const userFirstName = nameParts[0] || '';
      const userLastName = nameParts.slice(1).join(' ') || '';
      
      setFirstName(userFirstName);
      setLastName(userLastName);
      setEmailInput(user.email);
      
      // Pre-populate store but don't auto-advance
      setBasicInfo({
        name: displayName,
        email: user.email,
      });
    }
  }, [user, setBasicInfo, firstName, lastName]);

  const handleNext = () => {
    if (!firstName.trim() || !lastName.trim() || !emailInput.trim()) {
      toast({
        title: "Please fill in all fields",
        description: "We need your name and email to continue.",
        variant: "destructive",
      });
      return;
    }

    if (!isValidEmail(emailInput)) {
      toast({
        title: "Invalid email address",
        description: "Please enter a valid email address.",
        variant: "destructive",
      });
      return;
    }

    setBasicInfo({
      name: `${firstName.trim()} ${lastName.trim()}`,
      email: emailInput.trim(),
    });
    onNext();
  };

  const isValidEmail = (email: string) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };



  return (
    <div className="max-w-2xl mx-auto">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          Stay in the loop
        </h2>
        <p className="text-lg text-gray-600">
          Get personalized outfit recommendations and style tips delivered to your inbox.
        </p>
      </div>

      <Card className="p-6">
        <CardContent className="space-y-6">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="firstName">First Name</Label>
              <Input
                id="firstName"
                type="text"
                placeholder="Enter your first name"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                className="w-full"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="lastName">Last Name</Label>
              <Input
                id="lastName"
                type="text"
                placeholder="Enter your last name"
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
                className="w-full"
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="email">Email Address</Label>
            <Input
              id="email"
              type="email"
              placeholder="Enter your email address"
              value={emailInput}
              onChange={(e) => setEmailInput(e.target.value)}
              className="w-full"
            />
            <p className="text-sm text-gray-500">
              We&apos;ll send you personalized style recommendations and updates. You can unsubscribe at any time.
            </p>
          </div>
        </CardContent>
      </Card>

      <div className="flex justify-between mt-8">
        <Button variant="outline" onClick={onPrevious}>
          Previous
        </Button>
        <Button onClick={handleNext}>
          Next
        </Button>
      </div>
    </div>
  );
} 