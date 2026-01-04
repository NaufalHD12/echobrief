import { useState, useEffect, useRef } from "react";
import { BrutalButton } from "@/components/ui/brutal-button";
import { BrutalCard } from "@/components/ui/brutal-card";
import { BrutalBadge } from "@/components/ui/brutal-badge";
import { BrutalInputField } from "@/components/ui/brutal-input-field";
import { PageSizeSelector } from "@/components/ui/page-size-selector";
import { PageLayout } from "@/components/layout/PageLayout";
import { toast } from "sonner";
import { 
  Headphones, 
  Play,
  Pause,
  SkipBack,
  SkipForward,
  Volume2,
  Volume1,
  VolumeX,
  Plus,
  Loader2,
  RefreshCw,
  Search,
  Podcast
} from "lucide-react";
import api from "@/lib/api";
import { Podcast as PodcastType } from "@/types/api";

const Podcasts = () => {
  // Player State
  const [currentPodcast, setCurrentPodcast] = useState<PodcastType | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isScrubbing, setIsScrubbing] = useState(false);
  
  // Data State
  const [podcasts, setPodcasts] = useState<PodcastType[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  
  // Search & Pagination State
  const [searchQuery, setSearchQuery] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [total, setTotal] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  
  const audioRef = useRef<HTMLAudioElement | null>(null);

  // Debounce search
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchQuery);
    }, 500);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  const fetchPodcasts = async (pageNum: number = 1, append: boolean = false, silent: boolean = false) => {
    try {
      if (!silent) {
        if (append) {
          setIsLoadingMore(true);
        } else {
          setIsLoading(true);
        }
      }
      
      const params: any = { page: pageNum, per_page: pageSize };
      if (debouncedSearch) params.search = debouncedSearch;

      const response = await api.get<{ data: { items: PodcastType[]; total: number } }>("/podcasts/", { params });
      const newPodcasts = response.data.data.items;
      const totalCount = response.data.data.total;
      
      if (append) {
        setPodcasts(prev => [...prev, ...newPodcasts]);
      } else {
        setPodcasts(newPodcasts);
        // Set first podcast as current if none selected
        if (!currentPodcast && newPodcasts.length > 0) {
          setCurrentPodcast(newPodcasts[0]);
        }
      }
      
      setTotal(totalCount);
      setPage(pageNum);
      setHasMore(pageNum * pageSize < totalCount);
    } catch (error) {
      console.error("Failed to fetch podcasts:", error);
    } finally {
      setIsLoading(false);
      setIsLoadingMore(false);
    }
  };

  // Fetch on mount and when search changes
  useEffect(() => {
    setPage(1);
    fetchPodcasts(1, false);
  }, [debouncedSearch, pageSize]);

  // Polling for processing podcasts
  useEffect(() => {
    const hasProcessing = podcasts.some(p => p.status === 'processing' || p.status === 'pending');
    
    if (hasProcessing) {
      const interval = setInterval(() => {
        // Silent refresh current page to check statuses
        fetchPodcasts(page, false, true);
      }, 5000);
      return () => clearInterval(interval);
    }
  }, [podcasts, page]);

  const handleLoadMore = () => {
    fetchPodcasts(page + 1, true);
  };

  // Audio handling
  useEffect(() => {
    if (currentPodcast?.audio_url && audioRef.current) {
      // Only set src if it's different to avoid reloading
      if (audioRef.current.src !== currentPodcast.audio_url) {
        audioRef.current.src = currentPodcast.audio_url;
        audioRef.current.volume = volume;
        setCurrentTime(0);
      }
      
      if (isPlaying) {
        audioRef.current.play().catch(e => {
          console.error("Play failed:", e);
          setIsPlaying(false);
        });
      } else {
        audioRef.current.pause();
      }
    }
  }, [currentPodcast, isPlaying]);

  const handleTimeUpdate = () => {
    if (audioRef.current && !isScrubbing) {
      setCurrentTime(audioRef.current.currentTime);
      setDuration(audioRef.current.duration || 0);
    }
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const time = parseFloat(e.target.value);
    setCurrentTime(time);
    if (audioRef.current) {
      audioRef.current.currentTime = time;
    }
  };

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const vol = parseFloat(e.target.value);
    setVolume(vol);
    if (audioRef.current) {
      audioRef.current.volume = vol;
    }
  };

  const toggleMute = () => {
    if (volume > 0) {
      setVolume(0);
      if (audioRef.current) audioRef.current.volume = 0;
    } else {
      setVolume(1);
      if (audioRef.current) audioRef.current.volume = 1;
    }
  };

  const handleCreatePodcast = async () => {
    try {
      setIsGenerating(true);
      // Use quick-generate endpoint with hybrid approach
      const response = await api.post<{ message: string }>("/podcasts/quick-generate", {
        use_cached: true
      });
      // Refresh list to show new pending podcast
      await fetchPodcasts();
      toast.success(response.data.message || "Podcast creation started!");
    } catch (error: any) {
      console.error("Failed to create podcast:", error);
      toast.error(error.response?.data?.detail || "Failed to create podcast. Please try again.");
    } finally {
      setIsGenerating(false);
    }
  };

  const handlePlayPause = (podcast: PodcastType) => {
    if (currentPodcast?.id === podcast.id) {
      setIsPlaying(!isPlaying);
    } else {
      setCurrentPodcast(podcast);
      setIsPlaying(true);
    }
  };

  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case "completed": return "default";
      case "processing": return "accent";
      case "failed": return "destructive";
      default: return "outline";
    }
  };

  const headerActions = (
    <>
      <BrutalButton variant="outline" onClick={() => fetchPodcasts(1, false)} disabled={isLoading}>
        <RefreshCw className={`w-5 h-5 ${isLoading ? "animate-spin" : ""}`} />
      </BrutalButton>
      <BrutalButton onClick={handleCreatePodcast} disabled={isGenerating}>
        {isGenerating ? <Loader2 className="w-5 h-5 mr-2 animate-spin" /> : <Plus className="w-5 h-5 mr-2" />}
        {isGenerating ? "Generating..." : "Generate New"}
      </BrutalButton>
    </>
  );

  return (
    <>
      <audio 
        ref={audioRef}
        onEnded={() => setIsPlaying(false)}
        onPause={() => setIsPlaying(false)}
        onPlay={() => setIsPlaying(true)}
        onTimeUpdate={handleTimeUpdate}
        onLoadedMetadata={(e) => setDuration(e.currentTarget.duration)}
      />
      
      <PageLayout
        title="My Podcasts"
        subtitle="Listen to your generated news podcasts."
        extraBottomPadding
        headerActions={headerActions}
      >
        {/* Search & Count */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
          <BrutalInputField
            icon={Search}
            placeholder="Search podcasts..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            containerClassName="max-w-md flex-1"
          />
          {total > 0 && (
            <div className="flex items-center gap-4">
              <p className="text-sm text-muted-foreground hidden sm:block">
                Showing {podcasts.length} of {total} podcasts
              </p>
              <PageSizeSelector 
                value={pageSize} 
                onChange={setPageSize}
                options={[5, 10, 20]} 
              />
            </div>
          )}
        </div>

        {/* Podcasts List */}
        <div className="space-y-4">
          {isLoading && podcasts.length === 0 ? (
            <div className="flex justify-center py-10">
              <Loader2 className="w-10 h-10 animate-spin text-primary" />
            </div>
          ) : podcasts.length === 0 ? (
            <div className="text-center py-12">
              <div className="w-20 h-20 bg-muted border-[3px] border-foreground shadow-brutal mx-auto mb-4 flex items-center justify-center">
                <Podcast className="w-10 h-10 text-muted-foreground" />
              </div>
              <p className="text-muted-foreground">No podcasts yet. Click "Generate New" to create one!</p>
            </div>
          ) : (
            podcasts.map((podcast) => (
              <BrutalCard 
                key={podcast.id} 
                variant="static" 
                padding="sm"
                className={`cursor-pointer transition-all ${currentPodcast?.id === podcast.id ? "border-secondary ring-2 ring-secondary/20" : ""}`}
                onClick={() => setCurrentPodcast(podcast)}
              >
                <div className="flex items-center gap-4">
                  <button 
                    className={`w-14 h-14 border-[3px] border-foreground shadow-brutal flex items-center justify-center flex-shrink-0 transition-all ${
                      podcast.status === 'completed' 
                        ? 'bg-primary hover:shadow-brutal-hover hover:-translate-x-0.5 hover:-translate-y-0.5' 
                        : 'bg-muted cursor-not-allowed'
                    }`}
                    disabled={podcast.status !== 'completed'}
                    onClick={(e) => {
                      e.stopPropagation();
                      if (podcast.status === 'completed') {
                        handlePlayPause(podcast);
                      }
                    }}
                  >
                    {isPlaying && currentPodcast?.id === podcast.id ? (
                      <Pause className="w-6 h-6" />
                    ) : podcast.status === 'completed' ? (
                      <Play className="w-6 h-6 ml-1" />
                    ) : (
                      <Loader2 className="w-6 h-6 animate-spin" />
                    )}
                  </button>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-bold text-lg truncate">{podcast.status === 'processing' ? 'Generating Podcast...' : `Podcast ${new Date(podcast.created_at).toLocaleDateString()}`}</h3>
                      <BrutalBadge variant={getStatusBadgeVariant(podcast.status) as any} size="sm" className="capitalize">
                        {podcast.status}
                      </BrutalBadge>
                    </div>
                    <div className="flex items-center gap-3 text-sm text-muted-foreground">
                      <span>{Math.floor(podcast.duration_seconds / 60)}:{(podcast.duration_seconds % 60).toString().padStart(2, '0')}</span>
                      <span>•</span>
                      <span>{new Date(podcast.created_at).toLocaleTimeString()}</span>
                    </div>
                  </div>
                  <div className="hidden sm:flex gap-2">
                    {podcast.topics?.map((topic) => (
                      <BrutalBadge key={topic.id} variant="outline" size="sm">
                        {topic.name}
                      </BrutalBadge>
                    ))}
                  </div>
                </div>
              </BrutalCard>
            ))
          )}
        </div>

        {/* Load More Button */}
        {hasMore && (
          <div className="flex justify-center mt-8">
            <BrutalButton variant="outline" onClick={handleLoadMore} disabled={isLoadingMore}>
              {isLoadingMore ? <Loader2 className="w-5 h-5 mr-2 animate-spin" /> : null}
              {isLoadingMore ? "Loading..." : "Load More"}
            </BrutalButton>
          </div>
        )}
      </PageLayout>

      {/* Audio Player */}
      {currentPodcast && (
        <div className="fixed bottom-0 left-0 right-0 lg:left-64 bg-card border-t-[3px] border-foreground z-50">
          <div className="p-4">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-secondary border-[2px] border-foreground flex items-center justify-center flex-shrink-0">
                <Headphones className="w-6 h-6" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-bold truncate">Podcast {new Date(currentPodcast.created_at).toLocaleDateString()}</p>
                <div className="hidden sm:flex items-center gap-2 text-xs text-muted-foreground">
                   {currentPodcast.topics?.slice(0, 3).map(t => t.name).join(", ")}
                </div>
              </div>
              <div className="flex items-center gap-2">
                <button className="w-10 h-10 hover:bg-muted flex items-center justify-center transition-colors">
                  <SkipBack className="w-5 h-5" />
                </button>
                <button 
                  className={`w-12 h-12 border-[2px] border-foreground shadow-brutal flex items-center justify-center ${
                    currentPodcast.status === 'completed' ? 'bg-primary' : 'bg-muted cursor-not-allowed'
                  }`}
                  onClick={() => currentPodcast.status === 'completed' && setIsPlaying(!isPlaying)}
                  disabled={currentPodcast.status !== 'completed'}
                >
                  {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5 ml-0.5" />}
                </button>
                <button className="w-10 h-10 hover:bg-muted flex items-center justify-center transition-colors">
                  <SkipForward className="w-5 h-5" />
                </button>
              </div>
              <div className="hidden md:flex items-center gap-2 w-32 group relative">
                <button onClick={toggleMute} className="hover:text-primary transition-colors">
                  {volume === 0 ? (
                    <VolumeX className="w-5 h-5 text-muted-foreground" />
                  ) : volume < 0.5 ? (
                    <Volume1 className="w-5 h-5 text-muted-foreground" />
                  ) : (
                    <Volume2 className="w-5 h-5 text-muted-foreground" />
                  )}
                </button>
                <div className="flex-1 relative h-4 flex items-center group/vol">
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.01"
                    value={volume}
                    onChange={handleVolumeChange}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                  />
                  <div className="w-full h-1.5 bg-muted border-[1.5px] border-foreground relative overflow-hidden rounded-full">
                    <div 
                      className="h-full bg-foreground transition-all duration-100 ease-linear"
                      style={{ width: `${volume * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>
            
            {/* Interactive Seekbar */}
            <div className="mt-3 flex items-center gap-3">
              <span className="text-xs text-muted-foreground w-10 font-mono">
                {Math.floor(currentTime / 60)}:{(Math.floor(currentTime) % 60).toString().padStart(2, '0')}
              </span>
              <div className="flex-1 relative h-4 flex items-center group">
                <input
                  type="range"
                  min="0"
                  max={duration || 100}
                  value={currentTime}
                  onChange={handleSeek}
                  onMouseDown={() => setIsScrubbing(true)}
                  onMouseUp={() => setIsScrubbing(false)}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                />
                <div className="w-full h-2 bg-muted border-[2px] border-foreground relative overflow-hidden">
                  <div 
                    className="h-full bg-secondary transition-all duration-100 ease-linear"
                    style={{ width: `${(currentTime / (duration || 1)) * 100}%` }}
                  />
                </div>
              </div>
              <span className="text-xs text-muted-foreground w-10 text-right font-mono">
                {Math.floor((duration || currentPodcast.duration_seconds) / 60)}:{Math.floor((duration || currentPodcast.duration_seconds) % 60).toString().padStart(2, '0')}
              </span>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default Podcasts;

