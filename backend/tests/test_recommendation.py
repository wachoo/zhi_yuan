from app.services.recommendation_engine import RecommendationEngine


class TestRecommendationEngine:
    def setup_method(self):
        self.engine = RecommendationEngine()

    def _make_record(self, uni_name: str, major_name: str, min_rank: int,
                     year: int = 2025, province: str = "浙江",
                     subject_type: str = "综合改革",
                     tuition_min: int = 5000, tuition_max: int = 8000,
                     level: str = "985"):
        return {
            "university_name": uni_name,
            "major_name": major_name,
            "min_rank": min_rank,
            "year": year,
            "province": province,
            "subject_type": subject_type,
            "tuition_min": tuition_min,
            "tuition_max": tuition_max,
            "level": level,
        }

    def test_categorize_rush_stable_safe(self):
        """位次5000的考生，冲/稳/保分类正确"""
        records = [
            self._make_record("A大学", "计算机", 4000),
            self._make_record("B大学", "计算机", 4500),
            self._make_record("C大学", "计算机", 5200),
            self._make_record("D大学", "计算机", 5800),
            self._make_record("E大学", "计算机", 7000),
            self._make_record("F大学", "计算机", 8000),
        ]
        result = self.engine.categorize(equivalent_rank=5000, records=records)
        assert len(result["rush"]) == 2
        assert len(result["stable"]) == 2
        assert len(result["safe"]) == 2
        assert result["rush"][0]["university_name"] == "A大学"
        assert result["safe"][-1]["university_name"] == "F大学"

    def test_filter_by_province(self):
        records = [
            self._make_record("A大学", "计算机", 5000, province="浙江"),
            self._make_record("B大学", "计算机", 5000, province="北京"),
        ]
        filtered = self.engine.filter_records(
            records=records, province="浙江", subject_type="综合改革",
        )
        assert len(filtered) == 1

    def test_filter_by_tuition(self):
        records = [
            self._make_record("A大学", "计算机", 5000, tuition_max=6000),
            self._make_record("B大学", "计算机", 5000, tuition_min=30000, tuition_max=50000),
        ]
        filtered = self.engine.filter_records(
            records=records, province="浙江", subject_type="综合改革", tuition_max=10000,
        )
        assert len(filtered) == 1
        assert filtered[0]["university_name"] == "A大学"

    def test_empty_records_returns_empty(self):
        result = self.engine.categorize(equivalent_rank=5000, records=[])
        assert result == {"rush": [], "stable": [], "safe": []}

    def test_free_tier_limits_to_three(self):
        # 3 categories, 10 records each, equivalent_rank=5000
        records = []
        records += [self._make_record(f"冲大学{i}", "计算机", 4000 + i) for i in range(10)]   # rush: 0.8-0.802
        records += [self._make_record(f"稳大学{i}", "计算机", 5000 + i) for i in range(10)]   # stable: 1.0-1.002
        records += [self._make_record(f"保大学{i}", "计算机", 6200 + i) for i in range(10)]   # safe: 1.24-1.242
        result = self.engine.categorize(equivalent_rank=5000, records=records)
        free_result = self.engine.limit_for_tier(result, tier="free", max_per_group=1)
        total = len(free_result["rush"]) + len(free_result["stable"]) + len(free_result["safe"])
        assert total == 3