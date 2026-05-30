import json
import uuid
import time
import hashlib

from openai import AsyncOpenAI

from app.config import get_settings
from app.services.university_service import UniversityService
from app.services.major_service import MajorService
from app.services.admission_service import AdmissionService
from app.services.user_service import UserService
from app.skills import SkillRegistry
from app.services.recommend_service import RecommendService

settings = get_settings()

# 语义扩展缓存（内存，10分钟 TTL）
_SEMANTIC_CACHE: dict[str, dict] = {}

LLM_CONFIGS = {
    "deepseek": {
        "api_key": settings.DEEPSEEK_API_KEY,
        "base_url": settings.DEEPSEEK_BASE_URL,
        "model": "deepseek-v4-pro",
    },
    "qwen": {
        "api_key": settings.QWEN_API_KEY,
        "base_url": settings.QWEN_BASE_URL,
        "model": "qwen3.7-max",
    },
}

SYSTEM_PROMPT = """你是"智愿"的AI高考志愿顾问。你的职责是帮助考生和家长理解高考志愿填报的相关知识，并基于考生的个人情况给出个性化建议。

你可以使用以下工具查询真实数据：
- query_university: 查询院校基本信息（层次、类型、学费、地理位置等）
- query_major: 查询专业详细信息（课程、就业方向、薪资参考等）
- query_admission_score: 查询院校历年录取分数和位次（最重要的数据工具）
- query_score_segment: 查询一分一段表（分数与位次的换算关系）
- get_user_profile: 查询当前用户的五维画像详情
- get_user_recommendation: 查询当前用户最近的冲/稳/保推荐结果

重要规则：
1. 所有分数线、录取概率等数据必须来自工具调用返回的结果，绝对不能编造数据
2. 当用户询问某所学校的录取情况时，必须调用 query_admission_score 获取真实数据
3. 当用户询问分数对应什么位次时，调用 query_score_segment 查询一分一段表
4. 如果工具返回的数据不足以回答问题，请如实告知用户
5. 每次回答末尾适当提醒"以上信息仅供参考，建议结合多方信息综合决策"
6. 保持专业、耐心、客观的语气
7. 不要推荐具体的培训机构或付费服务

当前用户画像摘要：
{profile_summary}

当前推荐结果：
{recommendation_summary}
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "query_university",
            "description": "查询院校基本信息，包括院校层次（985/211/双一流）、类型、所在城市、学费范围、官网等",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "院校名称，支持模糊匹配，如「清华」「浙大」"},
                    "province": {"type": "string", "description": "按院校所在省份筛选，可选"},
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "query_major",
            "description": "查询专业详细信息，包括所属学科门类、学制、核心课程、就业方向、参考薪资等",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "专业名称，支持模糊匹配，如「计算机」「金融」"},
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "query_admission_score",
            "description": "查询某院校在指定省份的历年录取分数和位次数据。这是回答「XX学校多少分能上」类问题的核心工具。",
            "parameters": {
                "type": "object",
                "properties": {
                    "university_name": {"type": "string", "description": "院校名称"},
                    "province": {"type": "string", "description": "考生所在省份，如「浙江」「山东」"},
                    "subject_type": {"type": "string", "description": "科类，如「综合改革」「物理类」「历史类」「理科」「文科」"},
                    "major_name": {"type": "string", "description": "专业名称，可选。不填则返回院校整体录取数据"},
                },
                "required": ["university_name", "province"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "query_score_segment",
            "description": "查询一分一段表，用于分数与位次的相互换算。回答「XX分对应多少位次」或「XX位次对应多少分」时使用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "province": {"type": "string", "description": "省份"},
                    "year": {"type": "integer", "description": "年份，如 2025"},
                    "subject_type": {"type": "string", "description": "科类，如「综合改革」「物理类」「历史类」"},
                    "score": {"type": "integer", "description": "查询该分数附近的位次数据，可选"},
                },
                "required": ["province", "year", "subject_type"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_user_profile",
            "description": "查询当前用户的五维画像详情（基础信息、家庭背景、性格特质、能力优势、价值观），用于个性化分析",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_user_recommendation",
            "description": "查询当前用户最近的智能推荐结果（冲/稳/保院校组合），用于解读推荐方案",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
]


class LLMService:
    def __init__(self, provider: str = "deepseek", user_id: uuid.UUID | None = None):
        config = LLM_CONFIGS.get(provider, LLM_CONFIGS["qwen"])
        self.client = AsyncOpenAI(api_key=config["api_key"], base_url=config["base_url"])
        self.model = config["model"]
        self._user_id = user_id
        self._tool_handlers = {
            "query_university": self._query_university,
            "query_major": self._query_major,
            "query_admission_score": self._query_admission_score,
            "query_score_segment": self._query_score_segment,
            "get_user_profile": self._get_user_profile,
            "get_user_recommendation": self._get_user_recommendation,
        }

    # ── Tool handlers ──────────────────────────────────────────

    async def _query_university(self, name: str, province: str | None = None) -> dict:
        return await UniversityService().search_universities(name, province)

    async def _query_major(self, name: str) -> dict:
        return await MajorService().search_majors(name)

    async def _query_admission_score(
        self,
        university_name: str,
        province: str,
        subject_type: str | None = None,
        major_name: str | None = None,
    ) -> dict:
        return await AdmissionService().get_admission_scores(
            university_name=university_name,
            province=province,
            subject_type=subject_type,
            major_name=major_name,
        )

    async def _query_score_segment(
        self,
        province: str,
        year: int,
        subject_type: str,
        score: int | None = None,
    ) -> dict:
        return await AdmissionService().get_score_segments(
            province=province, year=year, subject_type=subject_type, score=score,
        )

    async def _get_user_profile(self) -> dict:
        if not self._user_id:
            return {"message": "当前无登录用户信息"}
        return await UserService().get_profile_detail(self._user_id)

    async def _get_user_recommendation(self) -> dict:
        if not self._user_id:
            return {"message": "当前无登录用户信息"}
        return await RecommendService().get_latest_recommendation_detail(self._user_id)

    async def _execute_tool_call(self, tool_call) -> str:
        name = tool_call.function.name
        try:
            args = json.loads(tool_call.function.arguments)
        except json.JSONDecodeError:
            return json.dumps({"error": f"工具 {name} 参数解析失败"})

        handler = self._tool_handlers.get(name)
        if not handler:
            return json.dumps({"error": f"未知工具: {name}"})

        result = await handler(**args)
        return json.dumps(result, ensure_ascii=False)

    # ── Semantic Expansion ─────────────────────────────────────

    async def semantic_expand(self, dislikes: list[str] | None = None,
                               interests: list[str] | None = None,
                               major_names: list[str] | None = None) -> dict:
        """使用 LLM 对厌恶/兴趣领域进行语义扩展，返回扩展后的关键词映射"""
        if not dislikes and not interests:
            return {}

        # 生成缓存 key
        cache_key = hashlib.md5(
            json.dumps({"dislikes": dislikes or [], "interests": interests or []},
                       sort_keys=True, ensure_ascii=False).encode()
        ).hexdigest()

        # 检查缓存（10 分钟 TTL）
        cached = _SEMANTIC_CACHE.get(cache_key)
        if cached and time.time() - cached["ts"] < 600:
            return cached["data"]

        # 如果有专业列表，让 LLM 从中筛选，而不是自由生成
        if major_names:
            prompt_parts = []
            if dislikes:
                prompt_parts.append(f"厌恶领域：{', '.join(dislikes)}")
            if interests:
                prompt_parts.append(f"兴趣领域：{', '.join(interests)}")

            prompt = f"""你是一个大学专业推荐助手。用户有以下偏好：
{chr(10).join(prompt_parts)}

