import { useState, useRef, useEffect } from 'react';
import { AppLayout } from '@/components/layout/app-layout';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { MessageCircle, Send, Bot, User, Sparkles, Clock, Zap } from 'lucide-react';
import { useChatCompletion, useChatHistory } from '@/hooks/use-ai-service';
import { useAIStore } from '@/store/ai-store';
import { cn } from '@/lib/utils';

const SUGGESTED_PROMPTS = [
  "How does image generation work?",
  "Explain object detection algorithms",
  "What's the difference between classification and segmentation?",
  "How can I improve my AI model results?",
  "Tell me about the latest AI techniques",
  "What are the best practices for AI training?"
];

export default function ChatPage() {
  const [message, setMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const chatMutation = useChatCompletion();
  const { chatMessages } = useAIStore();
  useChatHistory(); // Load chat history

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatMessages]);

  const handleSendMessage = () => {
    if (!message.trim() || chatMutation.isPending) return;

    const userMessage = message;
    setMessage('');
    setIsTyping(true);

    chatMutation.mutate(userMessage, {
      onSuccess: () => {
        setIsTyping(false);
      },
      onError: () => {
        setIsTyping(false);
      }
    });
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleSuggestedPrompt = (prompt: string) => {
    setMessage(prompt);
    inputRef.current?.focus();
  };

  const formatTime = (date: Date) => {
    return new Date(date).toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
  };

  return (
    <AppLayout 
      title="AI Assistant" 
      description="Intelligent conversations with context-aware responses about AI services"
    >
      <div className="p-6 max-w-7xl mx-auto space-y-6">
        
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-[calc(100vh-12rem)]">
          
          {/* Chat Interface */}
          <div className="lg:col-span-3 flex flex-col">
            <Card className="bg-gray-800/60 border-gray-700 flex-1 flex flex-col">
              <CardHeader className="border-b border-gray-700 pb-4">
                <CardTitle className="text-white flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Bot className="w-6 h-6 text-primary-400" />
                    <span>AI Assistant</span>
                    <Badge variant="secondary" className="bg-green-500/20 text-green-400">
                      Online
                    </Badge>
                  </div>
                  <div className="flex items-center space-x-2 text-sm text-gray-400">
                    <Zap className="w-4 h-4" />
                    <span>Powered by GPT-4o</span>
                  </div>
                </CardTitle>
              </CardHeader>
              
              <CardContent className="flex-1 flex flex-col p-0">
                {/* Messages Area */}
                <ScrollArea className="flex-1 p-6">
                  <div className="space-y-6">
                    {/* Welcome Message */}
                    {chatMessages.length === 0 && (
                      <div className="flex items-start space-x-3">
                        <Avatar className="w-8 h-8 bg-gradient-to-r from-primary-500 to-secondary-500">
                          <AvatarFallback className="text-white">
                            <Bot className="w-4 h-4" />
                          </AvatarFallback>
                        </Avatar>
                        <div className="bg-gray-700/50 rounded-lg rounded-tl-none p-4 max-w-md">
                          <p className="text-white text-sm">
                            Hello! I'm your AI assistant specialized in computer vision and AI services. 
                            I can help you understand and use various AI tools including image generation, 
                            classification, object detection, and segmentation. How can I assist you today?
                          </p>
                        </div>
                      </div>
                    )}

                    {/* Chat Messages */}
                    {chatMessages.map((msg, index) => (
                      <div key={index} className={cn(
                        "flex items-start space-x-3",
                        msg.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''
                      )}>
                        <Avatar className={cn(
                          "w-8 h-8",
                          msg.role === 'user' 
                            ? "bg-gradient-to-r from-green-400 to-blue-500" 
                            : "bg-gradient-to-r from-primary-500 to-secondary-500"
                        )}>
                          <AvatarFallback className="text-white">
                            {msg.role === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                          </AvatarFallback>
                        </Avatar>
                        
                        <div className={cn(
                          "rounded-lg p-4 max-w-md",
                          msg.role === 'user' 
                            ? "bg-primary-500 rounded-tr-none" 
                            : "bg-gray-700/50 rounded-tl-none"
                        )}>
                          <p className="text-white text-sm whitespace-pre-wrap">
                            {msg.content}
                          </p>
                          <div className={cn(
                            "flex items-center justify-end mt-2 text-xs",
                            msg.role === 'user' ? "text-primary-100" : "text-gray-400"
                          )}>
                            <Clock className="w-3 h-3 mr-1" />
                            {formatTime(msg.timestamp)}
                          </div>
                        </div>
                      </div>
                    ))}

                    {/* Typing Indicator */}
                    {(isTyping || chatMutation.isPending) && (
                      <div className="flex items-start space-x-3">
                        <Avatar className="w-8 h-8 bg-gradient-to-r from-primary-500 to-secondary-500">
                          <AvatarFallback className="text-white">
                            <Bot className="w-4 h-4" />
                          </AvatarFallback>
                        </Avatar>
                        <div className="bg-gray-700/50 rounded-lg rounded-tl-none p-4">
                          <div className="flex items-center space-x-1">
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                          </div>
                        </div>
                      </div>
                    )}
                    
                    <div ref={messagesEndRef} />
                  </div>
                </ScrollArea>

                {/* Input Area */}
                <div className="border-t border-gray-700 p-4">
                  {/* Suggested Prompts */}
                  {chatMessages.length === 0 && (
                    <div className="mb-4">
                      <p className="text-sm text-gray-400 mb-2">Suggested questions:</p>
                      <div className="flex flex-wrap gap-2">
                        {SUGGESTED_PROMPTS.slice(0, 3).map((prompt, index) => (
                          <Button
                            key={index}
                            variant="outline"
                            size="sm"
                            onClick={() => handleSuggestedPrompt(prompt)}
                            className="bg-gray-700/50 border-gray-600 hover:bg-gray-600 text-xs"
                          >
                            {prompt}
                          </Button>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="flex space-x-2">
                    <Input
                      ref={inputRef}
                      value={message}
                      onChange={(e) => setMessage(e.target.value)}
                      onKeyPress={handleKeyPress}
                      placeholder="Ask me anything about AI services..."
                      disabled={chatMutation.isPending}
                      className="flex-1 bg-gray-700 border-gray-600 text-white placeholder-gray-400 focus:border-primary-500"
                    />
                    <Button
                      onClick={handleSendMessage}
                      disabled={!message.trim() || chatMutation.isPending}
                      className="bg-primary-500 hover:bg-primary-600"
                    >
                      <Send className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
          
          {/* Sidebar */}
          <div className="space-y-6">
            
            {/* Chat Statistics */}
            <Card className="bg-gray-800/60 border-gray-700">
              <CardHeader>
                <CardTitle className="text-white flex items-center">
                  <MessageCircle className="w-5 h-5 mr-2 text-primary-400" />
                  Chat Stats
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-400">Messages</span>
                  <span className="text-sm font-medium text-white">{chatMessages.length}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-400">Response Time</span>
                  <span className="text-sm font-medium text-white">~1.2s avg</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-400">Model</span>
                  <span className="text-sm font-medium text-white">GPT-4o</span>
                </div>
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <Card className="bg-gray-800/60 border-gray-700">
              <CardHeader>
                <CardTitle className="text-white">Quick Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <Button 
                  variant="ghost" 
                  className="w-full justify-start text-left hover:bg-gray-700/50"
                  onClick={() => handleSuggestedPrompt("How does image generation work?")}
                >
                  <Sparkles className="w-4 h-4 mr-2 text-gray-400" />
                  <span className="text-sm">Learn about AI models</span>
                </Button>
                <Button 
                  variant="ghost" 
                  className="w-full justify-start text-left hover:bg-gray-700/50"
                  onClick={() => handleSuggestedPrompt("Show me classification examples")}
                >
                  <i className="fas fa-eye w-4 h-4 mr-2 text-gray-400"></i>
                  <span className="text-sm">Get examples</span>
                </Button>
                <Button 
                  variant="ghost" 
                  className="w-full justify-start text-left hover:bg-gray-700/50"
                  onClick={() => handleSuggestedPrompt("Troubleshoot my results")}
                >
                  <i className="fas fa-wrench w-4 h-4 mr-2 text-gray-400"></i>
                  <span className="text-sm">Troubleshoot</span>
                </Button>
                <Button 
                  variant="ghost" 
                  className="w-full justify-start text-left hover:bg-gray-700/50"
                  onClick={() => handleSuggestedPrompt("Best practices for AI")}
                >
                  <i className="fas fa-lightbulb w-4 h-4 mr-2 text-gray-400"></i>
                  <span className="text-sm">Best practices</span>
                </Button>
              </CardContent>
            </Card>

            {/* More Suggested Prompts */}
            <Card className="bg-gray-800/60 border-gray-700">
              <CardHeader>
                <CardTitle className="text-white">More Questions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {SUGGESTED_PROMPTS.slice(3).map((prompt, index) => (
                  <Button
                    key={index}
                    variant="outline"
                    size="sm"
                    onClick={() => handleSuggestedPrompt(prompt)}
                    className="w-full text-left justify-start bg-gray-700/50 border-gray-600 hover:bg-gray-600 text-xs h-auto py-2 px-3"
                  >
                    {prompt}
                  </Button>
                ))}
              </CardContent>
            </Card>

            {/* AI Capabilities */}
            <Card className="bg-gray-800/60 border-gray-700">
              <CardHeader>
                <CardTitle className="text-white">AI Capabilities</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                  <span className="text-sm text-gray-300">Image Analysis</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                  <span className="text-sm text-gray-300">Technical Support</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                  <span className="text-sm text-gray-300">Code Examples</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                  <span className="text-sm text-gray-300">Best Practices</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                  <span className="text-sm text-gray-300">Troubleshooting</span>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
