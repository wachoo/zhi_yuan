from app.models.enums import MembershipTier


# 厌恶领域 → 相关专业关键词映射（语义扩展）
_DISLIKE_KEYWORDS: dict[str, list[str]] = {
    "绘画": ["美术", "艺术", "绘画", "油画", "国画", "版画", "壁画", "雕塑", "书法"],
    "美术": ["美术", "艺术", "绘画", "油画", "国画", "版画", "壁画", "雕塑", "书法"],
    "体育": ["体育", "运动", "健身"],
    "音乐": ["音乐", "声乐", "器乐", "作曲", "钢琴", "小提琴"],
    "舞蹈": ["舞蹈", "芭蕾"],
    "化学": ["化学", "化工", "材料", "制药"],
    "生物": ["生物", "生态", "环境"],
    "物理": ["物理", "力学"],
    "数学": ["数学", "统计"],
    "编程": ["计算机", "软件", "人工智能", "数据"],
    "医学": ["医学", "临床", "护理", "药学", "中医", "针灸"],
    "法学": ["法学", "法律"],
    "会计": ["会计", "审计", "财务"],
    "教育": ["教育", "师范", "学前"],
    "建筑": ["建筑", "土木", "规划"],
    "农学": ["农学", "农业", "园艺", "植物", "动物"],
}


def _expand_dislikes(dislikes: list[str]) -> list[str]:
    """将用户厌恶项扩展为完整的关键词列表"""
    expanded = set()
    for d in dislikes:
        expanded.add(d)
        for keyword, related in _DISLIKE_KEYWORDS.items():
            if keyword in d or d in keyword:
                expanded.update(related)
    return list(expanded)


class RecommendationEngine:
    """推荐引擎核心：冲/稳/保分类 + 硬性条件过滤"""

    RUSH_RANGE = (0.7, 0.95)
    STABLE_RANGE = (0.95, 1.2)
    SAFE_RANGE = (1.2, 2.0)

    def filter_records(
        self,
        records: list[dict],
        province: str,
        subject_type: str,
        tuition_max: int | None = None,
        levels: list[str] | None = None,
        provinces_exclude: list[str] | None = None,
        dislikes: list[str] | None = None,
        expanded_dislikes: list[str] | None = None,
    ) -> list[dict]:
        filtered = []
        # 使用预扩展的关键词，或动态扩展
        effective_dislikes = expanded_dislikes or (_expand_dislikes(dislikes) if dislikes else None)
        for r in records:
            if r["province"] != province:
                continue
            if r["subject_type"] != subject_type:
                continue
            if tuition_max and r.get("tuition_min", 0) > tuition_max:
                continue
            if levels and r.get("level") not in levels:
                continue
            if provinces_exclude and r.get("university_province") in provinces_exclude:
                continue
            if effective_dislikes:
                major_name = r.get("major_name", "")
                if any(kw in major_name or major_name in kw for kw in effective_dislikes):
                    continue
            filtered.append(r)
        return filtered

    def categorize(self, equivalent_rank: int, records: list[dict]) -> dict:
        if not records:
            return {"rush": [], "stable": [], "safe": []}

        rush, stable, safe = [], [], []

        for r in records:
            min_rank = r["min_rank"]
            if min_rank is None:
                continue

            ratio = min_rank / equivalent_rank if equivalent_rank > 0 else 0
            entry = {**r, "rank_ratio": round(ratio, 3)}

            if self.RUSH_RANGE[0] <= ratio < self.RUSH_RANGE[1]:
                rush.append(entry)
            elif self.STABLE_RANGE[0] <= ratio < self.STABLE_RANGE[1]:
                stable.append(entry)
            elif self.SAFE_RANGE[0] <= ratio < self.SAFE_RANGE[1]:
                safe.append(entry)

        rush.sort(key=lambda x: x["rank_ratio"])
        stable.sort(key=lambda x: x["rank_ratio"])
        safe.sort(key=lambda x: x["rank_ratio"])

        return {"rush": rush, "stable": stable, "safe": safe}

    def limit_for_tier(self, result: dict, tier: str | MembershipTier = MembershipTier.free,
                       max_per_group: int = 1) -> dict:
        if tier == MembershipTier.free:
            return {
                "rush": result["rush"][:max_per_group],
                "stable": result["stable"][:max_per_group],
                "safe": result["safe"][:max_per_group],
            }
        return result