"""Skill 注册表 - 管理和获取可用的对话风格"""

from typing import Optional
from app.skills.base import Skill
from app.skills.skill_default import DEFAULT_SKILL
from app.skills.skill_zhangxuefeng import ZHANGXUEFENG_SKILL


class SkillRegistry:
    """Skill 注册表，管理所有可用的对话风格"""

    _skills: dict[str, Skill] = {
        "default": DEFAULT_SKILL,
        "zhangxuefeng": ZHANGXUEFENG_SKILL,
    }

    @classmethod
    def get(cls, skill_id: str) -> Optional[Skill]:
        """根据 ID 获取 Skill"""
        return cls._skills.get(skill_id)

    @classmethod
    def list(cls) -> list[dict]:
        """列出所有可用的 Skill"""
        return [
            {
                "id": skill.id,
                "name": skill.name,
                "description": skill.description,
                "emotion_tiers": skill.emotion_tiers,
            }
            for skill in cls._skills.values()
        ]

    @classmethod
    def register(cls, skill: Skill) -> None:
        """注册新的 Skill"""
        cls._skills[skill.id] = skill
