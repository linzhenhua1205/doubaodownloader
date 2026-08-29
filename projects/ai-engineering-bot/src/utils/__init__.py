"""结构化日志 — structlog 封装，trace_id 贯穿全链路。"""

from __future__ import annotations

import logging
import structlog
from config import settings


def setup_logging() -> None:
    """初始化 structlog。"""
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.dev.ConsoleRenderer()
            if settings.LOG_LEVEL == "DEBUG"
            else structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    logging.basicConfig(level=settings.LOG_LEVEL)


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    return structlog.get_logger(name or __name__)
