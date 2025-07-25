'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from '@/components/ui/alert-dialog';
import { toast } from 'sonner';

interface FixSuggestion {
  rule_type: string;
  rule_path: string;
  current_value: any;
  suggested_value: any;
  reason: string;
  fixable: boolean;
}

interface FixButtonProps {
  errorType: string;
  errorDetails: any;
  onFixApplied?: () => void;
  className?: string;
}

export function FixButton({ errorType, errorDetails, onFixApplied, className }: FixButtonProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [suggestion, setSuggestion] = useState<FixSuggestion | null>(null);
  const [showDialog, setShowDialog] = useState(false);

  const generateFixSuggestion = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/validation-rules/generate-fix-suggestion', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          error_type: errorType,
          error_details: errorDetails,
        }),
      });

      const data = await response.json();
      
      if (data.success && data.suggestion) {
        setSuggestion(data.suggestion);
        setShowDialog(true);
      } else {
        toast.error('No fixable suggestion available for this error');
      }
    } catch (error) {
      console.error('Error generating fix suggestion:', error);
      toast.error('Failed to generate fix suggestion');
    } finally {
      setIsLoading(false);
    }
  };

  const applyFix = async () => {
    if (!suggestion) return;
    
    setIsLoading(true);
    try {
      const response = await fetch('/api/validation-rules/apply-fix', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(suggestion),
      });

      const data = await response.json();
      
      if (data.success) {
        toast.success('✅ Fix applied successfully!');
        setShowDialog(false);
        setSuggestion(null);
        onFixApplied?.();
      } else {
        toast.error(`❌ Fix failed: ${data.error}`);
      }
    } catch (error) {
      console.error('Error applying fix:', error);
      toast.error('Failed to apply fix');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <Button
        onClick={generateFixSuggestion}
        disabled={isLoading}
        variant="outline"
        size="sm"
        className={className}
      >
        {isLoading ? '🔄 Generating...' : '🛠️ Fix This'}
      </Button>

      <AlertDialog open={showDialog} onOpenChange={setShowDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Apply Fix to Validation Rules</AlertDialogTitle>
            <AlertDialogDescription>
              This will update the validation rules to prevent this error in future outfit generations.
            </AlertDialogDescription>
          </AlertDialogHeader>
          
          {suggestion && (
            <div className="space-y-4">
              <div className="bg-muted p-4 rounded-lg">
                <h4 className="font-semibold mb-2">Fix Details:</h4>
                <div className="space-y-2 text-sm">
                  <div><strong>Rule:</strong> {suggestion.rule_path}</div>
                  <div><strong>Current Value:</strong> {suggestion.current_value}</div>
                  <div><strong>New Value:</strong> {suggestion.suggested_value}</div>
                  <div><strong>Reason:</strong> {suggestion.reason}</div>
                </div>
              </div>
            </div>
          )}
          
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={applyFix} disabled={isLoading}>
              {isLoading ? 'Applying...' : 'Apply Fix'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
