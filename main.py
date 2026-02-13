from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.utils.logger import log
from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.European_option_price_calculator.routers import router as European_option_price_calculator_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行的代码
    log.info("应用启动中...")
    yield
    log.info("应用正在关闭...")

app = FastAPI(title="Option Price Calculator", lifespan=lifespan)

origins = [     
    "http://localhost:5173",  
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        
    allow_credentials=True,       
    allow_methods=["*"],         
    allow_headers=["*"],         
)

# 全局异常捕获处理
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail}
    )

# 处理Pydantic请求验证错误
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    errors = []
    for error in exc.errors():
        errors.append({
            " -> ".join(str(loc) for loc in error['loc']): error['msg'],
        })
    
    return JSONResponse(
        status_code=422,
        content={
            "message": errors,
        }
    )


main_router = APIRouter(prefix="")
main_router.include_router(European_option_price_calculator_router)
app.include_router(main_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
