import { Switch, Route } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { ThemeProvider } from "next-themes";
import NotFound from "@/pages/not-found";
import Dashboard from "@/pages/dashboard";
import GeneratePage from "@/pages/generate";
import ClassifyPage from "@/pages/classify";
import DetectPage from "@/pages/detect";
import SegmentPage from "@/pages/segment";
import ChatPage from "@/pages/chat";
import AnalyticsPage from "@/pages/analytics";
import LoginPage from "@/pages/login"
<<<<<<< HEAD
=======
import Register from "./pages/register";
>>>>>>> feature/segment

function Router() {
  return (
    <Switch>
      <Route path="/" component={Dashboard} />
<<<<<<< HEAD
=======
      <Route path="/dashboard" component={Dashboard} />
>>>>>>> feature/segment
      <Route path="/generate" component={GeneratePage} />
      <Route path="/classify" component={ClassifyPage} />
      <Route path="/detect" component={DetectPage} />
      <Route path="/segment" component={SegmentPage} />
      <Route path="/chat" component={ChatPage} />
      <Route path="/analytics" component={AnalyticsPage} />
      <Route path="/login" component={LoginPage} />
<<<<<<< HEAD
=======
      <Route path="/register" component={Register}/>
>>>>>>> feature/segment
      <Route component={NotFound} />
    </Switch>
  );
}

function App() {
  return (
    <ThemeProvider attribute="class" defaultTheme="dark" enableSystem={false}>
      <QueryClientProvider client={queryClient}>
        <TooltipProvider>
          <Toaster />
          <Router />
        </TooltipProvider>
      </QueryClientProvider>
    </ThemeProvider>
  );
}

export default App;
