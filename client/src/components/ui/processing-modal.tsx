import { useEffect, useState } from 'react';
import { Dialog, DialogContent } from '@/components/ui/dialog';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { Sparkles, X } from 'lucide-react';
import { useAIStore } from '@/store/ai-store';

export function ProcessingModal() {
  const { processingStatus, setProcessingStatus } = useAIStore();
  const [progress, setProgress] = useState(0);
  const [timeRemaining, setTimeRemaining] = useState(0);

  useEffect(() => {
    if (!processingStatus.isProcessing) {
      setProgress(0);
      setTimeRemaining(0);
      return;
    }

    const startTime = Date.now();
    const estimatedDuration = processingStatus.estimatedTime || 30000;

    const interval = setInterval(() => {
      const elapsed = Date.now() - startTime;
      const newProgress = Math.min((elapsed / estimatedDuration) * 100, 95);
      const remaining = Math.max(estimatedDuration - elapsed, 0);
      
      setProgress(newProgress);
      setTimeRemaining(remaining);
    }, 100);

    return () => clearInterval(interval);
  }, [processingStatus.isProcessing, processingStatus.estimatedTime]);

  const handleCancel = () => {
    setProcessingStatus({ isProcessing: false });
  };

  const formatTime = (ms: number) => {
    const seconds = Math.ceil(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    
    if (minutes > 0) {
      return `${minutes}m ${remainingSeconds}s`;
    }
    return `${remainingSeconds}s`;
  };

  return (
    <Dialog open={processingStatus.isProcessing} onOpenChange={() => {}}>
      <DialogContent className="sm:max-w-md bg-dark-800 border-gray-700">
        <div className="text-center space-y-6">
          {/* Icon */}
          <div className="flex justify-center">
            <div className="w-16 h-16 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-full flex items-center justify-center animate-pulse">
              <Sparkles className="w-8 h-8 text-white" />
            </div>
          </div>

          {/* Title */}
          <div>
            <h3 className="text-xl font-semibold text-white mb-2">
              {processingStatus.message || "Processing Your Request"}
            </h3>
            <p className="text-gray-400">
              Please wait while our AI creates your masterpiece...
            </p>
          </div>

          {/* Progress */}
          <div className="space-y-3">
            <Progress 
              value={progress} 
              className="w-full h-3"
            />
            
            <div className="flex justify-between text-sm text-gray-400">
              {processingStatus.currentStep && processingStatus.totalSteps ? (
                <span>Step {processingStatus.currentStep}/{processingStatus.totalSteps}</span>
              ) : (
                <span>{Math.round(progress)}% complete</span>
              )}
              {timeRemaining > 0 && (
                <span>~{formatTime(timeRemaining)} remaining</span>
              )}
            </div>
          </div>

          {/* Actions */}
          <div className="flex justify-center">
            <Button
              variant="outline"
              onClick={handleCancel}
              className="bg-gray-800 border-gray-600 hover:bg-gray-700"
            >
              <X className="w-4 h-4 mr-2" />
              Cancel
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
