from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import get_settings
from app.api.v1 import upload, rewrite, export

# 获取配置
settings = get_settings()

# 创建FastAPI应用
app = FastAPI(
    title="Grain API",
    description="The AI Humanizer & Academic Shield - 守拙",
    version="3.1.2",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS
origins = settings.cors_origins.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(upload.router, prefix="/api/v1", tags=["upload"])
app.include_router(rewrite.router, prefix="/api/v1", tags=["rewrite"])
app.include_router(export.router, prefix="/api/v1", tags=["export"])


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "Welcome to Grain API",
        "version": "3.1.2",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "Grain API",
        "version": "3.1.2"
    }


@app.get("/api/v1/info")
async def api_info():
    """API信息端点"""
    return {
        "api_version": "v1",
        "features": {
            "plagiarism_fix": True,
            "ai_detection_fix": True,
            "format_preservation": True,
            "sentence_rewrite": True,
            "marian_optional": settings.use_marian_mt,
        },
        "supported_formats": [".docx"],
        "max_file_size": f"{settings.max_upload_size / 1024 / 1024}MB"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload
    )

