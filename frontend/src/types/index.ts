/** 科类枚举 */
export enum SubjectType {
  PHYSICS = "物理类",
  HISTORY = "历史类",
  COMPREHENSIVE_REFORM = "综合改革",
}

export const SUBJECT_TYPE_OPTIONS = [
  { value: SubjectType.PHYSICS, label: "物理类" },
  { value: SubjectType.HISTORY, label: "历史类" },
  { value: SubjectType.COMPREHENSIVE_REFORM, label: "综合改革" },
];

/** 考试科类枚举 */
export enum ExamType {
  NORMAL = "普通类",
  ART = "艺术类",
  SPORTS = "体育类",
}

export const EXAM_TYPE_OPTIONS = [
  {
    value: ExamType.NORMAL,
    label: "普通类",
    description:
      "普通高考文化课考试，可选工学、理学、医学、经济学、管理学、法学、文学、历史学、哲学、农学等专业",
  },
  {
    value: ExamType.ART,
    label: "艺术类",
    description:
      "需参加艺术类专业考试（省统考/校考），可选视觉传达设计、音乐学、表演、播音主持、动画、舞蹈等专业",
  },
  {
    value: ExamType.SPORTS,
    label: "体育类",
    description:
      "需参加体育类专业测试，可选体育教育、运动训练、武术与民族传统体育等专业",
  },
];

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
  ranking: number | null;
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
  reason: string | null;
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
    exam_type: string | null;
    professional_score: number | null;
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
  advisor_id: string | null;
  last_message_at: string | null;
}

export interface ChatMessage {
  id: string;
  session_id: string;
  role: "user" | "assistant" | "system" | "tool";
  content: string;
  advisor_id: string | null;
  advisor_name: string | null;
  created_at: string;
}

/** 会员等级 */
export enum MembershipTier {
  FREE = "free",
  STANDARD = "standard",
  DEEP = "deep",
  VIP = "vip",
}

/** 支付方式 */
export enum PaymentMethod {
  ALIPAY = "alipay",
  WECHAT = "wechat",
}

/** 订单状态 */
export enum OrderStatus {
  PENDING = "pending",
  PAID = "paid",
  ACTIVATED = "activated",
  EXPIRED = "expired",
  CANCELLED = "cancelled",
}

/** 会员等级信息 */
export interface TierInfo {
  tier: string;
  name: string;
  price: number;
  period?: string;
  features: string[];
  recommended?: boolean;
  current?: boolean;
}

/** 会员定价列表 */
export interface TierListResponse {
  tiers: TierInfo[];
  current_tier: string | null;
  expires_at: string | null;
}

/** 创建订单响应 */
export interface CreateOrderResponse {
  order_id: string;
  order_no: string;
  amount: number;
  payment_method: string;
  qr_content: string;
  expires_in: number;
}

/** 订单信息 */
export interface OrderInfo {
  order_id: string;
  order_no: string;
  tier: string;
  amount: number;
  payment_method: string | null;
  status: string;
  paid_at: string | null;
  created_at: string;
}

/** 会员状态 */
export interface MembershipInfo {
  tier: string;
  name: string;
  expires_at: string | null;
  days_remaining: number | null;
}
