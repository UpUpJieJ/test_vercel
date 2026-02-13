from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import sys
import os
import traceback

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.European_option_price_calculator.routers import (
    router as European_option_price_calculator_router,
)

app = FastAPI(title="Option Price Calculator API")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 全局异常处理 - 添加详细日志
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_detail = {"error": str(exc), "traceback": traceback.format_exc()}
    # 在 Vercel 日志中打印错误
    print(f"[ERROR] {error_detail}", flush=True)
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error", "detail": str(exc)},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        errors.append(
            {
                " -> ".join(str(loc) for loc in error["loc"]): error["msg"],
            }
        )
    return JSONResponse(status_code=422, content={"message": errors})


# 包含路由
app.include_router(European_option_price_calculator_router, prefix="/v1")


# 健康检查端点
@app.get("/")
async def root():
    return {"message": "API is running", "status": "ok"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
