from app.models.enums import MembershipTier


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
    ) -> list[dict]:
        filtered = []
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