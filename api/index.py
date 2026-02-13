from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.European_option_price_calculator.routers import (
    router as European_option_price_calculator_router,
)

app = FastAPI(title="Option Price Calculator API")

# CORS 配置 - 允许 Vercel 域名
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "https://*.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境建议指定具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 全局异常处理
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    errors = []
    for error in exc.errors():
        errors.append(
            {
                " -> ".join(str(loc) for loc in error["loc"]): error["msg"],
            }
        )

    return JSONResponse(status_code=422, content={"message": errors})


# 包含路由
app.include_router(European_option_price_calculator_router, prefix="/api")

# Vercel Serverless Function handler
# 注意：这里导出 app 供 Vercel 使用
