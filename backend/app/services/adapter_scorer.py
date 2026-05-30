class AdapterScorer:
    """六维适配度评分器"""

    DEFAULT_WEIGHTS = {
        "basic": 0.30,
        "family": 0.10,
        "city": 0.15,
        "personality": 0.25,
        "ability": 0.10,
        "values": 0.10,
    }

    def score(self, profile: dict, record: dict) -> dict:
        dimensions = {}
        dimensions["basic"] = self._score_basic(profile, record)
        dimensions["family"] = self._score_family(profile, record)
        dimensions["city"] = self._score_city(profile, record)
        dimensions["personality"] = self._score_personality(profile, record)
        dimensions["ability"] = self._score_ability(profile, record)
        dimensions["values"] = self._score_values(profile, record)

        weights = self._compute_weights(profile)
        total = sum(dimensions[k] * weights[k] for k in dimensions)
        total = min(100, max(0, round(total, 1)))

        return {
            "total": total,
            "dimensions": {k: round(v, 1) for k, v in dimensions.items()},
            "weights": weights,
        }

    def _score_basic(self, profile: dict, record: dict) -> float:
        basic = profile.get("basic_info", {})
        rank = basic.get("rank", 0)
        min_rank = record.get("min_rank", 0)
        if rank == 0 or min_rank == 0:
            return 50.0
        ratio = min_rank / rank
        if 0.95 <= ratio <= 1.2:
            return 90.0
        elif 0.7 <= ratio < 0.95:
            return 70.0
        elif 1.2 < ratio <= 2.0:
            return 85.0
        else:
            return 30.0

    def _score_family(self, profile: dict, record: dict) -> float:
        family = profile.get("family_info")
        if not family:
            return 0.0
        score = 50.0
        tuition_max = family.get("tuition_max")
        record_tuition = record.get("tuition_max", 0)
        if tuition_max and record_tuition:
            if record_tuition <= tuition_max:
                score += 25.0
            else:
                score -= 25.0
        return min(100, max(0, score))

    def _score_city(self, profile: dict, record: dict) -> float:
        family = profile.get("family_info")
        if not family:
            return 0.0
        prefer_cities = family.get("prefer_city", [])
        if not prefer_cities:
            return 50.0
        record_city = record.get("city", "")
        uni_province = record.get("university_province", "")
        if not record_city and not uni_province:
            return 50.0
        if record_city in prefer_cities or uni_province in prefer_cities:
            return 100.0
        return 20.0

    def _score_personality(self, profile: dict, record: dict) -> float:
        personality = profile.get("personality")
        if not personality:
            return 0.0
        score = 50.0
        interests = personality.get("interests", [])
        major_name = record.get("major_name", "")
        if interests and major_name:
            match_count = sum(1 for i in interests if i in major_name or major_name in i)
            score += match_count * 25.0
        dislikes = personality.get("dislikes", [])
        if dislikes and major_name:
            dislike_count = sum(1 for d in dislikes if d in major_name or major_name in d)
            score -= dislike_count * 30.0
        return min(100, max(0, score))

    def _score_ability(self, profile: dict, record: dict) -> float:
        ability = profile.get("ability")
        if not ability:
            return 0.0
        score = 50.0
        strong_subjects = ability.get("strong_subjects", [])
        major_name = record.get("major_name", "")
        science_keywords = {"数学": ["计算机", "软件", "电子", "人工智能", "自动化", "数学"],
                            "物理": ["计算机", "电子", "土木", "机械", "自动化", "物理"]}
        for subj in strong_subjects:
            related = science_keywords.get(subj, [])
            if any(kw in major_name for kw in related):
                score += 15.0
        return min(100, max(0, score))

    def _score_values(self, profile: dict, record: dict) -> float:
        values = profile.get("values_info")
        if not values:
            return 0.0
        score = 50.0
        career_values = values.get("career_values", [])
        major_name = record.get("major_name", "")
        if "高薪" in career_values:
            high_salary_keywords = ["计算机", "软件", "人工智能", "金融", "电子"]
            if any(kw in major_name for kw in high_salary_keywords):
                score += 25.0
        if "稳定" in career_values:
            stable_keywords = ["师范", "医学", "法学", "会计"]
            if any(kw in major_name for kw in stable_keywords):
                score += 25.0
        return min(100, max(0, score))

    def _compute_weights(self, profile: dict) -> dict:
        filled = []
        if profile.get("basic_info"):
            filled.append("basic")
        if profile.get("family_info"):
            filled.append("family")
            family = profile["family_info"]
            if family.get("prefer_city"):
                filled.append("city")
        if profile.get("personality"):
            filled.append("personality")
        if profile.get("ability"):
            filled.append("ability")
        if profile.get("values_info"):
            filled.append("values")

        if len(filled) <= 1:
            return {"basic": 1.0, "family": 0.0, "city": 0.0, "personality": 0.0, "ability": 0.0, "values": 0.0}

        raw = {k: self.DEFAULT_WEIGHTS[k] if k in filled else 0.0 for k in self.DEFAULT_WEIGHTS}
        total = sum(raw.values())
        if total == 0:
            return raw
        return {k: round(v / total, 3) for k, v in raw.items()}