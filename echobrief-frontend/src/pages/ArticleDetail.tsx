import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { BrutalButton } from "@/components/ui/brutal-button";
import { BrutalCard } from "@/components/ui/brutal-card";
import { BrutalBadge } from "@/components/ui/brutal-badge";
import { PageLayout } from "@/components/layout/PageLayout";
import { 
  ArrowLeft,
  ExternalLink,
  Calendar,
  Globe,
  Tag,
  Loader2,
  Clock,
  Share2
} from "lucide-react";
import api from "@/lib/api";
import { Article, Topic } from "@/types/api";
import { toast } from "sonner";

interface Source {
  id: number;
  name: string;
  base_url: string;
}

const ArticleDetail = () => {
  const { id } = useParams<{ id: string }>();
  const [article, setArticle] = useState<Article | null>(null);
  const [topic, setTopic] = useState<Topic | null>(null);
  const [source, setSource] = useState<Source | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchArticle = async () => {
      if (!id) return;
      
      try {
        setIsLoading(true);
        setError(null);
        
        // Fetch article
        const articleRes = await api.get<{ data: Article }>(`/articles/${id}`);
        const articleData = articleRes.data.data;
        setArticle(articleData);

        // Fetch topic and source in parallel
        const [topicRes, sourceRes] = await Promise.all([
          articleData.topic_id 
            ? api.get<{ data: Topic }>(`/topics/${articleData.topic_id}`) 
            : null,
          articleData.source_id 
            ? api.get<{ data: Source }>(`/sources/${articleData.source_id}`) 
            : null,
        ]);

        if (topicRes) setTopic(topicRes.data.data);
        if (sourceRes) setSource(sourceRes.data.data);
      } catch (err: any) {
        console.error("Failed to fetch article:", err);
        setError(err.response?.data?.detail || "Failed to load article");
      } finally {
        setIsLoading(false);
      }
    };

    fetchArticle();
  }, [id]);

  const handleShare = async () => {
    if (!article) return;
    
    try {
      await navigator.share({
        title: article.title,
        text: article.summary_text || "",
        url: window.location.href,
      });
    } catch (err) {
      // Fallback: copy to clipboard
      await navigator.clipboard.writeText(window.location.href);
      toast.success("Link copied to clipboard!");
    }
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString("en-US", {
      weekday: "long",
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };

  const formatTime = (dateStr: string) => {
    return new Date(dateStr).toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  if (isLoading) {
    return (
      <PageLayout title="Loading..." subtitle="">
        <div className="flex justify-center py-20">
          <Loader2 className="w-10 h-10 animate-spin text-primary" />
        </div>
      </PageLayout>
    );
  }

  if (error || !article) {
    return (
      <PageLayout title="Article Not Found" subtitle="">
        <div className="text-center py-20">
          <div className="w-20 h-20 bg-muted border-[3px] border-foreground shadow-brutal mx-auto mb-4 flex items-center justify-center">
            <ExternalLink className="w-10 h-10 text-muted-foreground" />
          </div>
          <p className="text-muted-foreground mb-6">{error || "Article not found"}</p>
          <Link to="/articles">
            <BrutalButton>
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Articles
            </BrutalButton>
          </Link>
        </div>
      </PageLayout>
    );
  }

  const headerActions = (
    <>
      <BrutalButton variant="outline" onClick={handleShare}>
        <Share2 className="w-4 h-4 mr-2" />
        Share
      </BrutalButton>
      <a href={article.url} target="_blank" rel="noopener noreferrer">
        <BrutalButton>
          <ExternalLink className="w-4 h-4 mr-2" />
          Read Original
        </BrutalButton>
      </a>
    </>
  );

  return (
    <PageLayout
      title=""
      subtitle=""
      hideTitle
      headerActions={headerActions}
    >
      {/* Back Button */}
      <Link to="/articles" className="inline-flex items-center text-muted-foreground hover:text-foreground mb-6 transition-colors">
        <ArrowLeft className="w-4 h-4 mr-2" />
        Back to Articles
      </Link>

      {/* Article Header */}
      <div className="mb-8">
        <div className="flex flex-wrap items-center gap-3 mb-4">
          {topic && (
            <BrutalBadge variant="accent" size="lg">
              <Tag className="w-3 h-3 mr-1" />
              {topic.name}
            </BrutalBadge>
          )}
          {source && (
            <BrutalBadge variant="outline" size="lg">
              <Globe className="w-3 h-3 mr-1" />
              {source.name}
            </BrutalBadge>
          )}
        </div>
        
        <h1 className="text-3xl lg:text-4xl font-bold mb-4 leading-tight">
          {article.title}
        </h1>

        <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
          <div className="flex items-center gap-1">
            <Calendar className="w-4 h-4" />
            <span>{formatDate(article.published_at)}</span>
          </div>
          <div className="flex items-center gap-1">
            <Clock className="w-4 h-4" />
            <span>{formatTime(article.published_at)}</span>
          </div>
        </div>
      </div>

      {/* Article Content */}
      <BrutalCard variant="static" className="mb-8">
        <h2 className="text-lg font-bold mb-4">Summary</h2>
        <p className="text-lg leading-relaxed whitespace-pre-wrap">
          {article.summary_text || "No summary available for this article."}
        </p>
      </BrutalCard>

      {/* Source Info */}
      {source && (
        <BrutalCard variant="static" className="mb-8">
          <h2 className="text-lg font-bold mb-4">Source Information</h2>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-secondary border-[2px] border-foreground flex items-center justify-center">
                <Globe className="w-6 h-6" />
              </div>
              <div>
                <p className="font-bold">{source.name}</p>
                <p className="text-sm text-muted-foreground">{source.base_url}</p>
              </div>
            </div>
            <a href={source.base_url} target="_blank" rel="noopener noreferrer">
              <BrutalButton variant="outline" size="sm">
                Visit Site
              </BrutalButton>
            </a>
          </div>
        </BrutalCard>
      )}

      {/* Read Original CTA */}
      <div className="text-center py-8">
        <p className="text-muted-foreground mb-4">
          Want to read the full article?
        </p>
        <a href={article.url} target="_blank" rel="noopener noreferrer">
          <BrutalButton size="lg">
            <ExternalLink className="w-5 h-5 mr-2" />
            Read Full Article
          </BrutalButton>
        </a>
      </div>
    </PageLayout>
  );
};

export default ArticleDetail;
