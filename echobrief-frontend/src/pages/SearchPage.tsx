import { useState, useEffect } from "react";
import { BrutalCard } from "@/components/ui/brutal-card";
import { BrutalBadge } from "@/components/ui/brutal-badge";
import { BrutalInputField } from "@/components/ui/brutal-input-field";
import { PageSizeSelector } from "@/components/ui/page-size-selector";
import { PageLayout } from "@/components/layout/PageLayout";
import { 
  FileText, 
  Tag,
  Globe,
  ArrowRight,
  Loader2,
  Search
} from "lucide-react";
import api from "@/lib/api";
import { GlobalSearchResult, GlobalSearchResponse } from "@/types/api";

const SearchPage = () => {
  const [query, setQuery] = useState("");
  const [debouncedQuery, setDebouncedQuery] = useState("");
  const [activeTab, setActiveTab] = useState<"all" | "article" | "topic" | "source">("all");
  const [results, setResults] = useState<GlobalSearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [pageSize, setPageSize] = useState(20);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(query);
    }, 500);
    return () => clearTimeout(timer);
  }, [query]);

  useEffect(() => {
    const fetchResults = async () => {
      if (!debouncedQuery.trim()) {
        setResults([]);
        setHasSearched(false);
        return;
      }

      try {
        setIsLoading(true);
        const response = await api.get<{ data: GlobalSearchResponse }>("/dashboard/search", {
          params: { q: debouncedQuery, per_page: pageSize }
        });
        setResults(response.data.data.items);
        setHasSearched(true);
      } catch (error) {
        console.error("Failed to search:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchResults();
  }, [debouncedQuery, pageSize]);

  const filteredResults = activeTab === 'all' 
    ? results 
    : results.filter(r => r.type === activeTab);

  const articles = results.filter(r => r.type === 'article');
  const topics = results.filter(r => r.type === 'topic');
  const sources = results.filter(r => r.type === 'source');

  return (
    <PageLayout
      title="Search"
      subtitle="Find articles, topics, and sources across EchoBrief."
      centered
    >
      {/* Search Bar */}
      <div className="relative mb-8 flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <BrutalInputField
            icon={Search}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search for anything..."
            className="h-14 text-lg"
          />
          {isLoading && (
            <div className="absolute right-4 top-1/2 -translate-y-1/2">
              <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
            </div>
          )}
        </div>
        <div className="flex-shrink-0">
          <PageSizeSelector 
            value={pageSize} 
            onChange={setPageSize}
            options={[10, 20, 50, 100]} 
            className="h-14"
          />
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-[3px] border-foreground mb-8">
        {(["all", "article", "topic", "source"] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`flex-1 py-3 font-bold uppercase text-sm transition-colors border-r-[3px] border-foreground last:border-r-0 ${
              activeTab === tab ? "bg-primary" : "bg-card hover:bg-muted"
            }`}
          >
            {tab === 'all' ? 'All' : tab.charAt(0).toUpperCase() + tab.slice(1) + 's'}
          </button>
        ))}
      </div>

      {/* Results */}
      {hasSearched ? (
        <div className="space-y-8">
          {filteredResults.length === 0 ? (
             <div className="text-center py-12 text-muted-foreground">
               No results found for "{query}".
             </div>
          ) : (
            <>
              {/* Articles */}
              {(activeTab === "all" || activeTab === "article") && (activeTab === 'article' ? filteredResults : articles).length > 0 && (
                <div>
                  <div className="flex items-center gap-2 mb-4">
                    <FileText className="w-5 h-5" />
                    <h2 className="text-lg font-bold">Articles</h2>
                    <BrutalBadge variant="outline" size="sm">{(activeTab === 'article' ? filteredResults : articles).length}</BrutalBadge>
                  </div>
                  <div className="space-y-3">
                    {(activeTab === 'article' ? filteredResults : articles).map((result) => (
                      <BrutalCard key={`${result.type}-${result.id}`} padding="sm" className="cursor-pointer hover:bg-muted/50 transition-colors">
                        <a href={result.url} target="_blank" rel="noopener noreferrer" className="flex items-center justify-between">
                          <div>
                            <p className="font-bold">{result.title}</p>
                            {result.description && <p className="text-sm text-muted-foreground">{result.description}</p>}
                          </div>
                          <ArrowRight className="w-5 h-5 opacity-50" />
                        </a>
                      </BrutalCard>
                    ))}
                  </div>
                </div>
              )}

              {/* Topics */}
              {(activeTab === "all" || activeTab === "topic") && (activeTab === 'topic' ? filteredResults : topics).length > 0 && (
                <div>
                  <div className="flex items-center gap-2 mb-4">
                    <Tag className="w-5 h-5" />
                    <h2 className="text-lg font-bold">Topics</h2>
                    <BrutalBadge variant="outline" size="sm">{(activeTab === 'topic' ? filteredResults : topics).length}</BrutalBadge>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {(activeTab === 'topic' ? filteredResults : topics).map((result) => (
                      <BrutalCard key={`${result.type}-${result.id}`} padding="sm" className="cursor-pointer hover:bg-muted/50 transition-colors">
                         <div className="flex items-center justify-between">
                          <div>
                            <p className="font-bold">{result.title}</p>
                          </div>
                          <ArrowRight className="w-5 h-5 opacity-50" />
                        </div>
                      </BrutalCard>
                    ))}
                  </div>
                </div>
              )}

              {/* Sources */}
              {(activeTab === "all" || activeTab === "source") && (activeTab === 'source' ? filteredResults : sources).length > 0 && (
                <div>
                  <div className="flex items-center gap-2 mb-4">
                    <Globe className="w-5 h-5" />
                    <h2 className="text-lg font-bold">Sources</h2>
                    <BrutalBadge variant="outline" size="sm">{(activeTab === 'source' ? filteredResults : sources).length}</BrutalBadge>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {(activeTab === 'source' ? filteredResults : sources).map((result) => (
                      <BrutalCard key={`${result.type}-${result.id}`} padding="sm" className="cursor-pointer hover:bg-muted/50 transition-colors">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="font-bold">{result.title}</p>
                          </div>
                          <ArrowRight className="w-5 h-5 opacity-50" />
                        </div>
                      </BrutalCard>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      ) : (
        <div className="text-center py-12">
          <div className="w-20 h-20 bg-muted border-[3px] border-foreground shadow-brutal mx-auto mb-4 flex items-center justify-center">
            <Search className="w-10 h-10 text-muted-foreground" />
          </div>
          <p className="text-muted-foreground">Start typing to search across articles, topics, and sources.</p>
        </div>
      )}
    </PageLayout>
  );
};

export default SearchPage;

