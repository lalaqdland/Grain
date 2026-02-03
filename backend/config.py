import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置类"""
    
    # API配置
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True
    
    # DeepSeek API配置
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com/v1"
    deepseek_model: str = "deepseek-chat"
    
    # CORS配置
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    
    # 文件上传配置
    max_upload_size: int = 10485760  # 10MB
    allowed_extensions: str = ".docx"
    
    # 临时文件存储路径
    temp_storage_path: str = "../storage/temp"
    
    # MarianMT配置
    use_marian_mt: bool = False
    marian_model_path: str = "Helsinki-NLP/opus-mt-en-de"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()

