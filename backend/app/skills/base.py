"""Skill 基类 - 定义顾问的能力模块"""

from dataclasses import dataclass, field


@dataclass
class Skill:
    """
    顾问的能力模块。

    Attributes:
        id: 唯一标识符（如 "base", "career_analysis"）
        name: 显示名称（如 "基础对话", "就业分析"）
        description: 简短描述
        prompt_style: 提示词风格覆盖/增强（可选）
        data_access: 可访问的数据范围（如 ["profile", "university", "admission"]）
        tools: 可用工具列表（如 ["query_university", "query_admission_score"]）
    """

    id: str
    name: str
    description: str
    prompt_style: str | None = None
    data_access: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)
