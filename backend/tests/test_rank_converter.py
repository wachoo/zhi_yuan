from app.services.rank_converter import RankConverter


class TestRankConverter:
    def setup_method(self):
        self.converter = RankConverter()

    def test_basic_conversion_same_plan_count(self):
        """招生计划数相同时，位次不变"""
        result = self.converter.convert(
            current_rank=5000,
            current_year_plan=10000,
            target_year_plan=10000,
        )
        assert result == 5000

    def test_conversion_plan_increased(self):
        """招生计划增加时，等效位次放大"""
        result = self.converter.convert(
            current_rank=5000,
            current_year_plan=10000,
            target_year_plan=12000,
        )
        assert result == 6000

    def test_conversion_plan_decreased(self):
        """招生计划减少时，等效位次缩小"""
        result = self.converter.convert(
            current_rank=6000,
            current_year_plan=12000,
            target_year_plan=10000,
        )
        assert result == 5000

    def test_batch_conversion_multiple_years(self):
        """批量换算到多个历史年份"""
        history = [
            {"year": 2025, "plan_count": 11000},
            {"year": 2024, "plan_count": 10500},
            {"year": 2023, "plan_count": 10000},
        ]
        results = self.converter.batch_convert(
            current_rank=5000,
            current_year_plan=10000,
            history=history,
        )
        assert len(results) == 3
        assert results[0]["year"] == 2025
        assert results[0]["equivalent_rank"] == 5500
        assert results[1]["year"] == 2024
        assert results[1]["equivalent_rank"] == 5250
        assert results[2]["year"] == 2023
        assert results[2]["equivalent_rank"] == 5000

    def test_conversion_with_score_line_adjustment(self):
        """考虑批次线变化的修正"""
        result = self.converter.convert(
            current_rank=5000,
            current_year_plan=10000,
            target_year_plan=10000,
            current_batch_line=520,
            target_batch_line=530,
            score=600,
        )
        assert result > 5000

    def test_conversion_rank_zero_returns_zero(self):
        """位次为0的边界情况"""
        result = self.converter.convert(
            current_rank=0,
            current_year_plan=10000,
            target_year_plan=10000,
        )
        assert result == 0