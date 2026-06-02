"""Advisor 基类 - 定义 AI 顾问实体"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.skills.base import Skill


@dataclass
class Advisor:
    """
    AI 顾问实体，代表一个具有特定人格和能力的顾问。

    Attributes:
        id: 唯一标识符，用于 API 传参（如 "default", "zhangxuefeng"）
        name: 显示名称（如 "智愿顾问", "名师张"）
        description: 简短描述，用于前端展示
        system_prompt_template: System Prompt 模板，接受 {profile_summary} 和 {recommendation_summary} 占位符
        emotion_tiers: 情绪档位定义（可选）
        skills: 该顾问拥有的能力模块列表
    """

    id: str
    name: str
    description: str
    system_prompt_template: str
    emotion_tiers: list[dict] = field(default_factory=list)
    skills: list["Skill"] = field(default_factory=list)

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
