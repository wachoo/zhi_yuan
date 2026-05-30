import uuid
from pydantic import BaseModel


class UniversityOut(BaseModel):
    id: uuid.UUID
    name: str
    province: str
    city: str
    level: str | None
    type: str | None
    tags: list[str]
    tuition_min: int | None
    tuition_max: int | None
    website: str | None
    logo_url: str | None
    description: str | None = None

    class Config:
        from_attributes = True


class PaginatedUniversityOut(BaseModel):
    items: list[UniversityOut]
    total: int
    page: int
    page_size: int
