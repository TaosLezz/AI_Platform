import { AppLayout } from '@/components/layout/app-layout';
import { ServiceCard } from '@/components/ui/service-card';
import { ResultCard } from '@/components/ui/result-card';
import { FileUpload } from '@/components/ui/file-upload';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { AIService } from '@/lib/types';
import { useAIStore } from '@/store/ai-store';
import { Link } from 'wouter';
import { Activity, TrendingUp, Clock, CheckCircle } from 'lucide-react';

const services: AIService[] = [
  {
    id: 'generate',
    name: 'Image Generation',
    description: 'Create stunning images from text prompts using advanced AI models',
    icon: 'fas fa-palette',
    avgTime: '~30s avg',
    status: 'active',
    color: 'bg-gradient-to-r from-purple-500 to-pink-500'
  },
  {
    id: 'classify',
    name: 'Classification',
    description: 'Identify and categorize objects in images with confidence scores',
    icon: 'fas fa-search',
    avgTime: '~2s avg',
    status: 'ready',
    color: 'bg-gradient-to-r from-blue-500 to-cyan-500'
  },
  {
    id: 'detect',
    name: 'Object Detection',
    description: 'Locate and identify multiple objects with bounding boxes',
    icon: 'fas fa-bullseye',
    avgTime: '~5s avg',
    status: 'ready',
    color: 'bg-gradient-to-r from-green-500 to-emerald-500'
  },
  {
    id: 'segment',
    name: 'Segmentation',
    description: 'Precise pixel-level object segmentation and masking',
    icon: 'fas fa-cut',
    avgTime: '~8s avg',
    status: 'ready',
    color: 'bg-gradient-to-r from-orange-500 to-red-500'
  },
  {
    id: 'chat',
    name: 'AI Chatbot',
    description: 'Intelligent conversations with context-aware responses',
    icon: 'fas fa-comments',
    avgTime: '~1s avg',
    status: 'ready',
    color: 'bg-gradient-to-r from-indigo-500 to-purple-500'
  }
];

export default function Dashboard() {
  const { recentJobs, setCurrentService } = useAIStore();

  const handleFileUpload = (file: File) => {
    console.log('File uploaded:', file.name);
    // Handle file upload logic here
  };

  const handleServiceClick = (serviceId: string) => {
    setCurrentService(serviceId);
  };

  const completedJobs = recentJobs.filter(job => job.status === 'completed').length;
  const totalProcessingTime = recentJobs.reduce((acc, job) => acc + (job.processingTime || 0), 0);

  return (
    <AppLayout 
      title="AI Services Dashboard" 
      description="Manage and monitor your AI workflows"
    >
      <div className="p-6 space-y-8">
        
        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card className="bg-gray-800/60 border-gray-700">
            <CardContent className="p-6">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-green-500/20 rounded-lg">
                  <CheckCircle className="w-6 h-6 text-green-400" />
                </div>
                <div>
                  <p className="text-sm text-gray-400">Completed Jobs</p>
                  <p className="text-2xl font-bold text-white">{completedJobs}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gray-800/60 border-gray-700">
            <CardContent className="p-6">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-blue-500/20 rounded-lg">
                  <Activity className="w-6 h-6 text-blue-400" />
                </div>
                <div>
                  <p className="text-sm text-gray-400">Services Active</p>
                  <p className="text-2xl font-bold text-white">5</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gray-800/60 border-gray-700">
            <CardContent className="p-6">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-purple-500/20 rounded-lg">
                  <Clock className="w-6 h-6 text-purple-400" />
                </div>
                <div>
                  <p className="text-sm text-gray-400">Avg Processing</p>
                  <p className="text-2xl font-bold text-white">
                    {completedJobs > 0 ? `${(totalProcessingTime / completedJobs / 1000).toFixed(1)}s` : '0s'}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gray-800/60 border-gray-700">
            <CardContent className="p-6">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-yellow-500/20 rounded-lg">
                  <TrendingUp className="w-6 h-6 text-yellow-400" />
                </div>
                <div>
                  <p className="text-sm text-gray-400">Success Rate</p>
                  <p className="text-2xl font-bold text-white">98.5%</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Service Cards */}
        <div>
          <h3 className="text-xl font-semibold text-white mb-6">AI Services</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {services.map((service) => (
              <Link key={service.id} href={`/${service.id}`}>
                <ServiceCard 
                  service={service}
                  onClick={() => handleServiceClick(service.id)}
                />
              </Link>
            ))}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          
          {/* File Upload */}
          <Card className="bg-gray-800/60 border-gray-700">
            <CardHeader>
              <CardTitle className="text-white flex items-center">
                <i className="fas fa-upload mr-2 text-primary-400"></i>
                Quick Upload
              </CardTitle>
            </CardHeader>
            <CardContent>
              <FileUpload onFileSelect={handleFileUpload} />
            </CardContent>
          </Card>

          {/* Recent Activity */}
          <Card className="bg-gray-800/60 border-gray-700">
            <CardHeader>
              <CardTitle className="text-white flex items-center justify-between">
                <span className="flex items-center">
                  <Activity className="w-5 h-5 mr-2 text-secondary-400" />
                  Recent Activity
                </span>
                <Link href="/jobs">
                  <Button variant="ghost" size="sm" className="text-primary-400 hover:text-primary-300">
                    View All
                  </Button>
                </Link>
              </CardTitle>
            </CardHeader>
            <CardContent>
              {recentJobs.length === 0 ? (
                <div className="text-center text-gray-500 py-8">
                  <Activity className="w-12 h-12 mx-auto mb-3 text-gray-600" />
                  <p>No recent activity</p>
                  <p className="text-sm">Start using AI services to see results here</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {recentJobs.slice(0, 5).map((job) => (
                    <div key={job.id} className="flex items-center space-x-3 p-3 bg-gray-700/50 rounded-lg">
                      <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                        job.status === 'completed' ? 'bg-green-500/20' :
                        job.status === 'failed' ? 'bg-red-500/20' :
                        'bg-blue-500/20'
                      }`}>
                        {job.status === 'completed' ? (
                          <CheckCircle className="w-4 h-4 text-green-400" />
                        ) : job.status === 'failed' ? (
                          <i className="fas fa-exclamation-triangle text-red-400 text-sm" />
                        ) : (
                          <div className="w-3 h-3 border-2 border-blue-400 border-t-transparent rounded-full animate-spin" />
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-white">
                          {/* {job.serviceType.charAt(0).toUpperCase() + job.serviceType.slice(1)} */}
                          {job?.serviceType
                            ? job.serviceType.charAt(0).toUpperCase() + job.serviceType.slice(1)
                            : "No Service Type"}
                        </p>
                        <p className="text-xs text-gray-400 truncate">
                          {job.prompt || 'Processing...'}
                        </p>
                      </div>
                      <div className="text-xs text-gray-500">
                        {job.createdAt && new Date(job.createdAt).toLocaleTimeString()}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Recent Results */}
        {recentJobs.filter(job => job.status === 'completed' && job.result?.url).length > 0 && (
          <div>
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold text-white">Recent Results</h3>
              <Button variant="ghost" className="text-primary-400 hover:text-primary-300">
                View All Results
              </Button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {recentJobs
                .filter(job => job.status === 'completed' && job.result?.url)
                .slice(0, 6)
                .map((job, index) => (
                  <ResultCard 
                    key={job.id} 
                    job={job} 
                    featured={index === 0}
                  />
                ))}
            </div>
          </div>
        )}
      </div>
    </AppLayout>
  );
}
