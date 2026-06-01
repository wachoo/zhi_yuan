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
        """完整六维画像，所有维度都有分数"""
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
        assert score["dimensions"]["city"] > 0
        assert score["dimensions"]["personality"] > 0
        assert score["dimensions"]["ability"] > 0
        assert score["dimensions"]["values"] > 0

    def test_city_match_boosts_city_score(self):
        profile = {
            "basic_info": {"score": 620, "rank": 5000, "province": "浙江", "subject_type": "综合改革"},
            "family_info": {"prefer_city": ["上海"]},
        }
        record_match = {"university_name": "A", "major_name": "CS", "min_rank": 5000, "city": "上海"}
        record_miss = {"university_name": "B", "major_name": "CS", "min_rank": 5000, "city": "哈尔滨"}
        score_match = self.scorer.score(profile=profile, record=record_match)
        score_miss = self.scorer.score(profile=profile, record=record_miss)
        assert score_match["dimensions"]["city"] > score_miss["dimensions"]["city"]
        assert score_match["total"] > score_miss["total"]

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


class TestGenerateReason:
    def setup_method(self):
        self.scorer = AdapterScorer()

    def test_reason_with_city_match(self):
        """城市匹配时应生成城市相关理由"""
        profile = {
            "basic_info": {"score": 620, "rank": 5000, "province": "浙江", "subject_type": "综合改革"},
            "family_info": {"prefer_city": ["上海"], "tuition_max": 10000},
        }
        record = {"university_name": "A大学", "major_name": "计算机", "min_rank": 5000, "city": "上海", "tuition_max": 6000}
        score_result = self.scorer.score(profile=profile, record=record)
        reason = self.scorer.generate_reason(profile=profile, record=record, score_result=score_result)
        assert "上海" in reason

    def test_reason_with_interest_match(self):
        """兴趣匹配时应生成兴趣相关理由"""
        profile = {
            "basic_info": {"score": 620, "rank": 5000, "province": "浙江", "subject_type": "综合改革"},
            "personality": {"interests": ["计算机"]},
        }
        record = {"university_name": "A大学", "major_name": "计算机科学与技术", "min_rank": 5000}
        score_result = self.scorer.score(profile=profile, record=record)
        reason = self.scorer.generate_reason(profile=profile, record=record, score_result=score_result)
        assert "计算机" in reason

    def test_reason_with_values_match(self):
        """职业价值观匹配时应生成相关理由"""
        profile = {
            "basic_info": {"score": 620, "rank": 5000, "province": "浙江", "subject_type": "综合改革"},
            "values_info": {"career_values": ["高薪"]},
        }
        record = {"university_name": "A大学", "major_name": "计算机科学", "min_rank": 5000}
        score_result = self.scorer.score(profile=profile, record=record)
        reason = self.scorer.generate_reason(profile=profile, record=record, score_result=score_result)
        assert "高薪" in reason

    def test_reason_fallback_when_no_profile(self):
        """无画像信息时应返回兜底理由"""
        profile = {"basic_info": {"rank": 5000}}
        record = {"university_name": "A大学", "major_name": "计算机", "min_rank": 5000}
        score_result = self.scorer.score(profile=profile, record=record)
        reason = self.scorer.generate_reason(profile=profile, record=record, score_result=score_result)
        assert isinstance(reason, str)
        assert len(reason) > 0

    def test_reason_with_ability_match(self):
        """学科优势匹配时应生成相关理由"""
        profile = {
            "basic_info": {"score": 620, "rank": 5000, "province": "浙江", "subject_type": "综合改革"},
            "ability": {"strong_subjects": ["数学", "物理"]},
        }
        record = {"university_name": "A大学", "major_name": "计算机科学", "min_rank": 5000}
        score_result = self.scorer.score(profile=profile, record=record)
        reason = self.scorer.generate_reason(profile=profile, record=record, score_result=score_result)
        assert "数学" in reason or "物理" in reason

    def test_family_tuition_affordability(self):
        """学费在承受范围内时 family 分数提升"""
        profile = {
            "basic_info": {"score": 620, "rank": 5000, "province": "浙江", "subject_type": "综合改革"},
            "family_info": {"tuition_max": 10000},
        }
        record_cheap = {"university_name": "A", "major_name": "CS", "min_rank": 5000, "tuition_max": 6000}
        record_expensive = {"university_name": "B", "major_name": "CS", "min_rank": 5000, "tuition_max": 20000}
        score_cheap = self.scorer.score(profile=profile, record=record_cheap)
        score_expensive = self.scorer.score(profile=profile, record=record_expensive)
        assert score_cheap["dimensions"]["family"] > score_expensive["dimensions"]["family"]

    def test_family_elderly_care_prefers_nearby(self):
        """有赡养负担时，家乡省份院校 family 分高于远距离"""
        profile = {
            "basic_info": {"score": 620, "rank": 5000, "province": "浙江", "subject_type": "综合改革"},
            "family_info": {"home_province": "浙江", "has_elderly_care": True},
        }
        record_near = {"university_name": "A", "major_name": "CS", "min_rank": 5000, "university_province": "浙江"}
        record_far = {"university_name": "B", "major_name": "CS", "min_rank": 5000, "university_province": "黑龙江"}
        score_near = self.scorer.score(profile=profile, record=record_near)
        score_far = self.scorer.score(profile=profile, record=record_far)
        assert score_near["dimensions"]["family"] > score_far["dimensions"]["family"]

    def test_city_home_province_proximity(self):
        """无偏好城市时，家乡省份院校 city 分更高"""
        profile = {
            "basic_info": {"score": 620, "rank": 5000, "province": "浙江", "subject_type": "综合改革"},
            "family_info": {"home_province": "浙江"},
        }
        record_home = {"university_name": "A", "major_name": "CS", "min_rank": 5000, "university_province": "浙江"}
        record_far = {"university_name": "B", "major_name": "CS", "min_rank": 5000, "university_province": "新疆"}
        score_home = self.scorer.score(profile=profile, record=record_home)
        score_far = self.scorer.score(profile=profile, record=record_far)
        assert score_home["dimensions"]["city"] > score_far["dimensions"]["city"]

    def test_family_reason_includes_home_province(self):
        """推荐理由应包含家乡相关信息"""
        profile = {
            "basic_info": {"score": 620, "rank": 5000, "province": "浙江", "subject_type": "综合改革"},
            "family_info": {"home_province": "浙江", "tuition_max": 10000},
        }
        record = {"university_name": "A大学", "major_name": "计算机", "min_rank": 5000,
                  "university_province": "浙江", "tuition_max": 6000}
        score_result = self.scorer.score(profile=profile, record=record)
        reason = self.scorer.generate_reason(profile=profile, record=record, score_result=score_result)
        assert "家乡" in reason or "学费" in reason
