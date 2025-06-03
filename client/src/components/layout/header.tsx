<<<<<<< HEAD
import { Bell, Settings, Zap } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useAIStore } from '@/store/ai-store';
=======
import { Bell, Settings, Zap, User, LogOut, HelpCircle, ChevronDown } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { 
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { useAIStore } from '@/store/ai-store';
import { useLocation } from 'wouter';
>>>>>>> feature/segment

interface HeaderProps {
  title: string;
  description: string;
}

<<<<<<< HEAD
export function Header({ title, description }: HeaderProps) {
  const { processingStatus } = useAIStore();
=======
const mockUser = {
  id: '1',
  name: 'Nguyễn Văn A',
  email: 'user@example.com',
  avatar: undefined,
  plan: 'Pro' as const,
};

function UserProfileDropdown({ onSettings, onHelp, onLogout }: {
  onSettings: () => void;
  onHelp: () => void;
  onLogout: () => void;
}) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button 
          variant="ghost" 
          size="sm" 
          className="text-gray-300 hover:text-white hover:bg-gray-700/50 p-1"
        >
          <ChevronDown className="w-4 h-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-48 bg-gray-800 border-gray-700">
        <DropdownMenuItem 
          onClick={onSettings}
          className="text-gray-300 hover:text-white hover:bg-gray-700 cursor-pointer"
        >
          <Settings className="w-4 h-4 mr-2" />
          Settings
        </DropdownMenuItem>
        <DropdownMenuItem 
          onClick={onHelp}
          className="text-gray-300 hover:text-white hover:bg-gray-700 cursor-pointer"
        >
          <HelpCircle className="w-4 h-4 mr-2" />
          Help & Support
        </DropdownMenuItem>
        <DropdownMenuSeparator className="bg-gray-700" />
        <DropdownMenuItem 
          onClick={onLogout}
          className="text-red-400 hover:text-red-300 hover:bg-red-900/20 cursor-pointer"
        >
          <LogOut className="w-4 h-4 mr-2" />
          Logout
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

export function Header({ title, description }: HeaderProps) {
  const { processingStatus, recentJobs = [] } = useAIStore();
  const [, setLocation] = useLocation();

  const handleLogout = () => {
    console.log('Logging out...');
    // Thêm logic logout thật ở đây
  };

  const handleSettings = () => setLocation('/settings');
  const handleHelp = () => setLocation('/help');

  const completedJobs = recentJobs.filter(job => job.status === 'completed').length;
>>>>>>> feature/segment

  return (
    <header className="bg-gray-800/60 backdrop-blur-sm border-b border-gray-700 px-6 py-4">
      <div className="flex items-center justify-between">
<<<<<<< HEAD
=======
        {/* Title & Description */}
>>>>>>> feature/segment
        <div>
          <h2 className="text-2xl font-bold text-white">{title}</h2>
          <p className="text-gray-400">{description}</p>
        </div>
<<<<<<< HEAD
        
        <div className="flex items-center space-x-4">
          {/* Processing Status */}
          <div className="bg-gray-800/60 rounded-lg px-4 py-2">
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${
=======

        {/* Right Controls */}
        <div className="flex items-center space-x-4">
          {/* Processing Status */}
          <div className="bg-gray-700/50 rounded-lg px-3 py-2">
            <div className="flex items-center space-x-2">
              <span className={`w-2 h-2 rounded-full ${
>>>>>>> feature/segment
                processingStatus.isProcessing 
                  ? 'bg-blue-400 animate-pulse' 
                  : 'bg-green-400'
              }`} />
              <span className="text-sm text-white">
                {processingStatus.isProcessing ? 'Processing...' : 'Ready'}
              </span>
            </div>
          </div>

<<<<<<< HEAD
          {/* GPU Status */}
          <div className="bg-gray-800/60 rounded-lg px-4 py-2">
            <div className="flex items-center space-x-2">
              <Zap className="w-4 h-4 text-yellow-400" />
              <span className="text-sm text-white">GPU Available</span>
            </div>
          </div>

=======
>>>>>>> feature/segment
          {/* Notifications */}
          <Button
            variant="ghost"
            size="sm"
            className="relative text-gray-400 hover:text-white"
<<<<<<< HEAD
=======
            aria-label="Notifications"
>>>>>>> feature/segment
          >
            <Bell className="w-5 h-5" />
            <Badge 
              variant="destructive" 
<<<<<<< HEAD
              className="absolute -top-1 -right-1 w-5 h-5 text-xs flex items-center justify-center p-0"
=======
              className="absolute -top-1 -right-1 w-4 h-4 text-xs flex items-center justify-center p-0"
>>>>>>> feature/segment
            >
              3
            </Badge>
          </Button>

<<<<<<< HEAD
          {/* Settings */}
          <Button
            variant="ghost"
            size="sm"
            className="text-gray-400 hover:text-white"
          >
            <Settings className="w-5 h-5" />
          </Button>
=======
          {/* User Profile */}
          <div className="flex items-center space-x-3">
            <Avatar className="w-8 h-8">
              <AvatarImage src={mockUser.avatar} alt={mockUser.name} />
              <AvatarFallback className="bg-primary-500 text-white text-sm">
                {mockUser.name.charAt(0).toUpperCase()}
              </AvatarFallback>
            </Avatar>

            <div className="hidden md:block">
              <p className="text-sm font-medium text-white">{mockUser.name.split(' ')[0]}</p>
              <div className="flex items-center space-x-2">
                <Badge variant="secondary" className="text-xs px-1.5 py-0.5">
                  {mockUser.plan}
                </Badge>
                <span className="text-xs text-gray-400">{completedJobs} jobs</span>
              </div>
            </div>

            <UserProfileDropdown
              onSettings={handleSettings}
              onHelp={handleHelp}
              onLogout={handleLogout}
            />
          </div>
>>>>>>> feature/segment
        </div>
      </div>
    </header>
  );
}
