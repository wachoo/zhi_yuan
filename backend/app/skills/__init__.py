"""
Skill 系统 - 顾问的能力模块定义

每个 Skill 定义：
- 提示词风格（prompt_style，可选覆盖/增强）
- 可访问的数据范围（data_access）
- 可用工具列表（tools）

Skill 是 Advisor 的子模块，一个 Advisor 可以拥有多个 Skill。
"""

from app.skills.base import Skill

__all__ = ["Skill"]
