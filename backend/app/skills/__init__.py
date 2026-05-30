"""
Skill 系统 - 可插拔的对话风格模块

每个 Skill 定义一套独立的：
- System Prompt（人格、表达风格、决策框架）
- 工具描述（可选扩展）
- 情绪档位（可选）

通过 SkillRegistry 注册和获取，ChatService 根据用户选择动态加载。
"""

from app.skills.base import Skill
from app.skills.registry import SkillRegistry

__all__ = ["Skill", "SkillRegistry"]
