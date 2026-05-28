from openai import AsyncOpenAI
from app.config import get_settings

settings = get_settings()

LLM_CONFIGS = {
    "deepseek": {
        "api_key": settings.DEEPSEEK_API_KEY,
        "base_url": settings.DEEPSEEK_BASE_URL,
        "model": "deepseek-chat",
    },
    "qwen": {
        "api_key": settings.QWEN_API_KEY,
        "base_url": settings.QWEN_BASE_URL,
        "model": "qwen-plus",
    },
}

SYSTEM_PROMPT = """你是"智愿"的AI高考志愿顾问。你的职责是帮助考生和家长理解高考志愿填报的相关知识，并基于考生的个人情况给出个性化建议。

重要规则：
1. 所有分数线、录取概率等数据必须来自工具调用返回的结果，绝对不能编造数据
2. 如果工具返回的数据不足以回答问题，请如实告知用户
3. 每次回答末尾适当提醒"以上信息仅供参考，建议结合多方信息综合决策"
4. 保持专业、耐心、客观的语气
5. 不要推荐具体的培训机构或付费服务

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
            "description": "查询院校详细信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "院校名称"},
                    "province": {"type": "string", "description": "考生所在省份"},
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "query_major",
            "description": "查询专业详细信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "专业名称"},
                },
                "required": ["name"],
            },
        },
    },
]


class LLMService:
    def __init__(self, provider: str = "deepseek"):
        config = LLM_CONFIGS.get(provider, LLM_CONFIGS["deepseek"])
        self.client = AsyncOpenAI(api_key=config["api_key"], base_url=config["base_url"])
        self.model = config["model"]

    async def chat(
        self,
        messages: list[dict],
        profile_summary: str = "",
        recommendation_summary: str = "",
    ) -> str:
        system = SYSTEM_PROMPT.format(
            profile_summary=profile_summary or "用户尚未填写个人画像",
            recommendation_summary=recommendation_summary or "暂无推荐结果",
        )
        full_messages = [{"role": "system", "content": system}] + messages
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                tools=TOOLS,
                temperature=0.7,
                max_tokens=2000,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"抱歉，AI服务暂时不可用，请稍后再试。（错误: {str(e)}）"

    async def chat_stream(self, messages: list[dict], profile_summary: str = "",
                          recommendation_summary: str = ""):
        system = SYSTEM_PROMPT.format(
            profile_summary=profile_summary or "用户尚未填写个人画像",
            recommendation_summary=recommendation_summary or "暂无推荐结果",
        )
        full_messages = [{"role": "system", "content": system}] + messages
        try:
            stream = await self.client.chat.completions.create(
                model=self.model, messages=full_messages, tools=TOOLS,
                temperature=0.7, max_tokens=2000, stream=True,
            )
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception:
            yield "抱歉，AI服务暂时不可用，请稍后再试。"
