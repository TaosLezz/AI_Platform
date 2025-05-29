import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useAIStore } from '@/store/ai-store';
import { generateImage, classifyImage, detectObjects, segmentImage, sendChatMessage, getChatHistory, getRecentJobs } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';

export function useImageGeneration() {
  const { setProcessingStatus, addJob, setLastGeneratedImage } = useAIStore();
  const { toast } = useToast();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ prompt, parameters }: { prompt: string; parameters: any }) => {
      setProcessingStatus({ 
        isProcessing: true, 
        message: "Generating image...",
        currentStep: 1,
        totalSteps: 50,
        estimatedTime: 30000
      });
      return generateImage(prompt, parameters);
    },
    onSuccess: (data) => {
      setProcessingStatus({ isProcessing: false });
      setLastGeneratedImage(data.url);
      addJob({
        id: data.jobId,
        serviceType: 'generate',
        status: 'completed',
        result: data,
        createdAt: new Date(),
        processingTime: data.processingTime
      });
      toast({
        title: "Image Generated Successfully",
        description: "Your image has been created and is ready for download.",
      });
      queryClient.invalidateQueries({ queryKey: ['/api/v1/jobs'] });
    },
    onError: (error: Error) => {
      setProcessingStatus({ isProcessing: false });
      toast({
        title: "Generation Failed",
        description: error.message,
        variant: "destructive",
      });
    },
  });
}

export function useImageClassification() {
  const { setProcessingStatus, addJob } = useAIStore();
  const { toast } = useToast();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ file, useHuggingFace }: { file: File; useHuggingFace?: boolean }) => {
      setProcessingStatus({ 
        isProcessing: true, 
        message: "Classifying image...",
        estimatedTime: 2000
      });
      return classifyImage(file, useHuggingFace);
    },
    onSuccess: (data) => {
      setProcessingStatus({ isProcessing: false });
      addJob({
        id: data.jobId,
        serviceType: 'classify',
        status: 'completed',
        result: data,
        createdAt: new Date(),
        processingTime: data.processingTime
      });
      toast({
        title: "Classification Complete",
        description: `Identified as: ${data.class} (${Math.round(data.confidence * 100)}% confidence)`,
      });
      queryClient.invalidateQueries({ queryKey: ['/api/v1/jobs'] });
    },
    onError: (error: Error) => {
      setProcessingStatus({ isProcessing: false });
      toast({
        title: "Classification Failed",
        description: error.message,
        variant: "destructive",
      });
    },
  });
}

export function useObjectDetection() {
  const { setProcessingStatus, addJob } = useAIStore();
  const { toast } = useToast();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ file, useHuggingFace }: { file: File; useHuggingFace?: boolean }) => {
      setProcessingStatus({ 
        isProcessing: true, 
        message: "Detecting objects...",
        estimatedTime: 5000
      });
      return detectObjects(file, useHuggingFace);
    },
    onSuccess: (data) => {
      setProcessingStatus({ isProcessing: false });
      addJob({
        id: data.jobId,
        serviceType: 'detect',
        status: 'completed',
        result: data,
        createdAt: new Date(),
        processingTime: data.processingTime
      });
      toast({
        title: "Detection Complete",
        description: `Found ${data.objects?.length || 0} objects in the image.`,
      });
      queryClient.invalidateQueries({ queryKey: ['/api/v1/jobs'] });
    },
    onError: (error: Error) => {
      setProcessingStatus({ isProcessing: false });
      toast({
        title: "Detection Failed",
        description: error.message,
        variant: "destructive",
      });
    },
  });
}

export function useImageSegmentation() {
  const { setProcessingStatus, addJob } = useAIStore();
  const { toast } = useToast();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ file, useHuggingFace }: { file: File; useHuggingFace?: boolean }) => {
      setProcessingStatus({ 
        isProcessing: true, 
        message: "Segmenting image...",
        estimatedTime: 8000
      });
      return segmentImage(file, useHuggingFace);
    },
    onSuccess: (data) => {
      setProcessingStatus({ isProcessing: false });
      addJob({
        id: data.jobId,
        serviceType: 'segment',
        status: 'completed',
        result: data,
        createdAt: new Date(),
        processingTime: data.processingTime
      });
      toast({
        title: "Segmentation Complete",
        description: `Image segmented into ${data.segments?.length || 0} regions.`,
      });
      queryClient.invalidateQueries({ queryKey: ['/api/v1/jobs'] });
    },
    onError: (error: Error) => {
      setProcessingStatus({ isProcessing: false });
      toast({
        title: "Segmentation Failed",
        description: error.message,
        variant: "destructive",
      });
    },
  });
}

export function useChatCompletion() {
  const { addChatMessage } = useAIStore();
  const { toast } = useToast();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (message: string) => {
      // Add user message immediately
      addChatMessage({
        id: Date.now(),
        role: 'user',
        content: message,
        timestamp: new Date(),
      });
      return sendChatMessage(message);
    },
    onSuccess: (data) => {
      // Add assistant response
      addChatMessage({
        id: Date.now() + 1,
        role: 'assistant',
        content: data.response,
        timestamp: new Date(),
      });
      queryClient.invalidateQueries({ queryKey: ['/api/v1/chat/history'] });
    },
    onError: (error: Error) => {
      toast({
        title: "Chat Error",
        description: error.message,
        variant: "destructive",
      });
    },
  });
}

export function useChatHistory() {
  const { setChatMessages } = useAIStore();

  return useQuery({
    queryKey: ['/api/v1/chat/history'],
    queryFn: async () => {
      const data = await getChatHistory();
      setChatMessages(data.messages);
      return data.messages;
    },
  });
}

export function useRecentJobs() {
  const { setRecentJobs } = useAIStore();

  return useQuery({
    queryKey: ['/api/v1/jobs'],
    queryFn: async () => {
      const data = await getRecentJobs();
      setRecentJobs(data.jobs);
      return data.jobs;
    },
    refetchInterval: 5000, // Refresh every 5 seconds
  });
}
