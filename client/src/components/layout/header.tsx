import { Bell, Settings, Zap } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useAIStore } from '@/store/ai-store';

interface HeaderProps {
  title: string;
  description: string;
}

export function Header({ title, description }: HeaderProps) {
  const { processingStatus } = useAIStore();

  return (
    <header className="bg-gray-800/60 backdrop-blur-sm border-b border-gray-700 px-6 py-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">{title}</h2>
          <p className="text-gray-400">{description}</p>
        </div>
        
        <div className="flex items-center space-x-4">
          {/* Processing Status */}
          <div className="bg-gray-800/60 rounded-lg px-4 py-2">
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${
                processingStatus.isProcessing 
                  ? 'bg-blue-400 animate-pulse' 
                  : 'bg-green-400'
              }`} />
              <span className="text-sm text-white">
                {processingStatus.isProcessing ? 'Processing...' : 'Ready'}
              </span>
            </div>
          </div>

          {/* GPU Status */}
          <div className="bg-gray-800/60 rounded-lg px-4 py-2">
            <div className="flex items-center space-x-2">
              <Zap className="w-4 h-4 text-yellow-400" />
              <span className="text-sm text-white">GPU Available</span>
            </div>
          </div>

          {/* Notifications */}
          <Button
            variant="ghost"
            size="sm"
            className="relative text-gray-400 hover:text-white"
          >
            <Bell className="w-5 h-5" />
            <Badge 
              variant="destructive" 
              className="absolute -top-1 -right-1 w-5 h-5 text-xs flex items-center justify-center p-0"
            >
              3
            </Badge>
          </Button>

          {/* Settings */}
          <Button
            variant="ghost"
            size="sm"
            className="text-gray-400 hover:text-white"
          >
            <Settings className="w-5 h-5" />
          </Button>
        </div>
      </div>
    </header>
  );
}
