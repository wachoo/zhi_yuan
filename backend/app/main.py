from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import get_settings

settings = get_settings()

_CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app = FastAPI(
    title=settings.APP_NAME,
    description="智愿 - LLM高考志愿填报助手API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载 PPT 静态文件
_ppt_dir = Path(__file__).resolve().parent.parent.parent / "ppt"
if _ppt_dir.is_dir():
    app.mount("/ppt", StaticFiles(directory=_ppt_dir, html=True), name="ppt")


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # Unhandled 500s otherwise omit CORS headers; the browser reports that as a CORS failure.
    detail = str(exc) if settings.DEBUG else "Internal server error"
    return JSONResponse(status_code=500, content={"detail": detail})


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