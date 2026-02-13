FROM python:3.12-alpine

# 安装 uv
RUN pip install uv

ENV UV_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/
ENV PIP_PROGRESS_BAR=off
ENV UV_LINK_MODE=copy

WORKDIR /app

# 复制依赖文件
COPY pyproject.toml uv.lock ./


RUN uv pip install --system --no-cache .


COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--log-level", "info"]
