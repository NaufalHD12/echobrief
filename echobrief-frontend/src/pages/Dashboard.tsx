import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { BrutalButton } from "@/components/ui/brutal-button";
import { BrutalCard } from "@/components/ui/brutal-card";
import { BrutalBadge } from "@/components/ui/brutal-badge";
import { PageLayout } from "@/components/layout/PageLayout";
import { 
  Play, 
  Podcast, 
  Calendar,
  Clock,
  Plus,
  Hand,
  Loader2
} from "lucide-react";
import api from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";
import { DashboardResponse } from "@/types/api";

const Dashboard = () => {
  const { user } = useAuth();
  const [data, setData] = useState<DashboardResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const response = await api.get<{ data: DashboardResponse }>("/dashboard/");
        setData(response.data.data);
      } catch (error) {
        console.error("Failed to fetch dashboard:", error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchDashboard();
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Loader2 className="w-10 h-10 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <PageLayout hideTitle>
      {/* Welcome Header */}
      <div className="mb-8">
        <h1 className="text-3xl lg:text-4xl font-bold mb-2 flex items-center gap-2">
          Welcome back, {user?.username || "there"}! <Hand className="w-8 h-8 text-secondary rotate-12" />
        </h1>
        <p className="text-muted-foreground">Here's what's happening with your news today.</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
        <BrutalCard variant="primary" padding="sm">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-background border-[3px] border-foreground flex items-center justify-center">
              <Podcast className="w-6 h-6" />
            </div>
            <div>
              <p className="text-2xl font-bold">{data?.stats.total_podcasts || 0}</p>
              <p className="text-sm">Total Podcasts</p>
            </div>
          </div>
        </BrutalCard>

        <BrutalCard variant="secondary" padding="sm">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-background border-[3px] border-foreground flex items-center justify-center">
              <Clock className="w-6 h-6" />
            </div>
            <div>
              <p className="text-2xl font-bold text-secondary-foreground">{data?.stats.completed_podcasts || 0}</p>
              <p className="text-sm text-secondary-foreground/80">Completed</p>
            </div>
          </div>
        </BrutalCard>

        <BrutalCard variant="accent" padding="sm">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-background border-[3px] border-foreground flex items-center justify-center">
              <Calendar className="w-6 h-6" />
            </div>
            <div>
              <p className="text-lg font-bold truncate">since {new Date(data?.stats.member_since || Date.now()).toLocaleDateString()}</p>
              <p className="text-sm">Member</p>
            </div>
          </div>
        </BrutalCard>
      </div>

      {/* Quick Actions */}
      <BrutalCard variant="static" padding="sm" className="mb-8">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          <div>
            <h2 className="text-xl font-bold">Ready for today's news?</h2>
            <p className="text-muted-foreground text-sm">Generate a fresh podcast based on your topics.</p>
          </div>
          <Link to="/podcasts">
            <BrutalButton size="lg">
              <Plus className="w-5 h-5 mr-2" />
              Generate Podcast
            </BrutalButton>
          </Link>
        </div>
      </BrutalCard>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Recent Podcasts */}
        <BrutalCard variant="static">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold">Recent Podcasts</h2>
            <Link to="/podcasts" className="text-sm font-medium text-secondary hover:underline">
              View all
            </Link>
          </div>
          <div className="space-y-3">
            {data?.recent_podcasts.length === 0 ? (
              <p className="text-muted-foreground text-center py-4">No podcasts yet. Generate one!</p>
            ) : (
              data?.recent_podcasts.map((podcast) => (
                <div key={podcast.id} className="flex items-center gap-4 p-3 bg-muted border-[2px] border-foreground hover:bg-muted/50 transition-colors">
                  <button className="w-10 h-10 bg-primary border-[2px] border-foreground flex items-center justify-center flex-shrink-0 hover:shadow-brutal transition-all">
                    <Play className="w-4 h-4 ml-0.5" />
                  </button>
                  <div className="flex-1 min-w-0">
                    <p className="font-bold truncate">Podcast from {new Date(podcast.created_at).toLocaleDateString()}</p>
                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                      <span>{Math.floor(podcast.duration_seconds / 60)}:{(podcast.duration_seconds % 60).toString().padStart(2, '0')}</span>
                      <span>•</span>
                      <span className="capitalize">{podcast.status}</span>
                    </div>
                  </div>
                  <div className="hidden sm:flex gap-1">
                    {podcast.topics.slice(0, 2).map((topic) => (
                      <BrutalBadge key={topic.id} variant="outline" size="sm">
                        {topic.name}
                      </BrutalBadge>
                    ))}
                  </div>
                </div>
              ))
            )}
          </div>
        </BrutalCard>

        {/* Recent Articles */}
        <BrutalCard variant="static">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold">Latest Articles</h2>
            <Link to="/articles" className="text-sm font-medium text-secondary hover:underline">
              View all
            </Link>
          </div>
          <div className="space-y-3">
            {data?.recent_articles.length === 0 ? (
              <p className="text-muted-foreground text-center py-4">No articles found.</p>
            ) : (
              data?.recent_articles.map((article) => (
                <a key={article.id} href={article.url} target="_blank" rel="noopener noreferrer" className="block p-3 bg-muted border-[2px] border-foreground hover:bg-muted/50 transition-colors cursor-pointer">
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <p className="font-bold text-sm leading-tight mb-1">{article.title}</p>
                      <p className="text-xs text-muted-foreground">{new Date(article.published_at).toLocaleDateString()}</p>
                    </div>
                  </div>
                </a>
              ))
            )}
          </div>
        </BrutalCard>
      </div>
    </PageLayout>
  );
};

export default Dashboard;

