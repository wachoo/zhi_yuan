from app.models.university import University
from app.models.major import Major, UniversityMajor
from app.models.admission import AdmissionRecord, ScoreSegment
from app.models.user import User, UserProfile
from app.models.recommendation import Recommendation, ChatMessage
from app.models.chat_session import ChatSession
from app.models.order import Order

__all__ = [
    "University", "Major", "UniversityMajor",
    "AdmissionRecord", "ScoreSegment",
    "User", "UserProfile",
    "Recommendation", "ChatMessage",
    "ChatSession",
    "Order",
]
