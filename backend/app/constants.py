from enum import Enum


class SubjectType(str, Enum):
    """科类枚举"""
    PHYSICS = "物理类"
    HISTORY = "历史类"
    COMPREHENSIVE_REFORM = "综合改革"


class ExamType(str, Enum):
    """考试科类枚举"""
    NORMAL = "普通类"
    ART = "艺术类"
    SPORTS = "体育类"
