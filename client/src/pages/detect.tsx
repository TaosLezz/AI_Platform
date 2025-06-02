import { useState } from 'react';
import { AppLayout } from '@/components/layout/app-layout';
import { FileUpload } from '@/components/ui/file-upload';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Target, Brain, FileImage, CheckCircle, Square } from 'lucide-react';
import { useObjectDetection } from '@/hooks/use-ai-service';
import { useAIStore } from '@/store/ai-store';
import { DetectionResult } from '@/lib/types';

export default function DetectPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [useHuggingFace, setUseHuggingFace] = useState(false);
  const [result, setResult] = useState<DetectionResult | null>(null);
  const [preview, setPreview] = useState<string | null>(null);

  const detectMutation = useObjectDetection();
  const { recentJobs } = useAIStore();

  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
    setResult(null);
    
    // Create preview
    const reader = new FileReader();
    reader.onload = (e) => {
      setPreview(e.target?.result as string);
    };
    reader.readAsDataURL(file);
  };

  const handleDetect = () => {
    if (!selectedFile) return;
    
    detectMutation.mutate(
      { file: selectedFile, useHuggingFace },
      {
        onSuccess: (data) => {
          setResult(data);
        }
      }
    );
  };

  const detectionJobs = recentJobs.filter(job => job.serviceType === 'detect');

  const renderBoundingBoxes = () => {
    if (!result || !result.objects || result.objects.length === 0) return null;
    return (
      <div className="absolute inset-0">
        {result.objects.map((obj, index) => {
          const colors = [
            'border-green-400 bg-green-400/10',
            'border-blue-400 bg-blue-400/10',
            'border-yellow-400 bg-yellow-400/10',
            'border-red-400 bg-red-400/10',
            'border-purple-400 bg-purple-400/10'
          ];
          const colorClass = colors[index % colors.length];
          
          // Convert percentage-based bbox to pixel coordinates
          const [x, y, width, height] = obj.bbox;
          
          return (
            <div
              key={index}
              className={`absolute border-2 ${colorClass} rounded`}
              style={{
                left: `${x}%`,
                top: `${y}%`,
                width: `${width}%`,
                height: `${height}%`
              }}
            >
              <div className="absolute -top-6 left-0">
                <Badge variant="secondary" className={`text-xs ${colorClass.replace('bg-', 'bg-').replace('/10', '')} border-0`}>
                  {obj.name} ({Math.round(obj.confidence * 100)}%)
                </Badge>
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <AppLayout 
      title="Object Detection" 
      description="Locate and identify multiple objects with bounding boxes and confidence scores"
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
                  disabled={detectMutation.isPending}
                />
              </CardContent>
            </Card>

            {/* Model Settings */}
            <Card className="bg-gray-800/60 border-gray-700">
              <CardHeader>
                <CardTitle className="text-white flex items-center">
                  <Brain className="w-5 h-5 mr-2 text-secondary-400" />
                  Detection Settings
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <label className="text-sm font-medium text-white">Use Hugging Face Models</label>
                    <p className="text-xs text-gray-400">Switch between OpenAI Vision and YOLO/DETR models</p>
                  </div>
                  <Switch
                    checked={useHuggingFace}
                    onCheckedChange={setUseHuggingFace}
                    disabled={detectMutation.isPending}
                  />
                </div>
                
                <div className="text-xs text-gray-500 p-3 bg-gray-700/50 rounded-lg">
                  <strong>Current Model:</strong> {useHuggingFace ? 'Hugging Face YOLO v8/DETR' : 'OpenAI GPT-4o Vision'}
                </div>

                <div className="grid grid-cols-2 gap-4 text-xs text-gray-400">
                  <div>
                    <span className="font-medium">Confidence Threshold:</span>
                    <p>≥ 50%</p>
                  </div>
                  <div>
                    <span className="font-medium">Max Objects:</span>
                    <p>20 per image</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Action Button */}
            <div className="flex justify-center">
              <Button 
                onClick={handleDetect}
                disabled={!selectedFile || detectMutation.isPending}
                className="w-full bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-white font-semibold py-3"
              >
                <Target className="w-5 h-5 mr-2" />
                {detectMutation.isPending ? 'Detecting Objects...' : 'Detect Objects'}
              </Button>
            </div>

            {/* Image Preview with Detection Results */}
            {preview && (
              <Card className="bg-gray-800/60 border-gray-700">
                <CardHeader>
                  <CardTitle className="text-white flex items-center justify-between">
                    <span>Detection Results</span>
                    {result && result.objects && (
                      <Badge variant="secondary" className="bg-green-500/20 text-green-400">
                        {result.objects.length} objects found
                      </Badge>
                    )}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="aspect-video bg-gray-700 rounded-lg overflow-hidden relative">
                    <img 
                      src={preview} 
                      alt="Preview" 
                      className="w-full h-full object-contain"
                    />
                    {renderBoundingBoxes()}
                  </div>
                  
                  {result && result.objects && result.objects.length > 0 && (
                    <div className="mt-4 space-y-2">
                      <h4 className="text-sm font-medium text-white">Detected Objects:</h4>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                        {result.objects.map((obj, index) => (
                          <div key={index} className="flex items-center justify-between bg-gray-700/50 rounded-lg p-2">
                            <div className="flex items-center space-x-2">
                              <Square className="w-3 h-3 text-green-400" />
                              <span className="text-sm text-white">{obj.name}</span>
                            </div>
                            <Badge variant="outline" className="text-xs">
                              {Math.round(obj.confidence * 100)}%
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
            
            {/* Detection Summary */}
            {result && (
              <Card className="bg-gray-800/60 border-gray-700">
                <CardHeader>
                  <CardTitle className="text-white flex items-center">
                    <CheckCircle className="w-5 h-5 mr-2 text-green-400" />
                    Detection Summary
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="text-center">
                    <h3 className="text-2xl font-bold text-white mb-2">
                      {result.objects?.length || 0}
                    </h3>
                    <p className="text-sm text-gray-400 mb-4">Objects Detected</p>
                  </div>
                  
                  {result.objects && result.objects.length > 0 && (
                    <div className="space-y-2">
                      <h4 className="text-sm font-medium text-white">Object Types:</h4>
                      {[...new Set(result.objects.map(obj => obj.name))].map((type, index) => {
                        const count = result.objects.filter(obj => obj.name === type).length;
                        const avgConfidence = result.objects
                          .filter(obj => obj.name === type)
                          .reduce((sum, obj) => sum + obj.confidence, 0) / count;
                        
                        return (
                          <div key={index} className="flex items-center justify-between text-sm">
                            <span className="text-gray-300">{type} ({count})</span>
                            <Badge variant="outline" className="text-xs">
                              {Math.round(avgConfidence * 100)}%
                            </Badge>
                          </div>
                        );
                      })}
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
                      {detectMutation.isPending ? 'Processing...' : 'Ready'}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-400">Model</span>
                    <span className="text-sm font-medium text-white">
                      {useHuggingFace ? 'YOLO v8' : 'OpenAI Vision'}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-400">Avg Time</span>
                    <span className="text-sm font-medium text-white">~5s</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Recent Detections */}
            <Card className="bg-gray-800/60 border-gray-700">
              <CardHeader>
                <CardTitle className="text-white flex items-center">
                  <i className="fas fa-history mr-2 text-warning"></i>
                  Recent Detections
                </CardTitle>
              </CardHeader>
              <CardContent>
                {detectionJobs.length === 0 ? (
                  <div className="text-center text-gray-500 py-4">
                    <p className="text-sm">No detections yet</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {detectionJobs.slice(0, 5).map((job) => (
                      <div key={job.id} className="bg-gray-700/50 rounded-lg p-3">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-medium text-white">
                            {job.result?.objects?.length || 0} objects detected
                          </span>
                          <Badge variant="secondary" className="text-xs">
                            {job.status}
                          </Badge>
                        </div>
                        <p className="text-xs text-gray-400">
                          {job.createdAt && new Date(job.createdAt).toLocaleTimeString()}
                        </p>
                        {job.result?.objects && job.result.objects.length > 0 && (
                          <div className="mt-2">
                            <p className="text-xs text-gray-500">
                              Found: {[...new Set(job.result.objects.map((obj: { name: string }) => obj.name))].join(', ')}
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
