import sys
import os
from loguru import logger

# 移除默认的日志处理器
logger.remove()

# 检测是否在 Vercel Serverless 环境
IS_VERCEL = os.environ.get("VERCEL") == "1" or os.path.exists("/var/task")

if IS_VERCEL:
    # Vercel Serverless 环境：简化日志，只输出到 stderr，不使用文件
    logger.add(
        sys.stderr,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        level="INFO",
    )
else:
    # 本地开发环境：完整的日志配置
    logger.add(
        sys.stderr,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
        level="INFO",
        enqueue=True,
    )

    # 只在本地环境添加文件日志
    logger.add(
        "logs/app_{time:YYYY-MM-DD}.log",
        rotation="00:00",
        retention="7 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        encoding="utf-8",
        enqueue=True,
    )

log = logger
