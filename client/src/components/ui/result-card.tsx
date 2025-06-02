import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Download, Expand, Heart, Clock, CheckCircle, AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';
import { AIJob } from '@/lib/types';

interface ResultCardProps {
  job: AIJob;
  className?: string;
  featured?: boolean;
}

export function ResultCard({ job, className, featured }: ResultCardProps) {
  const [isLiked, setIsLiked] = useState(false);
  const [imageError, setImageError] = useState(false);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle className="w-3 h-3 text-green-400" />;
      case 'failed': return <AlertCircle className="w-3 h-3 text-red-400" />;
      case 'processing': return <div className="w-3 h-3 border-2 border-blue-400 border-t-transparent rounded-full animate-spin" />;
      default: return <Clock className="w-3 h-3 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-500/20 text-green-400';
      case 'failed': return 'bg-red-500/20 text-red-400';
      case 'processing': return 'bg-blue-500/20 text-blue-400';
      default: return 'bg-gray-500/20 text-gray-400';
    }
  };

  const getServiceLabel = (serviceType: string) => {
    switch (serviceType) {
      case 'generate': return 'Generation';
      case 'classify': return 'Classification';
      case 'detect': return 'Detection';
      case 'segment': return 'Segmentation';
      default: return serviceType;
    }
  };

  const formatTimeAgo = (date: Date) => {
    if (!date || !(date instanceof Date) || isNaN(date.getTime())) return "Unknown time";
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} min ago`;
    
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    
    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays}d ago`;
  };

  const handleDownload = () => {
    if (job.result?.url) {
      const link = document.createElement('a');
      link.href = job.result.url;
      link.download = `ai-result-${job.id}.jpg`;
      link.click();
    }
  };

  const cardContent = (
    <CardContent className="p-4">
      {/* Image/Result Display */}
      <div className="aspect-square mb-4 relative group rounded-lg overflow-hidden bg-gray-700">
        {job.result?.url && !imageError ? (
          <>
            <img 
              src={job.result.url} 
              alt={job.prompt || 'AI Result'} 
              className="w-full h-full object-cover"
              onError={() => setImageError(true)}
            />
            {/* Hover Overlay */}
            <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-50 transition-all duration-300 flex items-center justify-center opacity-0 group-hover:opacity-100">
              <div className="flex space-x-3">
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={handleDownload}
                  className="bg-black/50 hover:bg-black/70 text-white"
                >
                  <Download className="w-4 h-4" />
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  className="bg-black/50 hover:bg-black/70 text-white"
                >
                  <Expand className="w-4 h-4" />
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => setIsLiked(!isLiked)}
                  className="bg-black/50 hover:bg-black/70 text-white"
                >
                  <Heart className={cn("w-4 h-4", isLiked && "fill-red-400 text-red-400")} />
                </Button>
              </div>
            </div>
          </>
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-500">
            <div className="text-center">
              <AlertCircle className="w-8 h-8 mx-auto mb-2" />
              <p className="text-sm">No preview available</p>
            </div>
          </div>
        )}
      </div>

      {/* Content */}
      <div className="space-y-3">
        {/* Prompt/Description */}
        <p className="text-sm text-gray-300 line-clamp-2">
          {job.prompt || job.result?.description || 'AI processing result'}
        </p>

        {/* meta_data */}
        <div className="flex items-center justify-between text-xs text-gray-400">
          <span>{job.result?.resolution || '1024x1024'}</span>
          <span>{formatTimeAgo(job.createdAt)}</span>
        </div>

        {/* Status and Service Type */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            {getStatusIcon(job.status)}
            <span className="text-xs text-gray-400">{job.status}</span>
          </div>
          
          {job.result?.confidence && (
            <span className="text-xs text-gray-400">
              Confidence: {Math.round(job.result.confidence * 100)}%
            </span>
          )}
        </div>

        {/* Service Badge */}
        <div className="flex items-center justify-between">
          <Badge 
            variant="secondary"
            className={getStatusColor(job.status)}
          >
            {getServiceLabel(job.serviceType)}
          </Badge>
          
          {job.processingTime && (
            <span className="text-xs text-gray-500">
              {(job.processingTime / 1000).toFixed(1)}s
            </span>
          )}
        </div>
      </div>
    </CardContent>
  );

  if (featured) {
    return (
      <div className={cn("relative", className)}>
        <div className="absolute -inset-0.5 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-xl opacity-75"></div>
        <Card className="relative bg-dark-800 border-0">
          {cardContent}
        </Card>
      </div>
    );
  }

  return (
    <Card className={cn(
      "bg-gray-800/60 backdrop-blur-sm border-gray-700 hover:border-gray-600 transition-colors",
      className
    )}>
      {cardContent}
    </Card>
  );
}
