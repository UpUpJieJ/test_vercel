# 直接复用 main.py 中的 FastAPI app
# 这样 Vercel 就能使用完整的 FastAPI 配置

import sys
import os

# 添加项目根目录到路径（确保能导入 app 目录）
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 从 main.py 导入 FastAPI app
# 注意：这会执行 main.py 的全部代码，包括 lifespan 和中间件配置
from main import app

# app 已经配置完成，直接导出供 Vercel 使用
# Vercel 会处理所有 /api/* 的请求
