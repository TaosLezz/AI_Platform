import { useState } from 'react';
import { AppLayout } from '@/components/layout/app-layout';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Slider } from '@/components/ui/slider';
import { ResultCard } from '@/components/ui/result-card';
import { Sparkles, Shuffle, Save, Download } from 'lucide-react';
import { useImageGeneration } from '@/hooks/use-ai-service';
import { useAIStore } from '@/store/ai-store';
import { GenerationParameters } from '@/lib/types';

export default function GeneratePage() {
  const [prompt, setPrompt] = useState('A serene mountain landscape with snow-capped peaks reflecting in a crystal clear lake, surrounded by pine trees in golden autumn colors');
  const [parameters, setParameters] = useState<GenerationParameters>({
    style: 'photorealistic',
    resolution: '1024x1024',
    guidanceScale: 7.5,
    steps: 4
  });

  const generateMutation = useImageGeneration();
  const { recentJobs, lastGeneratedImage } = useAIStore();

  const handleGenerate = () => {
    if (!prompt.trim()) return;
    generateMutation.mutate({ prompt, parameters });
  };

  const handleRandomPrompt = () => {
    const prompts = [
      'A majestic dragon soaring over a medieval castle at sunset',
      'A futuristic cyberpunk city with neon lights and flying cars',
      'A peaceful zen garden with cherry blossoms and koi pond',
      'A space station orbiting a distant alien planet',
      'A cozy library filled with magical floating books',
      'An underwater coral reef city with mermaids and sea creatures'
    ];
    setPrompt(prompts[Math.floor(Math.random() * prompts.length)]);
  };

  const handleDownload = () => {
    if (lastGeneratedImage) {
      const link = document.createElement('a');
      link.href = lastGeneratedImage;
      link.download = 'generated-image.jpg';
      link.click();
    }
  };

  const generationJobs = recentJobs.filter(job => job.serviceType === 'generate');

  return (
    <AppLayout 
      title="Image Generation Studio" 
      description="Create stunning images from text descriptions using advanced AI models"
    >
      <div className="p-6 max-w-7xl mx-auto space-y-6">
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Input Panel */}
          <div className="lg:col-span-2 space-y-6">
            
            {/* Prompt Input */}
            <Card className="bg-gray-800/60 border-gray-700">
              <CardHeader>
                <CardTitle className="text-white flex items-center">
                  <Sparkles className="w-5 h-5 mr-2 text-primary-400" />
                  Prompt Input
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Describe your image
                  </label>
                  <Textarea
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    placeholder="A futuristic city skyline at sunset with flying cars and neon lights..."
                    className="bg-gray-700 border-gray-600 text-white placeholder-gray-400 focus:border-primary-500 resize-none"
                    rows={4}
                  />
                </div>
                
                {/* Settings Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">Style</label>
                    <Select 
                      value={parameters.style} 
                      onValueChange={(value) => setParameters({...parameters, style: value})}
                    >
                      <SelectTrigger className="bg-gray-700 border-gray-600 text-white">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent className="bg-gray-700 border-gray-600">
                        <SelectItem value="photorealistic">Photorealistic</SelectItem>
                        <SelectItem value="digital-art">Digital Art</SelectItem>
                        <SelectItem value="oil-painting">Oil Painting</SelectItem>
                        <SelectItem value="anime">Anime/Manga</SelectItem>
                        <SelectItem value="sketch">Sketch</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">Resolution</label>
                    <Select 
                      value={parameters.resolution} 
                      onValueChange={(value) => setParameters({...parameters, resolution: value})}
                    >
                      <SelectTrigger className="bg-gray-700 border-gray-600 text-white">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent className="bg-gray-700 border-gray-600">
                        <SelectItem value="512x512">512x512</SelectItem>
                        <SelectItem value="768x768">768x768</SelectItem>
                        <SelectItem value="1024x1024">1024x1024</SelectItem>
                        <SelectItem value="1024x768">1024x768 (Landscape)</SelectItem>
                        <SelectItem value="768x1024">768x1024 (Portrait)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                {/* Parameter Sliders */}
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between mb-2">
                      <label className="text-sm font-medium text-gray-300">Guidance Scale</label>
                      <span className="text-sm text-gray-400">{parameters.guidanceScale}</span>
                    </div>
                    <Slider
                      value={[parameters.guidanceScale]}
                      onValueChange={([value]) => setParameters({...parameters, guidanceScale: value})}
                      min={1}
                      max={20}
                      step={0.5}
                      className="w-full"
                    />
                  </div>
                  
                  <div>
                    <div className="flex justify-between mb-2">
                      <label className="text-sm font-medium text-gray-300">Steps</label>
                      <span className="text-sm text-gray-400">{parameters.steps}</span>
                    </div>
                    <Slider
                      value={[parameters.steps]}
                      onValueChange={([value]) => setParameters({...parameters, steps: value})}
                      min={1}
                      max={4}
                      step={1}
                      className="w-full"
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
            
            {/* Action Buttons */}
            <div className="flex space-x-4">
              <Button 
                onClick={handleGenerate}
                disabled={!prompt.trim() || generateMutation.isPending}
                className="flex-1 bg-gradient-to-r from-primary-500 to-secondary-500 hover:from-primary-600 hover:to-secondary-600 text-white font-semibold"
              >
                <Sparkles className="w-4 h-4 mr-2" />
                {generateMutation.isPending ? 'Generating...' : 'Generate Image'}
              </Button>
              
              <Button
                variant="outline"
                onClick={handleRandomPrompt}
                className="bg-gray-700 border-gray-600 hover:bg-gray-600"
              >
                <Shuffle className="w-4 h-4" />
              </Button>
              
              <Button
                variant="outline"
                className="bg-gray-700 border-gray-600 hover:bg-gray-600"
              >
                <Save className="w-4 h-4" />
              </Button>
            </div>
          </div>
          
          {/* Results Panel */}
          <div className="space-y-6">
            
            {/* Current Result */}
            {lastGeneratedImage && (
              <Card className="bg-gray-800/60 border-gray-700">
                <CardHeader>
                  <CardTitle className="text-white flex items-center justify-between">
                    <span>Generated Image</span>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={handleDownload}
                      className="text-primary-400 hover:text-primary-300"
                    >
                      <Download className="w-4 h-4" />
                    </Button>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="aspect-square rounded-lg overflow-hidden">
                    <img 
                      src={lastGeneratedImage} 
                      alt="Generated" 
                      className="w-full h-full object-cover"
                    />
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Processing Status */}
            <Card className="bg-gray-800/60 border-gray-700">
              <CardHeader>
                <CardTitle className="text-white flex items-center">
                  <i className="fas fa-chart-line mr-2 text-success"></i>
                  Processing Status
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-400">Status</span>
                    <span className="text-sm font-medium text-white">
                      {generateMutation.isPending ? 'Generating...' : 'Ready'}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-400">Queue</span>
                    <span className="text-sm font-medium text-white">0 pending</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-400">GPU Usage</span>
                    <span className="text-sm font-medium text-white">
                      {generateMutation.isPending ? '85%' : '12%'}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Recent Results */}
            <Card className="bg-gray-800/60 border-gray-700">
              <CardHeader>
                <CardTitle className="text-white flex items-center">
                  <i className="fas fa-images mr-2 text-warning"></i>
                  Recent Results
                </CardTitle>
              </CardHeader>
              <CardContent>
                {generationJobs.length === 0 ? (
                  <div className="text-center text-gray-500 py-4">
                    <p className="text-sm">No generations yet</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {generationJobs.slice(0, 3).map((job) => (
                      <div key={job.id} className="bg-gray-700/50 rounded-lg p-3 hover:bg-gray-700 transition-colors cursor-pointer">
                        <div className="flex items-center space-x-3">
                          {job.result?.url && (
                            <img 
                              src={job.result.url} 
                              alt="Generated" 
                              className="w-12 h-12 rounded-lg object-cover"
                            />
                          )}
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-white truncate">
                              {job.prompt || 'Generated image'}
                            </p>
                            <p className="text-xs text-gray-400">
                              {job.createdAt && new Date(job.createdAt).toLocaleTimeString()}
                            </p>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Button
                              variant="ghost"
                              size="sm"
                              className="h-8 w-8 p-0 hover:bg-gray-600"
                            >
                              <Download className="w-3 h-3" />
                            </Button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Generated Results Gallery */}
        {generationJobs.filter(job => job.status === 'completed' && job.result?.url).length > 0 && (
          <Card className="bg-gray-800/60 border-gray-700">
            <CardHeader>
              <CardTitle className="text-xl text-white flex items-center justify-between">
                <span className="flex items-center">
                  <i className="fas fa-image mr-3 text-primary-500"></i>
                  Generated Results
                </span>
                <div className="flex items-center space-x-3">
                  <Button variant="outline" size="sm" className="bg-gray-700 border-gray-600">
                    <i className="fas fa-th mr-2"></i>
                    Grid
                  </Button>
                </div>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {generationJobs
                  .filter(job => job.status === 'completed' && job.result?.url)
                  .map((job, index) => (
                    <ResultCard 
                      key={job.id} 
                      job={job} 
                      featured={index === 0}
                    />
                  ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </AppLayout>
  );
}
