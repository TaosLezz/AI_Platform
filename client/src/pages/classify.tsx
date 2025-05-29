import { useState } from 'react';
import { AppLayout } from '@/components/layout/app-layout';
import { FileUpload } from '@/components/ui/file-upload';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Progress } from '@/components/ui/progress';
import { Eye, Brain, FileImage, CheckCircle } from 'lucide-react';
import { useImageClassification } from '@/hooks/use-ai-service';
import { useAIStore } from '@/store/ai-store';
import { ClassificationResult } from '@/lib/types';

export default function ClassifyPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [useHuggingFace, setUseHuggingFace] = useState(false);
  const [result, setResult] = useState<ClassificationResult | null>(null);
  const [preview, setPreview] = useState<string | null>(null);

  const classifyMutation = useImageClassification();
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

  const handleClassify = () => {
    if (!selectedFile) return;
    
    classifyMutation.mutate(
      { file: selectedFile, useHuggingFace },
      {
        onSuccess: (data) => {
          setResult(data);
        }
      }
    );
  };

  const classificationJobs = recentJobs.filter(job => job.serviceType === 'classify');

  return (
    <AppLayout 
      title="Image Classification" 
      description="Identify and categorize objects in images with confidence scores"
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
                  disabled={classifyMutation.isPending}
                />
              </CardContent>
            </Card>

            {/* Model Settings */}
            <Card className="bg-gray-800/60 border-gray-700">
              <CardHeader>
                <CardTitle className="text-white flex items-center">
                  <Brain className="w-5 h-5 mr-2 text-secondary-400" />
                  Model Settings
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <label className="text-sm font-medium text-white">Use Hugging Face Models</label>
                    <p className="text-xs text-gray-400">Switch between OpenAI Vision and Hugging Face models</p>
                  </div>
                  <Switch
                    checked={useHuggingFace}
                    onCheckedChange={setUseHuggingFace}
                    disabled={classifyMutation.isPending}
                  />
                </div>
                
                <div className="text-xs text-gray-500 p-3 bg-gray-700/50 rounded-lg">
                  <strong>Current Model:</strong> {useHuggingFace ? 'Hugging Face ResNet/EfficientNet' : 'OpenAI GPT-4o Vision'}
                </div>
              </CardContent>
            </Card>

            {/* Action Button */}
            <div className="flex justify-center">
              <Button 
                onClick={handleClassify}
                disabled={!selectedFile || classifyMutation.isPending}
                className="w-full bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 text-white font-semibold py-3"
              >
                <Eye className="w-5 h-5 mr-2" />
                {classifyMutation.isPending ? 'Classifying...' : 'Classify Image'}
              </Button>
            </div>

            {/* Image Preview */}
            {preview && (
              <Card className="bg-gray-800/60 border-gray-700">
                <CardHeader>
                  <CardTitle className="text-white">Image Preview</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="aspect-video bg-gray-700 rounded-lg overflow-hidden">
                    <img 
                      src={preview} 
                      alt="Preview" 
                      className="w-full h-full object-contain"
                    />
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
          
          {/* Results Panel */}
          <div className="space-y-6">
            
            {/* Classification Result */}
            {result && (
              <Card className="bg-gray-800/60 border-gray-700">
                <CardHeader>
                  <CardTitle className="text-white flex items-center">
                    <CheckCircle className="w-5 h-5 mr-2 text-green-400" />
                    Classification Result
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="text-center">
                    <h3 className="text-2xl font-bold text-white mb-2">{result.class}</h3>
                    <div className="flex items-center justify-center space-x-2 mb-4">
                      <span className="text-sm text-gray-400">Confidence:</span>
                      <Badge variant="secondary" className="bg-green-500/20 text-green-400">
                        {Math.round(result.confidence * 100)}%
                      </Badge>
                    </div>
                    <Progress 
                      value={result.confidence * 100} 
                      className="w-full h-2 mb-4"
                    />
                  </div>
                  
                  <div className="bg-gray-700/50 rounded-lg p-3">
                    <p className="text-sm text-gray-300">{result.description}</p>
                  </div>

                  {result.alternatives && result.alternatives.length > 0 && (
                    <div>
                      <h4 className="text-sm font-medium text-white mb-2">Alternative Classifications:</h4>
                      <div className="space-y-2">
                        {result.alternatives.map((alt, index) => (
                          <div key={index} className="flex items-center justify-between text-sm">
                            <span className="text-gray-300">{alt.label}</span>
                            <Badge variant="outline" className="text-xs">
                              {Math.round(alt.score * 100)}%
                            </Badge>
                          </div>
                        ))}
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
                      {classifyMutation.isPending ? 'Processing...' : 'Ready'}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-400">Model</span>
                    <span className="text-sm font-medium text-white">
                      {useHuggingFace ? 'Hugging Face' : 'OpenAI Vision'}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-400">Avg Time</span>
                    <span className="text-sm font-medium text-white">~2s</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Recent Classifications */}
            <Card className="bg-gray-800/60 border-gray-700">
              <CardHeader>
                <CardTitle className="text-white flex items-center">
                  <i className="fas fa-history mr-2 text-warning"></i>
                  Recent Classifications
                </CardTitle>
              </CardHeader>
              <CardContent>
                {classificationJobs.length === 0 ? (
                  <div className="text-center text-gray-500 py-4">
                    <p className="text-sm">No classifications yet</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {classificationJobs.slice(0, 5).map((job) => (
                      <div key={job.id} className="bg-gray-700/50 rounded-lg p-3">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-medium text-white">
                            {job.result?.class || 'Processing...'}
                          </span>
                          {job.result?.confidence && (
                            <Badge variant="secondary" className="text-xs">
                              {Math.round(job.result.confidence * 100)}%
                            </Badge>
                          )}
                        </div>
                        <p className="text-xs text-gray-400">
                          {job.createdAt && new Date(job.createdAt).toLocaleTimeString()}
                        </p>
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
