import { useState } from 'react';
import { AppLayout } from '@/components/layout/app-layout';
import { FileUpload } from '@/components/ui/file-upload';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Scissors, Brain, FileImage, CheckCircle, Layers, MousePointer } from 'lucide-react';
import { useImageSegmentation } from '@/hooks/use-ai-service';
import { useAIStore } from '@/store/ai-store';
import { SegmentationResult } from '@/lib/types';

export default function SegmentPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [useHuggingFace, setUseHuggingFace] = useState(false);
  const [result, setResult] = useState<SegmentationResult | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [selectedSegment, setSelectedSegment] = useState<number | null>(null);

  const segmentMutation = useImageSegmentation();
  const { recentJobs } = useAIStore();

  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
    setResult(null);
    setSelectedSegment(null);
    
    // Create preview
    const reader = new FileReader();
    reader.onload = (e) => {
      setPreview(e.target?.result as string);
    };
    reader.readAsDataURL(file);
  };

  const handleSegment = () => {
    if (!selectedFile) return;
    
    segmentMutation.mutate(
      { file: selectedFile, useHuggingFace },
      {
        onSuccess: (data) => {
          setResult(data);
        }
      }
    );
  };

  const segmentationJobs = recentJobs.filter(job => job.serviceType === 'segment');

  const getSegmentColor = (index: number) => {
    const colors = [
      'bg-red-400/30 border-red-400',
      'bg-blue-400/30 border-blue-400',
      'bg-green-400/30 border-green-400',
      'bg-yellow-400/30 border-yellow-400',
      'bg-purple-400/30 border-purple-400',
      'bg-pink-400/30 border-pink-400',
      'bg-cyan-400/30 border-cyan-400',
      'bg-orange-400/30 border-orange-400'
    ];
    return colors[index % colors.length];
  };

  return (
    <AppLayout 
      title="Image Segmentation" 
      description="Precise pixel-level object segmentation and masking with interactive controls"
    >
      <div className="p-6 max-w-7xl mx-auto space-y-6">
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Input Panel */}
          <div className="lg:col-span-2 space-y-6">
            
            {/* File Upload */}
            <Card className="bg-gray-800/60 border-gray-700">
              <CardHeader>
                <CardTitle className="text-white flex items-center">
                  <FileImage className="w-5 h-5 mr-2 text-primary-400" />
                  Upload Image
                </CardTitle>
              </CardHeader>
              <CardContent>
                <FileUpload 
                  onFileSelect={handleFileSelect}
                  acceptedTypes={['image/*']}
                  disabled={segmentMutation.isPending}
                />
              </CardContent>
            </Card>

            {/* Model Settings */}
            <Card className="bg-gray-800/60 border-gray-700">
              <CardHeader>
                <CardTitle className="text-white flex items-center">
                  <Brain className="w-5 h-5 mr-2 text-secondary-400" />
                  Segmentation Settings
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <label className="text-sm font-medium text-white">Use Hugging Face Models</label>
                    <p className="text-xs text-gray-400">Switch between OpenAI Vision and SAM/DeepLab models</p>
                  </div>
                  <Switch
                    checked={useHuggingFace}
                    onCheckedChange={setUseHuggingFace}
                    disabled={segmentMutation.isPending}
                  />
                </div>
                
                <div className="text-xs text-gray-500 p-3 bg-gray-700/50 rounded-lg">
                  <strong>Current Model:</strong> {useHuggingFace ? 'Hugging Face SAM/U-Net' : 'OpenAI GPT-4o Vision'}
                </div>

                <div className="grid grid-cols-2 gap-4 text-xs text-gray-400">
                  <div>
                    <span className="font-medium">Segmentation Type:</span>
                    <p>Semantic + Instance</p>
                  </div>
                  <div>
                    <span className="font-medium">Min Segment Size:</span>
                    <p>100 pixels</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Action Button */}
            <div className="flex justify-center">
              <Button 
                onClick={handleSegment}
                disabled={!selectedFile || segmentMutation.isPending}
                className="w-full bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600 text-white font-semibold py-3"
              >
                <Scissors className="w-5 h-5 mr-2" />
                {segmentMutation.isPending ? 'Segmenting Image...' : 'Segment Image'}
              </Button>
            </div>

            {/* Image Preview with Segmentation Results */}
            {preview && (
              <Card className="bg-gray-800/60 border-gray-700">
                <CardHeader>
                  <CardTitle className="text-white flex items-center justify-between">
                    <span>Segmentation Results</span>
                    {result && result.segments && (
                      <Badge variant="secondary" className="bg-orange-500/20 text-orange-400">
                        {result.segments.length} segments found
                      </Badge>
                    )}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <Tabs defaultValue="original" className="w-full">
                    <TabsList className="grid w-full grid-cols-3 bg-gray-700">
                      <TabsTrigger value="original" className="data-[state=active]:bg-gray-600">
                        Original
                      </TabsTrigger>
                      <TabsTrigger value="segmented" className="data-[state=active]:bg-gray-600">
                        Segmented
                      </TabsTrigger>
                      <TabsTrigger value="overlay" className="data-[state=active]:bg-gray-600">
                        Overlay
                      </TabsTrigger>
                    </TabsList>
                    
                    <TabsContent value="original" className="mt-4">
                      <div className="aspect-video bg-gray-700 rounded-lg overflow-hidden">
                        <img 
                          src={preview} 
                          alt="Original" 
                          className="w-full h-full object-contain"
                        />
                      </div>
                    </TabsContent>
                    
                    <TabsContent value="segmented" className="mt-4">
                      <div className="aspect-video bg-gray-700 rounded-lg overflow-hidden relative">
                        <img 
                          src={preview} 
                          alt="Segmented" 
                          className="w-full h-full object-contain"
                        />
                        {result && result.segments && result.segments.map((segment, index) => (
                          <div
                            key={index}
                            className={`absolute inset-0 cursor-pointer transition-opacity ${
                              selectedSegment === index ? 'opacity-70' : 'opacity-30 hover:opacity-50'
                            } ${getSegmentColor(index)}`}
                            onClick={() => setSelectedSegment(selectedSegment === index ? null : index)}
                            style={{
                              clipPath: segment.mask || 'none'
                            }}
                          >
                            <div className="absolute top-2 left-2">
                              <Badge variant="secondary" className="text-xs bg-gray-900/80 text-white">
                                {segment.name}
                              </Badge>
                            </div>
                          </div>
                        ))}
                      </div>
                    </TabsContent>
                    
                    <TabsContent value="overlay" className="mt-4">
                      <div className="aspect-video bg-gray-700 rounded-lg overflow-hidden relative">
                        <img 
                          src={preview} 
                          alt="Overlay" 
                          className="w-full h-full object-contain opacity-60"
                        />
                        {result && result.segments && result.segments.map((segment, index) => (
                          <div
                            key={index}
                            className={`absolute inset-0 border-2 cursor-pointer transition-all ${
                              selectedSegment === index ? 'opacity-80' : 'opacity-40 hover:opacity-60'
                            } ${getSegmentColor(index)}`}
                            onClick={() => setSelectedSegment(selectedSegment === index ? null : index)}
                          >
                            <div className="absolute top-2 left-2">
                              <Badge variant="secondary" className="text-xs bg-gray-900/80 text-white">
                                {segment.name} ({Math.round(segment.confidence * 100)}%)
                              </Badge>
                            </div>
                          </div>
                        ))}
                      </div>
                    </TabsContent>
                  </Tabs>

                  {result && result.segments && result.segments.length > 0 && (
                    <div className="mt-4 space-y-2">
                      <div className="flex items-center space-x-2 text-sm text-gray-400">
                        <MousePointer className="w-4 h-4" />
                        <span>Click on segments to highlight them</span>
                      </div>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                        {result.segments.map((segment, index) => (
                          <div 
                            key={index} 
                            className={`flex items-center justify-between rounded-lg p-2 cursor-pointer transition-all ${
                              selectedSegment === index 
                                ? 'bg-gray-600 border border-gray-500' 
                                : 'bg-gray-700/50 hover:bg-gray-700'
                            }`}
                            onClick={() => setSelectedSegment(selectedSegment === index ? null : index)}
                          >
                            <div className="flex items-center space-x-2">
                              <div className={`w-3 h-3 rounded border-2 ${getSegmentColor(index)}`}></div>
                              <span className="text-sm text-white">{segment.name}</span>
                            </div>
                            <Badge variant="outline" className="text-xs">
                              {Math.round(segment.confidence * 100)}%
                            </Badge>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}
          </div>
          
          {/* Results Panel */}
          <div className="space-y-6">
            
            {/* Segmentation Summary */}
            {result && (
              <Card className="bg-gray-800/60 border-gray-700">
                <CardHeader>
                  <CardTitle className="text-white flex items-center">
                    <CheckCircle className="w-5 h-5 mr-2 text-green-400" />
                    Segmentation Summary
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="text-center">
                    <h3 className="text-2xl font-bold text-white mb-2">
                      {result.segments?.length || 0}
                    </h3>
                    <p className="text-sm text-gray-400 mb-4">Segments Identified</p>
                  </div>
                  
                  {result.segments && result.segments.length > 0 && (
                    <div className="space-y-2">
                      <h4 className="text-sm font-medium text-white">Segment Details:</h4>
                      {result.segments.map((segment, index) => (
                        <div 
                          key={index} 
                          className={`flex items-center justify-between text-sm p-2 rounded transition-colors ${
                            selectedSegment === index ? 'bg-gray-600' : 'hover:bg-gray-700/50'
                          }`}
                        >
                          <div className="flex items-center space-x-2">
                            <div className={`w-3 h-3 rounded ${getSegmentColor(index)}`}></div>
                            <span className="text-gray-300">{segment.name}</span>
                          </div>
                          <Badge variant="outline" className="text-xs">
                            {Math.round(segment.confidence * 100)}%
                          </Badge>
                        </div>
                      ))}
                    </div>
                  )}

                  {selectedSegment !== null && result.segments && result.segments[selectedSegment] && (
                    <div className="border-t border-gray-600 pt-3">
                      <h4 className="text-sm font-medium text-white mb-2">Selected Segment:</h4>
                      <div className="bg-gray-700/50 rounded-lg p-3">
                        <p className="text-sm text-white font-medium">
                          {result.segments[selectedSegment].name}
                        </p>
                        <p className="text-xs text-gray-400 mt-1">
                          Confidence: {Math.round(result.segments[selectedSegment].confidence * 100)}%
                        </p>
                      </div>
                    </div>
                  )}
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
                      {segmentMutation.isPending ? 'Processing...' : 'Ready'}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-400">Model</span>
                    <span className="text-sm font-medium text-white">
                      {useHuggingFace ? 'SAM/U-Net' : 'OpenAI Vision'}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-400">Avg Time</span>
                    <span className="text-sm font-medium text-white">~8s</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <Card className="bg-gray-800/60 border-gray-700">
              <CardHeader>
                <CardTitle className="text-white flex items-center">
                  <Layers className="w-5 h-5 mr-2 text-warning" />
                  Quick Actions
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <Button 
                    variant="ghost" 
                    className="w-full justify-start text-left hover:bg-gray-700/50"
                    disabled={!result}
                  >
                    <i className="fas fa-download mr-2 text-gray-400"></i>
                    <span className="text-sm">Export Masks</span>
                  </Button>
                  <Button 
                    variant="ghost" 
                    className="w-full justify-start text-left hover:bg-gray-700/50"
                    disabled={!result}
                  >
                    <i className="fas fa-eye mr-2 text-gray-400"></i>
                    <span className="text-sm">View in Detail</span>
                  </Button>
                  <Button 
                    variant="ghost" 
                    className="w-full justify-start text-left hover:bg-gray-700/50"
                    disabled={!result}
                  >
                    <i className="fas fa-edit mr-2 text-gray-400"></i>
                    <span className="text-sm">Refine Segments</span>
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Recent Segmentations */}
            <Card className="bg-gray-800/60 border-gray-700">
              <CardHeader>
                <CardTitle className="text-white flex items-center">
                  <i className="fas fa-history mr-2 text-warning"></i>
                  Recent Segmentations
                </CardTitle>
              </CardHeader>
              <CardContent>
                {segmentationJobs.length === 0 ? (
                  <div className="text-center text-gray-500 py-4">
                    <p className="text-sm">No segmentations yet</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {segmentationJobs.slice(0, 5).map((job) => (
                      <div key={job.id} className="bg-gray-700/50 rounded-lg p-3">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-medium text-white">
                            {job.result?.segments?.length || 0} segments found
                          </span>
                          <Badge variant="secondary" className="text-xs">
                            {job.status}
                          </Badge>
                        </div>
                        <p className="text-xs text-gray-400">
                          {job.createdAt && new Date(job.createdAt).toLocaleTimeString()}
                        </p>
                        {job.result?.segments && job.result.segments.length > 0 && (
                          <div className="mt-2">
                            <p className="text-xs text-gray-500">
                              Segments: {job.result.segments.map(s => s.name).join(', ')}
                            </p>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
