from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    description="智愿 - LLM高考志愿填报助手API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": settings.APP_NAME}


from app.api.auth import router as auth_router
from app.api.profile import router as profile_router
from app.api.universities import router as universities_router
from app.api.recommend import router as recommend_router
from app.api.chat import router as chat_router

app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(universities_router)
app.include_router(recommend_router)
app.include_router(chat_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)