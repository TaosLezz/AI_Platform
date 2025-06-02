import { Sidebar } from './sidebar';
import { Header } from './header';
import { ProcessingModal } from '../ui/processing-modal';
import { useRecentJobs } from '@/hooks/use-ai-service';

interface AppLayoutProps {
  children: React.ReactNode;
  title: string;
  description: string;
}

export function AppLayout({ children, title, description }: AppLayoutProps) {
  // Initialize data fetching
  useRecentJobs();

  return (
    <div className="flex h-screen bg-gray-900">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header title={title} description={description} />
        <main className="flex-1 overflow-y-auto">
          {children}
        </main>
      </div>
      <ProcessingModal />
    </div>
  );
}