以下是数据库中所有可用的专业名称：
{', '.join(major_names)}

请从上述专业列表中，选出与用户厌恶领域相关的专业名称。

要求：
1. 只从给定的专业列表中选择，不要编造新专业
2. 选出所有与厌恶领域相关的专业（包括直接相关和间接相关）
3. 返回 JSON 格式：{{"dislikes": ["专业1", "专业2", ...], "interests": []}}
4. 如果某类为空，返回空数组 []

示例：
厌恶"美术"，专业列表包含["动画", "美术学", "计算机科学与技术", "艺术设计"]
输出：{{"dislikes": ["动画", "美术学", "艺术设计"], "interests": []}}

请只返回 JSON，不要有其他内容。"""

        else:
            # 没有专业列表时，让 LLM 自由生成关键词（兜底）
            prompt_parts = []
            if dislikes:
                prompt_parts.append(f"厌恶领域：{', '.join(dislikes)}")
            if interests:
                prompt_parts.append(f"兴趣领域：{', '.join(interests)}")

            prompt = f"""你是一个大学专业推荐助手。请根据用户的{('和'.join(prompt_parts))}，对每个领域进行语义扩展。

要求：
1. 对每个厌恶/兴趣词，扩展出相关的大学专业名称关键词（5-15个）
2. 关键词应该能匹配大学专业名称中的核心词
3. 返回 JSON 格式，结构为：{{"dislikes": {{"原词": ["扩展词1", "扩展词2", ...]}}, "interests": {{"原词": ["扩展词1", "扩展词2", ...]}}}}
4. 如果某类为空，返回空对象 {{}}

