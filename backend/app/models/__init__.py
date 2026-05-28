from app.models.university import University
from app.models.major import Major, UniversityMajor
from app.models.admission import AdmissionRecord, ScoreSegment
from app.models.user import User, UserProfile
from app.models.recommendation import Recommendation, ChatMessage

__all__ = [
    "University", "Major", "UniversityMajor",
    "AdmissionRecord", "ScoreSegment",
    "User", "UserProfile",
    "Recommendation", "ChatMessage",
]