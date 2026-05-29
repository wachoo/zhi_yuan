import json

from openai import AsyncOpenAI

from app.config import get_settings
from app.services.university_service import UniversityService
from app.services.major_service import MajorService

settings = get_settings()

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
        config = LLM_CONFIGS.get(provider, LLM_CONFIGS["qwen"])
        self.client = AsyncOpenAI(api_key=config["api_key"], base_url=config["base_url"])
        self.model = config["model"]
        self._tool_handlers = {
            "query_university": self._query_university,
            "query_major": self._query_major,
        }

    # ── Tool handlers ──────────────────────────────────────────

    async def _query_university(self, name: str, province: str | None = None) -> dict:
        return await UniversityService().search_universities(name, province)

    async def _query_major(self, name: str) -> dict:
        return await MajorService().search_majors(name)

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

    # ── Chat ───────────────────────────────────────────────────

    async def chat(
        self,
        messages: list[dict],
        profile_summary: str = "",
        recommendation_summary: str = "",
        max_tool_rounds: int = 5,
    ) -> str:
        system = SYSTEM_PROMPT.format(
            profile_summary=profile_summary or "用户尚未填写个人画像",
            recommendation_summary=recommendation_summary or "暂无推荐结果",
        )
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

                # 如果 LLM 直接返回文本内容（无工具调用），直接返回
                if choice.finish_reason == "stop" or not msg.tool_calls:
                    return msg.content or ""

                # LLM 要求调用工具：把 assistant 消息（含 tool_calls）加入对话
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

                # 执行每个工具调用，把结果作为 tool message 返回
                for tc in msg.tool_calls:
                    tool_result = await self._execute_tool_call(tc)
                    full_messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": tool_result,
                    })

            # 超过最大轮数，强制不带 tools 调用一次
            response = await self.client.chat.completions.create(
                model=self.model, messages=full_messages,
                temperature=0.7, max_tokens=2000,
            )
            return response.choices[0].message.content or ""

        except Exception as e:
            return f"抱歉，AI服务暂时不可用，请稍后再试。（错误: {str(e)}）"

    async def chat_stream(self, messages: list[dict], profile_summary: str = "",
                          recommendation_summary: str = "", max_tool_rounds: int = 5):
        system = SYSTEM_PROMPT.format(
            profile_summary=profile_summary or "用户尚未填写个人画像",
            recommendation_summary=recommendation_summary or "暂无推荐结果",
        )
        full_messages = [{"role": "system", "content": system}] + messages

        try:
            # 工具调用阶段：非流式处理，直到获得最终文本回复
            for _ in range(max_tool_rounds):
                response = await self.client.chat.completions.create(
                    model=self.model, messages=full_messages, tools=TOOLS,
                    temperature=0.7, max_tokens=2000,
                )
                choice = response.choices[0]
                msg = choice.message

                if choice.finish_reason == "stop" or not msg.tool_calls:
                    # 无工具调用，进入流式输出
                    break

                # 处理工具调用（非流式）
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

            # 最终回复：流式输出
            stream = await self.client.chat.completions.create(
                model=self.model, messages=full_messages,
                temperature=0.7, max_tokens=2000, stream=True,
            )
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception:
            yield "抱歉，AI服务暂时不可用，请稍后再试。"
