import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import { Activity, Clock, Zap, Database, TrendingUp, Server, Users } from "lucide-react";

export default function AnalyticsPage() {
  // Fetch dashboard metrics
  const { data: metrics, isLoading: metricsLoading } = useQuery({
    queryKey: ["/api/v1/metrics/dashboard"],
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  // Fetch performance stats
  const { data: performance, isLoading: performanceLoading } = useQuery({
    queryKey: ["/api/v1/performance/stats"],
    refetchInterval: 10000, // Refresh every 10 seconds
  });

  // Fetch cache stats
  const { data: cache, isLoading: cacheLoading } = useQuery({
    queryKey: ["/api/v1/cache/stats"],
    refetchInterval: 15000, // Refresh every 15 seconds
  });

  // Fetch user runs for trends
  const { data: runs, isLoading: runsLoading } = useQuery({
    queryKey: ["/api/v1/runs"],
    refetchInterval: 60000, // Refresh every minute
  });

  const isLoading = metricsLoading || performanceLoading || cacheLoading || runsLoading;

  // Process data for charts
  const serviceData = metrics?.service_breakdown ? 
    Object.entries(metrics.service_breakdown).map(([name, value]) => ({
      name: name.charAt(0).toUpperCase() + name.slice(1),
      value
    })) : [];

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  // Performance trend data (simulated from recent runs)
  const performanceTrend = runs?.slice(0, 10).reverse().map((run: any, index: number) => ({
    time: `${index + 1}`,
    processing_time: run.metrics?.processing_time || 0,
    success: run.status === 'FINISHED' ? 1 : 0
  })) || [];

  if (isLoading) {
    return (
      <div className="container mx-auto p-6">
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {[...Array(4)].map((_, i) => (
              <Card key={i} className="animate-pulse">
                <CardHeader className="space-y-2">
                  <div className="h-4 bg-gray-200 rounded"></div>
                  <div className="h-8 bg-gray-200 rounded"></div>
                </CardHeader>
              </Card>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Analytics Dashboard</h1>
          <p className="text-muted-foreground">
            Monitor your AI platform usage and performance
          </p>
        </div>
        <Badge variant="outline" className="text-sm">
          Live Data
        </Badge>
      </div>

      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Requests</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics?.total_runs || 0}</div>
            <p className="text-xs text-muted-foreground">
              {metrics?.successful_runs || 0} successful
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics?.success_rate?.toFixed(1) || 0}%</div>
            <Progress value={metrics?.success_rate || 0} className="mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Response Time</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {metrics?.avg_processing_time_ms?.toFixed(0) || 0}ms
            </div>
            <p className="text-xs text-muted-foreground">
              Total: {(metrics?.total_processing_time_ms / 1000)?.toFixed(1) || 0}s
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Cache Hit Rate</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{cache?.hit_rate || 0}%</div>
            <p className="text-xs text-muted-foreground">
              {cache?.hits || 0} hits, {cache?.misses || 0} misses
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Analytics */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="services">Services</TabsTrigger>
          <TabsTrigger value="system">System Health</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Service Usage Distribution</CardTitle>
                <CardDescription>
                  Breakdown of requests by AI service type
                </CardDescription>
              </CardHeader>
              <CardContent>
                {serviceData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={serviceData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {serviceData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex items-center justify-center h-64 text-muted-foreground">
                    No service data available
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Performance Trend</CardTitle>
                <CardDescription>
                  Recent request processing times
                </CardDescription>
              </CardHeader>
              <CardContent>
                {performanceTrend.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={performanceTrend}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="time" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Line 
                        type="monotone" 
                        dataKey="processing_time" 
                        stroke="#8884d8" 
                        name="Processing Time (ms)"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex items-center justify-center h-64 text-muted-foreground">
                    No performance data available
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="performance" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>System Metrics</CardTitle>
                <CardDescription>Real-time system performance</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm font-medium">CPU Usage</span>
                    <span className="text-sm">{performance?.cpu?.percent?.toFixed(1) || 0}%</span>
                  </div>
                  <Progress value={performance?.cpu?.percent || 0} />
                </div>
                
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm font-medium">Memory Usage</span>
                    <span className="text-sm">{performance?.memory?.percent?.toFixed(1) || 0}%</span>
                  </div>
                  <Progress value={performance?.memory?.percent || 0} />
                </div>
                
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm font-medium">Disk Usage</span>
                    <span className="text-sm">{performance?.disk?.percent?.toFixed(1) || 0}%</span>
                  </div>
                  <Progress value={performance?.disk?.percent || 0} />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Cache Performance</CardTitle>
                <CardDescription>Redis cache statistics</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center p-4 border rounded-lg">
                    <div className="text-2xl font-bold text-green-600">{cache?.hits || 0}</div>
                    <div className="text-sm text-muted-foreground">Cache Hits</div>
                  </div>
                  <div className="text-center p-4 border rounded-lg">
                    <div className="text-2xl font-bold text-red-600">{cache?.misses || 0}</div>
                    <div className="text-sm text-muted-foreground">Cache Misses</div>
                  </div>
                </div>
                
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm font-medium">Hit Rate</span>
                    <span className="text-sm font-bold text-green-600">{cache?.hit_rate || 0}%</span>
                  </div>
                  <Progress value={cache?.hit_rate || 0} className="h-2" />
                </div>
                
                <div className="pt-2 text-sm text-muted-foreground">
                  Memory Used: {cache?.memory_used || 'N/A'}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="services" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Service Breakdown</CardTitle>
              <CardDescription>Detailed usage by AI service</CardDescription>
            </CardHeader>
            <CardContent>
              {serviceData.length > 0 ? (
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart data={serviceData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="value" fill="#8884d8" name="Requests" />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex items-center justify-center h-64 text-muted-foreground">
                  No service usage data available
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="system" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">System Status</CardTitle>
                <Server className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">Healthy</div>
                <p className="text-xs text-muted-foreground">All systems operational</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Request Rate</CardTitle>
                <Zap className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{performance?.requests?.total_count || 0}</div>
                <p className="text-xs text-muted-foreground">Total requests processed</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Error Rate</CardTitle>
                <Users className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {performance?.requests?.error_rate?.toFixed(2) || 0}%
                </div>
                <p className="text-xs text-muted-foreground">
                  {performance?.requests?.error_count || 0} errors
                </p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}