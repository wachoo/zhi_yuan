from app.services.adapter_scorer import AdapterScorer


class TestAdapterScorer:
    def setup_method(self):
        self.scorer = AdapterScorer()

    def test_basic_only_profile(self):
        """仅基础信息时，只有基础匹配分"""
        profile = {
            "basic_info": {"score": 620, "rank": 5000, "province": "浙江", "subject_type": "综合改革"},
        }
        record = {"university_name": "A大学", "major_name": "计算机", "min_rank": 5200}
        score = self.scorer.score(profile=profile, record=record)
        assert 0 <= score["total"] <= 100
        assert score["dimensions"]["basic"] > 0
        assert score["dimensions"]["family"] == 0
        assert score["dimensions"]["personality"] == 0

    def test_full_profile_all_dimensions(self):
        """完整五维画像，所有维度都有分数"""
        profile = {
            "basic_info": {"score": 620, "rank": 5000, "province": "浙江", "subject_type": "综合改革"},
            "family_info": {"income_range": "20-50万", "tuition_max": 10000, "prefer_city": ["上海", "杭州"]},
            "personality": {"interests": ["计算机", "编程"], "holland_code": "IR"},
            "ability": {"strong_subjects": ["数学", "物理"], "english_level": 4},
            "values_info": {"career_values": ["高薪"], "distance_preference": "接受外地", "plan": "直接就业"},
        }
        record = {
            "university_name": "A大学",
            "major_name": "计算机科学与技术",
            "min_rank": 5200,
            "city": "上海",
            "tuition_max": 6000,
            "career_directions": ["软件工程师", "算法工程师"],
        }
        score = self.scorer.score(profile=profile, record=record)
        assert score["total"] > 0
        assert score["dimensions"]["basic"] > 0
        assert score["dimensions"]["family"] > 0
        assert score["dimensions"]["personality"] > 0
        assert score["dimensions"]["ability"] > 0
        assert score["dimensions"]["values"] > 0

    def test_city_match_boosts_family_score(self):
        profile = {
            "basic_info": {"score": 620, "rank": 5000, "province": "浙江", "subject_type": "综合改革"},
            "family_info": {"prefer_city": ["上海"]},
        }
        record_match = {"university_name": "A", "major_name": "CS", "min_rank": 5000, "city": "上海"}
        record_miss = {"university_name": "B", "major_name": "CS", "min_rank": 5000, "city": "哈尔滨"}
        score_match = self.scorer.score(profile=profile, record=record_match)
        score_miss = self.scorer.score(profile=profile, record=record_miss)
        assert score_match["dimensions"]["family"] > score_miss["dimensions"]["family"]

    def test_interest_match_boosts_personality(self):
        profile = {
            "basic_info": {"score": 620, "rank": 5000, "province": "浙江", "subject_type": "综合改革"},
            "personality": {"interests": ["计算机", "编程"]},
        }
        record_match = {"university_name": "A", "major_name": "计算机科学与技术", "min_rank": 5000}
        record_miss = {"university_name": "B", "major_name": "土木工程", "min_rank": 5000}
        score_match = self.scorer.score(profile=profile, record=record_match)
        score_miss = self.scorer.score(profile=profile, record=record_miss)
        assert score_match["dimensions"]["personality"] > score_miss["dimensions"]["personality"]

    def test_score_range_is_zero_to_hundred(self):
        profile = {
            "basic_info": {"score": 620, "rank": 5000, "province": "浙江", "subject_type": "综合改革"},
            "family_info": {"income_range": "20-50万", "tuition_max": 10000, "prefer_city": ["上海"]},
            "personality": {"interests": ["计算机"], "holland_code": "IR"},
            "ability": {"strong_subjects": ["数学"], "english_level": 4},
            "values_info": {"career_values": ["高薪"], "plan": "直接就业"},
        }
        record = {"university_name": "A", "major_name": "计算机", "min_rank": 5000, "city": "上海",
                  "tuition_max": 6000, "career_directions": ["软件工程师"]}
        score = self.scorer.score(profile=profile, record=record)
        assert 0 <= score["total"] <= 100
    def test_dislike_penalty_reduces_personality_score(self):
        """厌恶领域匹配时降低人格维度得分"""
        profile = {
            "basic_info": {"score": 620, "rank": 5000, "province": "浙江", "subject_type": "综合改革"},
            "personality": {"interests": ["计算机"], "dislikes": ["化学", "生物"]},
        }
        record_match = {"university_name": "A", "major_name": "化学工程", "min_rank": 5000}
        record_miss = {"university_name": "B", "major_name": "土木工程", "min_rank": 5000}
        score_match = self.scorer.score(profile=profile, record=record_match)
        score_miss = self.scorer.score(profile=profile, record=record_miss)
        # 化学工程匹配到"化学"厌恶项，得分应该低于土木工程（无厌恶匹配）
        assert score_match["dimensions"]["personality"] < score_miss["dimensions"]["personality"]

    def test_interest_and_dislike_combined(self):
        """兴趣和厌恶同时存在时，得分合理"""
        profile = {
            "basic_info": {"score": 620, "rank": 5000, "province": "浙江", "subject_type": "综合改革"},
            "personality": {"interests": ["计算机"], "dislikes": ["编程"]},
        }
        record = {"university_name": "A", "major_name": "计算机科学与技术", "min_rank": 5000}
        score = self.scorer.score(profile=profile, record=record)
        # "计算机"匹配major_name(+25), "编程"不匹配"计算机科学与技术"(-0), 基础50, 总计75
        assert score["dimensions"]["personality"] == 75.0
