from enum import Enum


class MembershipTier(str, Enum):
    free = "free"
    standard = "standard"
    deep = "deep"
    vip = "vip"