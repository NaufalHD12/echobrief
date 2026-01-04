import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { BrutalButton } from "@/components/ui/brutal-button";
import { BrutalCard } from "@/components/ui/brutal-card";
import { BrutalBadge } from "@/components/ui/brutal-badge";
import { BrutalInputField } from "@/components/ui/brutal-input-field";
import { PageSizeSelector } from "@/components/ui/page-size-selector";
import { PageLayout } from "@/components/layout/PageLayout";
import { 
  ExternalLink,
  FileText,
  Loader2,
  Search,
  ArrowRight
} from "lucide-react";
import api from "@/lib/api";
import { Article, Topic } from "@/types/api";

const Articles = () => {
  const [selectedTopicId, setSelectedTopicId] = useState<number | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [articles, setArticles] = useState<Article[]>([]);
  const [topics, setTopics] = useState<Topic[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(12);
  const [total, setTotal] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  
  // Debounce search
  const [debouncedSearch, setDebouncedSearch] = useState("");

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchQuery);
    }, 500);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Fetch topics once
  useEffect(() => {
    const fetchTopics = async () => {
      try {
        const response = await api.get<{ data: { items: Topic[] } }>("/topics/");
        setTopics(response.data.data.items);
      } catch (error) {
        console.error("Failed to fetch topics:", error);
      }
    };
    fetchTopics();
  }, []);

  // Fetch articles function
  const fetchArticles = async (pageNum: number = 1, append: boolean = false) => {
    try {
      if (append) {
        setIsLoadingMore(true);
      } else {
        setIsLoading(true);
      }
      
      const params: any = { page: pageNum, per_page: pageSize };
      if (selectedTopicId) params.topic_id = selectedTopicId;
      if (debouncedSearch) params.search = debouncedSearch;

      const response = await api.get<{ data: { items: Article[]; total: number } }>("/articles/", { params });
      const newArticles = response.data.data.items;
      const totalCount = response.data.data.total;
      
      if (append) {
        setArticles(prev => [...prev, ...newArticles]);
      } else {
        setArticles(newArticles);
      }
      
      setTotal(totalCount);
      setPage(pageNum);
      setHasMore(pageNum * pageSize < totalCount);
    } catch (error) {
      console.error("Failed to fetch articles:", error);
    } finally {
      setIsLoading(false);
      setIsLoadingMore(false);
    }
  };

  // Fetch articles when filters change
  useEffect(() => {
    setPage(1);
    fetchArticles(1, false);
  }, [selectedTopicId, debouncedSearch, pageSize]);

  const handleLoadMore = () => {
    fetchArticles(page + 1, true);
  };

  const getTopicName = (id?: number) => {
    if (!id) return "Unknown";
    const topic = topics.find(t => t.id === id);
    return topic ? topic.name : "General";
  };

  return (
    <PageLayout
      title="Articles"
      subtitle="Browse and read the latest news from your favorite topics."
    >
      {/* Search & Count */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <BrutalInputField
          icon={Search}
          placeholder="Search articles..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          containerClassName="w-full sm:max-w-md"
        />
        {total > 0 && (
          <div className="flex items-center gap-4">
             <p className="text-sm text-muted-foreground hidden sm:block">
              Showing {articles.length} of {total} articles
            </p>
            <PageSizeSelector 
              value={pageSize} 
              onChange={setPageSize}
              options={[12, 24, 48]} 
            />
          </div>
        )}
      </div>

      {/* Topic Pills */}
      <div className="flex flex-wrap gap-2 mb-8">
        <button
          onClick={() => setSelectedTopicId(null)}
          className={`px-4 py-2 border-[2px] border-foreground font-bold uppercase text-sm transition-all ${
            selectedTopicId === null
              ? "bg-primary shadow-brutal"
              : "bg-card hover:bg-muted"
          }`}
        >
          All
        </button>
        
        {topics.map((topic) => (
          <button
            key={topic.id}
            onClick={() => setSelectedTopicId(topic.id)}
            className={`px-4 py-2 border-[2px] border-foreground font-bold uppercase text-sm transition-all ${
              selectedTopicId === topic.id
                ? "bg-primary shadow-brutal"
                : "bg-card hover:bg-muted"
            }`}
          >
            {topic.name}
          </button>
        ))}
      </div>

      {/* Articles Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {isLoading ? (
           <div className="col-span-full flex justify-center py-10">
             <Loader2 className="w-10 h-10 animate-spin text-primary" />
           </div>
        ) : articles.length === 0 ? (
          <div className="col-span-full text-center py-12">
            <div className="w-20 h-20 bg-muted border-[3px] border-foreground shadow-brutal mx-auto mb-4 flex items-center justify-center">
              <FileText className="w-10 h-10 text-muted-foreground" />
            </div>
            <p className="text-muted-foreground">No articles found matching your criteria.</p>
          </div>
        ) : (
          articles.map((article) => (
            <Link key={article.id} to={`/articles/${article.id}`}>
              <BrutalCard className="cursor-pointer group flex flex-col h-full hover:shadow-brutal-hover hover:-translate-x-0.5 hover:-translate-y-0.5 transition-all" padding="sm">
                <div className="flex items-start justify-between gap-2 mb-3">
                  <BrutalBadge variant="accent" size="sm">
                    {getTopicName(article.topic_id)}
                  </BrutalBadge>
                  <span className="text-xs text-muted-foreground">{new Date(article.published_at).toLocaleDateString()}</span>
                </div>
                <h3 className="text-lg font-bold mb-2 group-hover:text-secondary transition-colors line-clamp-2">
                  {article.title}
                </h3>
                <p className="text-sm text-muted-foreground mb-4 line-clamp-3">{article.summary_text}</p>
                <div className="mt-auto flex items-center justify-between pt-4 border-t border-border/50">
                  <span className="text-sm font-medium truncate max-w-[200px]">{new URL(article.url).hostname.replace('www.', '')}</span>
                  <span className="flex items-center text-sm font-bold text-primary">
                    View Details <ArrowRight className="w-3 h-3 ml-1" />
                  </span>
                </div>
              </BrutalCard>
            </Link>
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
  );
};

export default Articles;

