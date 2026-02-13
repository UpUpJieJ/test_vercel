# 期权价格计算器

一个基于 Black-Scholes 模型的欧式期权定价计算器，提供 Web 界面和 REST API 接口。

已经部署在http://43.142.89.100:8001/，可快速查看

## 项目简介

本项目实现了一个完整的期权价格计算系统，采用前后端分离架构：
- **后端**：基于 FastAPI 构建，提供期权定价计算服务
- **前端**：基于 Vue 3 + Element Plus 构建，提供友好的用户界面

## 功能特性

- 支持欧式看涨期权（Call Option）和看跌期权（Put Option）定价
- 基于 Black-Scholes 模型进行精确计算
- RESTful API 接口，易于集成
- 响应式 Web 界面，操作便捷
- 支持 Docker 容器化部署
- 完整的参数验证和错误处理

## 技术栈

### 后端
- **Python 3.12**
- **FastAPI** - 高性能 Web 框架
- **NumPy & SciPy** - 科学计算库
- **Pydantic** - 数据验证
- **Uvicorn** - ASGI 服务器

### 前端
- **Vue 3** - 渐进式 JavaScript 框架
- **Vite** - 下一代前端构建工具
- **Element Plus** - Vue 3 组件库

## 快速开始

### 环境要求

- Python 3.12+
- Node.js 22.12.0+
- uv (Python 包管理器)

### 后端启动

```bash
# 安装依赖
uv pip install --system

# 启动开发服务器
python main.py
```

后端服务将在 `http://127.0.0.1:8000` 启动

API 文档访问：`http://127.0.0.1:8000/docs`

### 运行测试

```bash
# 安装测试依赖
uv pip install --system pytest pytest-asyncio

# 运行单元测试
python -m pytest tests/ -v
```

测试覆盖：
- 看涨期权价格计算
- 看跌期权价格计算
- 平价期权（ATM）测试
- 深度实值/虚值期权测试
- 价格关系验证（如看跌-看涨平价关系）

### 前端启动

```bash
cd frontend/option_price_calculator

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端服务将在 `http://localhost:5173` 启动

## Docker 部署

### 使用 Docker Compose

### 构建前端

```bash
npm run build
```

构建产物将输出到 `docker/html` 目录

`nginx.conf`文件在`docker/conf`目录

```bash
# 构建并启动所有服务
docker-compose up -d

# 停止服务
docker-compose down
```

服务访问地址：
- 后端 API：`http://localhost:8000`
- 前端界面：`http://localhost:8001`

## API 使用说明

### 计算期权价格

```http
POST /api/v1/calculate
{
  "ccy_pair": "USDCNY",
  "option_type": "call",
  "spot_rate": 7.2,
  "strike_price": 7.3,
  "days_to_expiry": 90
}
```

**输入参数说明**

| 参数           | 类型   | 必填 | 说明                                     |
| -------------- | ------ | ---- | ---------------------------------------- |
| ccy_pair       | string | 是   | 标的资产币种对（6位大写字母，如 USDCNY） |
| option_type    | string | 是   | 期权类型：call（看涨）或 put（看跌）     |
| spot_rate      | float  | 是   | 即期汇率/现汇汇率                        |
| strike_price   | float  | 是   | 期权行权价                               |
| days_to_expiry | int    | 是   | 期权到期时间（天）                       |

**响应格式**

```json
{
  "option_price": 0.12345678,
  "calculation_time": "2026-01-28T10:30:00",
  "status": "success",
  "parameters": {
    "ccy_pair": "USDCNY",
    "option_type": "call",
    "spot_rate": 7.2,
    "strike_price": 7.3,
    "days_to_expiry": 90
  }
}
```

## 项目结构

```
option_price_calculator/
├── app/
│   ├── European_option_price_calculator/
│   │   ├── depends.py      # 依赖注入
│   │   ├── exceptions.py   # 异常定义
│   │   ├── routers.py      # 路由定义
│   │   ├── schemas.py      # 数据模型
│   │   └── services.py     # 业务逻辑
│   └── utils/
│       └── logger.py       # 日志工具
├── frontend/
│   └── option_price_calculator/
│       ├── src/
│       │   ├── components/
│       │   │   └── OptionCalculator.vue
│       │   ├── App.vue
│       │   └── main.js
│       ├── docker/
│       │   ├── conf/nginx.conf
│       │   └── html/       # 构建产物
│       └── package.json
├── logs/                   # 日志文件
├── main.py                 # 应用入口
├── pyproject.toml          # Python 项目配置
├── Dockerfile              # 后端 Docker 配置
└── docker-compose.yml      # Docker Compose 配置
```

## Black-Scholes 模型

### 模型假设

Black-Scholes 模型基于以下几个关键假设：

- 市场无摩擦（无交易成本、无税收）
- 资产价格遵循几何布朗运动
- 无风险利率 $r$ 恒定且已知
- 标的资产不支付股息
- 市场允许卖空
- 期权为欧式期权（只能在到期日执行）

### Black-Scholes 公式

#### 欧式看涨期权定价公式

对于欧式看涨期权，定价公式为：

$$C = S_0 N(d_1) - K e^{-rT} N(d_2)$$

其中：

- $C$ = 看涨期权价格
- $S_0$ = 标的资产当前价格
- $K$ = 期权执行价格
- $r$ = 无风险利率
- $T$ = 期权到期时间（年）
- $N(\cdot)$ = 标准正态分布的累积分布函数
- $\sigma$ = 标的资产收益率的波动率

#### 中间变量 $d_1$ 和 $d_2$

$$d_1 = \frac{\ln(S_0 / K) + (r + \sigma^2 / 2) T}{\sigma \sqrt{T}}$$

$$d_2 = d_1 - \sigma \sqrt{T}$$

#### 欧式看跌期权定价公式

对于欧式看跌期权，定价公式为：

$$P = K e^{-rT} N(-d_2) - S_0 N(-d_1)$$

其中 $P$ 为看跌期权价格。

## 代码中的假设

- 假设用户输入的币种对正确，即真实存在这个币种
- 无风险利率默认为 2%
- 隐含波动率使用历史波动率替代，默认为 3%
- 

## 说明

- 前端部分布局以及css样式使用Gemini3pro辅助完成
- 测试的案例使用MiniMax-M2.1辅助完成
