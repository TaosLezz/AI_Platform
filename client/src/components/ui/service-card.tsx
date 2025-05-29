import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Clock, ArrowRight } from 'lucide-react';
import { cn } from '@/lib/utils';
import { AIService } from '@/lib/types';

interface ServiceCardProps {
  service: AIService;
  onClick?: () => void;
  isActive?: boolean;
  className?: string;
}

export function ServiceCard({ service, onClick, isActive, className }: ServiceCardProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-500/20 text-green-400';
      case 'ready': return 'bg-blue-500/20 text-blue-400';
      case 'monitoring': return 'bg-yellow-500/20 text-yellow-400';
      default: return 'bg-gray-500/20 text-gray-400';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'active': return 'Active';
      case 'ready': return 'Ready';
      case 'monitoring': return 'Monitoring';
      default: return 'Unknown';
    }
  };

  return (
    <Card 
      className={cn(
        "cursor-pointer transition-all duration-300 hover:scale-105 hover:shadow-xl",
        "bg-gray-800/60 backdrop-blur-sm border-gray-700",
        "hover:bg-gray-800/80 hover:border-primary-500/50",
        isActive && "border-primary-500 bg-primary-500/10",
        className
      )}
      onClick={onClick}
    >
      <CardContent className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div 
            className={cn(
              "w-12 h-12 rounded-lg flex items-center justify-center",
              service.color
            )}
          >
            <i className={`${service.icon} text-white text-xl`} />
          </div>
          <Badge 
            variant="secondary"
            className={cn("text-xs", getStatusColor(service.status))}
          >
            {getStatusText(service.status)}
          </Badge>
        </div>

        <h3 className="text-lg font-semibold text-white mb-2">
          {service.name}
        </h3>
        
        <p className="text-gray-400 text-sm mb-4 line-clamp-2">
          {service.description}
        </p>

        <div className="flex items-center justify-between">
          <div className="flex items-center text-xs text-gray-500">
            <Clock className="w-3 h-3 mr-1" />
            {service.avgTime}
          </div>
          <ArrowRight className="w-4 h-4 text-primary-400" />
        </div>
      </CardContent>
    </Card>
  );
}
