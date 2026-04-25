from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from pydantic import Field, AliasChoices
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    """应用配置类"""
    
    # API配置
    api_host: str = "0.0.0.0"
    api_port: int = 8001  # 使用8001端口，避免与NeuralNote冲突
    api_reload: bool = True
    
    # DeepSeek API配置
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com/v1"
    deepseek_model: str = "deepseek-chat"
    deepseek_request_timeout: int = 30  # API 请求超时时间（秒）
    deepseek_degradation_enabled: bool = True  # 降级策略开关
    
    # CORS配置
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001"
    
    # 文件上传配置
    max_upload_size: int = 10485760  # 10MB
    allowed_extensions: str = ".docx"
    
    # 临时文件存储路径
    temp_storage_path: str = str((BASE_DIR / "../storage/temp").resolve())

    # 导出失败统计存储（SQLite）
    export_stats_db_path: str = str((BASE_DIR / "../storage/export_stats.db").resolve())
    export_stats_db_warn_bytes: int = 10 * 1024 * 1024
    export_stats_db_critical_bytes: int = 50 * 1024 * 1024
    
    # MarianMT配置
    use_marian_mt: bool = True
    marian_en_de_model: str = Field(
        default="Helsinki-NLP/opus-mt-en-de",
        validation_alias=AliasChoices("MARIAN_EN_DE_MODEL", "MARIAN_MODEL_PATH"),
    )
    marian_de_en_model: str = "Helsinki-NLP/opus-mt-de-en"
    marian_cache_dir: str = Field(
        default=str((BASE_DIR / "../models").resolve()),
        validation_alias=AliasChoices("MARIAN_CACHE_DIR", "MODEL_CACHE_DIR"),
    )
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()

