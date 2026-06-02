"""
Advisor 系统 - AI 顾问实体管理

每个 Advisor 定义：
- 人格和名称（name, description）
- System Prompt（system_prompt_template）
- 情绪档位（emotion_tiers，可选）
- 能力模块（skills: list[Skill]）

通过 AdvisorRegistry 注册和获取，ChatService 根据用户选择动态加载。
"""

from app.advisors.base import Advisor
from app.advisors.registry import AdvisorRegistry

__all__ = ["Advisor", "AdvisorRegistry"]
