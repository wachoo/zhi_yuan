"""Skill 基类 - 定义对话风格模块的协议"""

from dataclasses import dataclass, field


@dataclass
class Skill:
    """
    对话风格 Skill 的基类。

    Attributes:
        id: 唯一标识符，用于 API 传参（如 "default", "zhangxuefeng"）
        name: 显示名称（如 "默认顾问", "张雪峰视角"）
        description: 简短描述，用于前端展示
        system_prompt_template: System Prompt 模板，接受 {profile_summary} 和 {recommendation_summary} 占位符
        tools_description: 工具描述列表（可选覆盖默认值）
        emotion_tiers: 情绪档位定义（可选）
    """

    id: str
    name: str
    description: str
    system_prompt_template: str
    tools_description: list[dict] = field(default_factory=list)
    emotion_tiers: list[dict] = field(default_factory=list)

    def render_system_prompt(
        self,
        profile_summary: str = "",
        recommendation_summary: str = "",
    ) -> str:
        """渲染 System Prompt，填充用户画像和推荐结果"""
        return self.system_prompt_template.format(
            profile_summary=profile_summary or "用户尚未填写个人画像",
            recommendation_summary=recommendation_summary or "暂无推荐结果",
        )
