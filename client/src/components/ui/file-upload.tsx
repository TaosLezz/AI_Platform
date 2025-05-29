import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, X, FileImage } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  acceptedTypes?: string[];
  maxSize?: number;
  className?: string;
  disabled?: boolean;
}

export function FileUpload({ 
  onFileSelect, 
  acceptedTypes = ['image/*'], 
  maxSize = 10 * 1024 * 1024, // 10MB
  className,
  disabled = false 
}: FileUploadProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      setSelectedFile(file);
      onFileSelect(file);
      
      // Create preview for images
      if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = (e) => {
          setPreview(e.target?.result as string);
        };
        reader.readAsDataURL(file);
      }
    }
  }, [onFileSelect]);

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: acceptedTypes.reduce((acc, type) => ({ ...acc, [type]: [] }), {}),
    maxSize,
    multiple: false,
    disabled,
  });

  const clearFile = () => {
    setSelectedFile(null);
    setPreview(null);
  };

  return (
    <div className={cn("w-full", className)}>
      {!selectedFile ? (
        <div
          {...getRootProps()}
          className={cn(
            "border-2 border-dashed rounded-lg p-8 text-center transition-all duration-200 cursor-pointer",
            "border-gray-600 hover:border-primary-500 bg-dark-800/50 hover:bg-primary-500/10",
            isDragActive && "border-primary-500 bg-primary-500/20",
            isDragReject && "border-red-500 bg-red-500/10",
            disabled && "opacity-50 cursor-not-allowed"
          )}
        >
          <input {...getInputProps()} />
          <div className="flex flex-col items-center space-y-4">
            <Upload className="w-12 h-12 text-gray-400" />
            <div>
              <p className="text-white font-medium mb-2">
                {isDragActive ? "Drop your files here" : "Drag & drop your files here"}
              </p>
              <p className="text-gray-400 text-sm mb-4">or click to browse files</p>
              <Button 
                type="button"
                variant="outline"
                size="sm"
                disabled={disabled}
                className="bg-dark-800 border-gray-600 hover:bg-gray-700"
              >
                Browse Files
              </Button>
            </div>
            <p className="text-xs text-gray-500">
              Supports: {acceptedTypes.join(', ')} (Max {Math.round(maxSize / 1024 / 1024)}MB)
            </p>
          </div>
        </div>
      ) : (
        <div className="bg-dark-800 rounded-lg p-4">
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-sm font-medium text-white">Selected File</h4>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={clearFile}
              className="h-8 w-8 p-0 hover:bg-gray-700"
            >
              <X className="w-4 h-4" />
            </Button>
          </div>
          
          <div className="flex items-center space-x-3">
            {preview ? (
              <img 
                src={preview} 
                alt="Preview" 
                className="w-16 h-16 rounded-lg object-cover"
              />
            ) : (
              <div className="w-16 h-16 bg-gray-700 rounded-lg flex items-center justify-center">
                <FileImage className="w-8 h-8 text-gray-400" />
              </div>
            )}
            
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-white truncate">
                {selectedFile.name}
              </p>
              <p className="text-xs text-gray-400">
                {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
