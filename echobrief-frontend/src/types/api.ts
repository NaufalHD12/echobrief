export interface User {
  id: string;
  email: string;
  username: string;
  role: string;
  plan_type: string;
  avatar_url?: string;
  created_at: string;
  last_login?: string;
}

export interface UserResponse {
  id: string;
  email: string;
  username: string;
  role: string;
  plan_type: string;
  avatar_url?: string;
  created_at: string;
  last_login?: string;
}

export interface Token {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface Topic {
  id: number;
  name: string;
  slug: string;
  description?: string;
}

export interface Article {
  id: number;
  source_id?: number;
  topic_id?: number;
  title: string;
  summary_text: string;
  url: string;
  published_at: string;
  fetched_at: string;
}

export interface PodcastSegment {
  id: number;
  podcast_id: string;
  title: string;
  start_second: number;
  end_second: number;
}

export interface Podcast {
  id: string;
  user_id: string;
  generated_script?: string;
  audio_url?: string;
  duration_seconds: number;
  status: "pending" | "processing" | "completed" | "failed";
  created_at: string;
  topics: Topic[];
  articles: Article[];
  segments: PodcastSegment[];
}

export interface PodcastListResponse {
  items: Podcast[];
  total: number;
  page: number;
  per_page: number;
}

export interface DashboardStats {
  total_podcasts: number;
  completed_podcasts: number;
  total_topics: number;
  plan_type: string;
  member_since: string;
}

export interface DashboardResponse {
  user: UserResponse;
  stats: DashboardStats;
  recent_podcasts: Podcast[];
  recent_articles: Article[];
  favorite_topics: Topic[];
}

export interface GlobalSearchResult {
  type: "article" | "topic" | "source";
  id: number;
  title: string;
  description?: string;
  url?: string;
}

export interface GlobalSearchResponse {
  items: GlobalSearchResult[];
  total: number;
  page: number;
  per_page: number;
}

export interface ApiResponse<T> {
  message: string;
  data: T;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
}

export interface OnboardingRequest {
  plan_type: "free" | "paid";
  topic_ids: string; // comma separated
  avatar?: File;
}
