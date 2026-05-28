class RankConverter:
    """位次等效换算器

    核心公式：等效位次 = 当年位次 × (目标年计划数 / 当年计划数)
    批次线修正：当批次线变化较大时，叠加线性修正因子
    """

    def convert(
        self,
        current_rank: int,
        current_year_plan: int,
        target_year_plan: int,
        current_batch_line: int | None = None,
        target_batch_line: int | None = None,
        score: int | None = None,
    ) -> int:
        if current_rank == 0:
            return 0

        # 基础换算
        ratio = target_year_plan / current_year_plan
        equivalent = current_rank * ratio

        # 批次线修正
        if (current_batch_line and target_batch_line and score
                and current_batch_line != target_batch_line):
            line_diff = target_batch_line - current_batch_line
            adjustment = 1 + (line_diff / 10) * 0.03
            equivalent *= adjustment

        return round(equivalent)

    def batch_convert(
        self,
        current_rank: int,
        current_year_plan: int,
        history: list[dict],
    ) -> list[dict]:
        results = []
        for item in history:
            eq_rank = self.convert(
                current_rank=current_rank,
                current_year_plan=current_year_plan,
                target_year_plan=item["plan_count"],
            )
            results.append({
                "year": item["year"],
                "equivalent_rank": eq_rank,
                "plan_count": item["plan_count"],
            })
        return results