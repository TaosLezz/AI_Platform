import { create } from 'zustand';
import { AIJob, ChatMessage, ProcessingStatus } from '@/lib/types';

interface AIStore {
  // Processing state
  processingStatus: ProcessingStatus;
  setProcessingStatus: (status: ProcessingStatus) => void;
  
  // Recent jobs
  recentJobs: AIJob[];
  setRecentJobs: (jobs: AIJob[]) => void;
  addJob: (job: AIJob) => void;
  updateJob: (id: number, updates: Partial<AIJob>) => void;
  
  // Chat state
  chatMessages: ChatMessage[];
  setChatMessages: (messages: ChatMessage[]) => void;
  addChatMessage: (message: ChatMessage) => void;
  
  // UI state
  currentService: string;
  setCurrentService: (service: string) => void;
  
  // Results
  lastGeneratedImage: string | null;
  setLastGeneratedImage: (url: string | null) => void;
}

export const useAIStore = create<AIStore>((set, get) => ({
  // Processing state
  processingStatus: { isProcessing: false },
  setProcessingStatus: (status) => set({ processingStatus: status }),
  
  // Recent jobs
  recentJobs: [],
  setRecentJobs: (jobs) => set({ recentJobs: jobs }),
  addJob: (job) => set((state) => ({ 
    recentJobs: [job, ...state.recentJobs].slice(0, 20) 
  })),
  updateJob: (id, updates) => set((state) => ({
    recentJobs: state.recentJobs.map(job => 
      job.id === id ? { ...job, ...updates } : job
    )
  })),
  
  // Chat state
  chatMessages: [],
  setChatMessages: (messages) => set({ chatMessages: messages }),
  addChatMessage: (message) => set((state) => ({
    chatMessages: [...state.chatMessages, message]
  })),
  
  // UI state
  currentService: 'generate',
  setCurrentService: (service) => set({ currentService: service }),
  
  // Results
  lastGeneratedImage: null,
  setLastGeneratedImage: (url) => set({ lastGeneratedImage: url }),
}));
