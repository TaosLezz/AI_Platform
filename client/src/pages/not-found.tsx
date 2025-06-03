import { Card, CardContent } from "@/components/ui/card";
import { AlertCircle } from "lucide-react";

export default function NotFound() {
  return (
<<<<<<< HEAD
    <div className="min-h-screen w-full flex items-center justify-center bg-gray-50">
      <Card className="w-full max-w-md mx-4">
        <CardContent className="pt-6">
          <div className="flex mb-4 gap-2">
            <AlertCircle className="h-8 w-8 text-red-500" />
            <h1 className="text-2xl font-bold text-gray-900">404 Page Not Found</h1>
          </div>

          <p className="mt-4 text-sm text-gray-600">
            Did you forget to add the page to the router?
          </p>
=======
    <div className="min-h-screen w-full flex items-center justify-center bg-gradient-to-tr from-blue-50 to-white">
      <Card className="w-full max-w-md mx-4 shadow-lg border border-blue-200 rounded-lg">
        <CardContent className="pt-8 pb-10 px-8 text-center">
          <div className="flex items-center justify-center mb-6">
            <AlertCircle className="h-12 w-12 text-blue-600 animate-pulse" />
          </div>
          <h1 className="text-4xl font-extrabold text-blue-700 mb-3 select-none">
            404 Page Not Found
          </h1>
          <p className="text-md text-blue-500 mb-8">
            The page you are looking for might have been removed, had its name changed, or is temporarily unavailable.
          </p>
          <a
            href="/"
            className="inline-block px-6 py-3 bg-blue-600 text-white font-semibold rounded-md shadow-md hover:bg-blue-700 transition-colors"
          >
            Go Back Home
          </a>
>>>>>>> feature/segment
        </CardContent>
      </Card>
    </div>
  );
}
