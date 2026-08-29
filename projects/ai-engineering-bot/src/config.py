"""配置管理 — 从环境变量加载，带默认值和校验。"""

from __future__ import annotations

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    # ── 飞书 ──────────────────────────────────────────────
    FEISHU_APP_ID: str = ""
    FEISHU_APP_SECRET: str = ""

    # ── LLM ───────────────────────────────────────────────
    LLM_API_KEY: str = ""
    LLM_BASE_URL: str = "https://api.deepseek.com/v1"
    LLM_MODEL: str = "deepseek-chat"
    LLM_MAX_TOKENS: int = 8192
    LLM_TEMPERATURE: float = 0.3

    # ── 向量库 ────────────────────────────────────────────
    VECTOR_STORE_TYPE: str = "memory"  # memory | milvus | qdrant
    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: int = 19530

    # ── Redis ─────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── 服务 ──────────────────────────────────────────────
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    LOG_LEVEL: str = "INFO"

    # ── 技能市场路径（映射到本地 skill 目录）───────────────
    SKILLS_PATH: str = "/home/lzh/cow/skills"

    # ── 知识库路径 ────────────────────────────────────────
    KNOWLEDGE_PATH: str = "/home/lzh/cow/knowledge"

    @field_validator("FEISHU_APP_ID")
    @classmethod
    def check_feishu_app_id(cls, v: str) -> str:
        if not v or v == "cli_xxxxxxxxxxxxxxxx":
            raise ValueError("FEISHU_APP_ID 未配置，请设置 .env 文件")
        return v

    @field_validator("LLM_API_KEY")
    @classmethod
    def check_llm_key(cls, v: str) -> str:
        if not v:
            raise ValueError("LLM_API_KEY 未配置，请设置 .env 文件")
        return v


settings = Settings()
