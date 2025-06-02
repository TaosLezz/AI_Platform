import { Link, useLocation } from 'wouter';
import { cn } from '@/lib/utils';
import { Badge } from '@/components/ui/badge';
import { 
  Palette, 
  Search, 
  Target, 
  Scissors, 
  MessageCircle, 
  BarChart3, 
  Database,
  Brain,
  Activity
} from 'lucide-react';

const navigation = [
  {
    title: 'Services',
    items: [
      { name: 'Image Generation', href: '/generate', icon: Palette, description: 'Text to Image' },
      { name: 'Classification', href: '/classify', icon: Search, description: 'Image Analysis' },
      { name: 'Object Detection', href: '/detect', icon: Target, description: 'Object Finder' },
      { name: 'Segmentation', href: '/segment', icon: Scissors, description: 'Pixel Precision' },
      { name: 'Chatbot', href: '/chat', icon: MessageCircle, description: 'AI Assistant' },
    ]
  },
  {
    title: 'Analytics',
    items: [
      { name: 'MLflow Dashboard', href: '/mlflow', icon: BarChart3, description: 'Experiments' },
      { name: 'Model Registry', href: '/models', icon: Database, description: 'Model Store' },
    ]
  }
];

export function Sidebar() {
  const [location] = useLocation();

  return (
    <div className="w-64 bg-gray-800/60 backdrop-blur-sm border-r border-gray-700 flex flex-col">
      {/* Logo Section */}
      <div className="p-6 border-b border-gray-700">
        <Link href="/">
          <div className="flex items-center space-x-3 cursor-pointer">
            <div className="w-10 h-10 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-xl flex items-center justify-center">
              <Brain className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white">AI Portfolio</h1>
              <p className="text-gray-400 text-sm">Platform v2.0</p>
            </div>
          </div>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-6 overflow-y-auto">
        {navigation.map((section) => (
          <div key={section.title}>
            <div className="text-gray-400 text-xs font-semibold uppercase tracking-wider mb-4">
              {section.title}
            </div>
            <div className="space-y-2">
              {section.items.map((item) => {
                const isActive = location === item.href;
                const Icon = item.icon;
                
                return (
                  <Link key={item.href} href={item.href}>
                    <div 
                      className={cn(
                        "flex items-center space-x-3 px-4 py-3 rounded-lg transition-all duration-200 cursor-pointer group",
                        isActive 
                          ? "bg-primary-500/20 text-primary-400 border border-primary-500/30" 
                          : "text-gray-300 hover:text-white hover:bg-gray-700/50"
                      )}
                    >
                      <Icon className="w-5 h-5" />
                      <div className="flex-1 min-w-0">
                        <span className="text-sm font-medium">{item.name}</span>
                        {item.description && (
                          <p className="text-xs text-gray-500 group-hover:text-gray-400 transition-colors">
                            {item.description}
                          </p>
                        )}
                      </div>
                    </div>
                  </Link>
                );
              })}
            </div>
          </div>
        ))}
      </nav>

      {/* Status Section */}
      <div className="p-4 border-t border-gray-700">
        <div className="bg-gray-800/60 rounded-lg p-3">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">System Status</span>
            <div className="flex items-center space-x-1">
              <Activity className="w-2 h-2 text-green-400 animate-pulse" />
              <span className="text-xs text-green-400">Online</span>
            </div>
          </div>
          <div className="text-xs text-gray-500">
            All services operational
          </div>
        </div>
      </div>
    </div>
  );
}