示例：
输入：厌恶"绘画"
输出：{{"dislikes": {{"绘画": ["美术", "艺术", "绘画", "油画", "国画", "版画", "壁画", "雕塑", "书法", "设计"]}}, "interests": {{}}}}

请只返回 JSON，不要有其他内容。"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的语义扩展助手，只返回 JSON 格式的结果。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1500,
            )
            content = response.choices[0].message.content or "{}"
            # 尝试解析 JSON
            result = json.loads(content)

            # 缓存结果
            _SEMANTIC_CACHE[cache_key] = {"data": result, "ts": time.time()}
            return result

        except Exception as e:
            # LLM 不可用时返回空，让调用方使用兜底策略
            return {}

    # ── Chat ───────────────────────────────────────────────────

    async def chat(
        self,
        messages: list[dict],
        profile_summary: str = "",
        recommendation_summary: str = "",
        skill_id: str = "default",
        max_tool_rounds: int = 5,
    ) -> str:
        skill = SkillRegistry.get(skill_id) or SkillRegistry.get("default")
        system = skill.render_system_prompt(profile_summary, recommendation_summary)
        full_messages = [{"role": "system", "content": system}] + messages

        try:
            for _ in range(max_tool_rounds):
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=full_messages,
                    tools=TOOLS,
                    temperature=0.7,
                    max_tokens=2000,
                )
                choice = response.choices[0]
                msg = choice.message

                if choice.finish_reason == "stop" or not msg.tool_calls:
                    return msg.content or ""

                full_messages.append({
                    "role": "assistant",
                    "content": msg.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            },
                        }
                        for tc in msg.tool_calls
                    ],
                })

                for tc in msg.tool_calls:
                    tool_result = await self._execute_tool_call(tc)
                    full_messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": tool_result,
                    })

            response = await self.client.chat.completions.create(
                model=self.model, messages=full_messages,
                temperature=0.7, max_tokens=2000,
            )
            return response.choices[0].message.content or ""

        except Exception as e:
            return f"抱歉，AI服务暂时不可用，请稍后再试。（错误: {str(e)}）"

    async def chat_stream(self, messages: list[dict], profile_summary: str = "",
                          recommendation_summary: str = "", skill_id: str = "default",
                          max_tool_rounds: int = 5):
        skill = SkillRegistry.get(skill_id) or SkillRegistry.get("default")
        system = skill.render_system_prompt(profile_summary, recommendation_summary)
        full_messages = [{"role": "system", "content": system}] + messages

        try:
            for _ in range(max_tool_rounds):
                response = await self.client.chat.completions.create(
                    model=self.model, messages=full_messages, tools=TOOLS,
                    temperature=0.7, max_tokens=2000,
                )
                choice = response.choices[0]
                msg = choice.message

                if choice.finish_reason == "stop" or not msg.tool_calls:
                    break

                full_messages.append({
                    "role": "assistant",
                    "content": msg.content,
                    "tool_calls": [
                        {"id": tc.id, "type": "function",
                         "function": {"name": tc.function.name,
                                      "arguments": tc.function.arguments}}
                        for tc in msg.tool_calls
                    ],
                })
                for tc in msg.tool_calls:
                    tool_result = await self._execute_tool_call(tc)
                    full_messages.append({
                        "role": "tool", "tool_call_id": tc.id, "content": tool_result,
                    })
            else:
                yield "抱歉，工具调用轮数超出限制。"
                return

            stream = await self.client.chat.completions.create(
                model=self.model, messages=full_messages,
                temperature=0.7, max_tokens=2000, stream=True,
            )
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception:
            yield "抱歉，AI服务暂时不可用，请稍后再试。"
