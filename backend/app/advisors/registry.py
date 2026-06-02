"""Advisor 注册表 - 管理和获取可用的 AI 顾问"""

from typing import Optional
from app.advisors.base import Advisor
from app.advisors.advisor_default import DEFAULT_ADVISOR
from app.advisors.advisor_zhangxuefeng import ZHANGXUEFENG_ADVISOR


class AdvisorRegistry:
    """Advisor 注册表，管理所有可用的 AI 顾问"""

    _advisors: dict[str, Advisor] = {
        "default": DEFAULT_ADVISOR,
        "zhangxuefeng": ZHANGXUEFENG_ADVISOR,
    }

    @classmethod
    def get(cls, advisor_id: str) -> Optional[Advisor]:
        """根据 ID 获取 Advisor"""
        return cls._advisors.get(advisor_id)

    @classmethod
    def list(cls) -> list[dict]:
        """列出所有可用的 Advisor"""
        return [
            {
                "id": advisor.id,
                "name": advisor.name,
                "description": advisor.description,
                "emotion_tiers": advisor.emotion_tiers,
                "skills": [
                    {
                        "id": skill.id,
                        "name": skill.name,
                        "description": skill.description,
                    }
                    for skill in advisor.skills
                ],
            }
            for advisor in cls._advisors.values()
        ]

    @classmethod
    def register(cls, advisor: Advisor) -> None:
        """注册新的 Advisor"""
        cls._advisors[advisor.id] = advisor
