export interface University {
  id: string;
  name: string;
  province: string;
  city: string;
  level: string | null;
  type: string | null;
  tags: string[];
  tuition_min: number | null;
  tuition_max: number | null;
  website: string | null;
  logo_url: string | null;
  description: string | null;
}

export interface PaginatedUniversityResponse {
  items: University[];
  total: number;
  page: number;
  page_size: number;
}

export interface RecommendItem {
  university_name: string;
  major_name: string;
  min_rank: number | null;
  rank_ratio: number | null;
  adapter_score: number | null;
}

export interface RecommendResult {
  rush: RecommendItem[];
  stable: RecommendItem[];
  safe: RecommendItem[];
  profile_completeness: number;
}

export interface UserProfile {
  basic_info: {
    score: number;
    rank: number;
    province: string;
    subject_type: string;
  } | null;
  family_info: Record<string, unknown> | null;
  personality: Record<string, unknown> | null;
  ability: Record<string, unknown> | null;
  values_info: Record<string, unknown> | null;
  completeness: number;
}

export interface ChatSession {
  session_id: string;
  title: string;
  message_count: number;
  last_message_at: string | null;
}

export interface ChatMessage {
  id: string;
  session_id: string;
  role: "user" | "assistant" | "system" | "tool";
  content: string;
  created_at: string;
}
