import uuid
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.enums import MembershipTier


class UserRegister(BaseModel):
    phone: str = Field(..., pattern=r"^1[3-9]\d{9}$")
    password: str = Field(..., min_length=6, max_length=32)


class UserLogin(BaseModel):
    phone: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: uuid.UUID


class UserInfo(BaseModel):
    id: uuid.UUID
    phone: str
    nickname: str | None
    membership_tier: MembershipTier
    created_at: datetime

    class Config:
        from_attributes = True


class ProfileBasicInfo(BaseModel):
    score: int = Field(..., ge=0, le=750)
    rank: int = Field(..., ge=0)
    province: str
    subject_type: str
    exam_type: str | None = None


class ProfileFamilyInfo(BaseModel):
    income_range: str | None = None
    tuition_max: int | None = None
    prefer_city: list[str] | None = None
    parent_industry: str | None = None


class ProfilePersonality(BaseModel):
    interests: list[str] | None = None
    dislikes: list[str] | None = None
    holland_code: str | None = None
    mbti: str | None = None
    introvert_extrovert: str | None = None


class ProfileAbility(BaseModel):
    strong_subjects: list[str] | None = None
    social_ability: int | None = Field(None, ge=1, le=5)
    english_level: int | None = Field(None, ge=1, le=6)
    awards: list[str] | None = None


class ProfileValues(BaseModel):
    career_values: list[str] | None = None
    distance_preference: str | None = None
    plan: str | None = None
    industry_preference: list[str] | None = None


class ProfileUpdate(BaseModel):
    basic_info: ProfileBasicInfo | None = None
    family_info: ProfileFamilyInfo | None = None
    personality: ProfilePersonality | None = None
    ability: ProfileAbility | None = None
    values_info: ProfileValues | None = None
