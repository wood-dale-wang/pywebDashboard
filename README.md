# 模块化仪表盘技术文档

## 项目概述

本项目是一个基于 FastAPI 和 YAML 配置的模块化仪表盘系统，采用前后端分离架构，支持动态模块加载和灵活的配置管理。

## 技术栈

| 层级 | 技术 | 版本 | 用途 |
|---|---|---|---|
| 后端框架 | FastAPI | 0.104.1 | Web 服务框架 |
| 模板引擎 | Jinja2 | 3.1.2 | HTML 模板渲染 |
| 配置管理 | PyYAML | 6.0.1 | YAML 配置文件解析 |
| 工具库 | aiohttp | 3.9.1 | 异步 HTTP 请求 |
| 系统监控 | psutil | 5.9.6 | 系统资源监控 |
| 时间处理 | pytz | 2023.3.post1 | 时区处理 |
| WSGI 服务器 | uvicorn | 0.24.0 | ASGI 服务器 |

## 项目结构

```
modular-dashboard/
├── engine.py                 # 核心引擎
├── run.py                   # 启动脚本
├── config.yaml              # 主配置文件
├── requirements.txt         # 依赖列表
├── modules/                 # 功能模块目录
│   ├── __init__.py
│   ├── clock.py            # 时钟模块
│   ├── system.py           # 系统监控模块
│   ├── weather.py          # 天气模块
│   └── news.py             # 新闻模块
├── templates/               # HTML 模板
│   └── dashboard.html      # 主仪表盘模板
└── static/                  # 静态资源
    ├── css/
    │   └── dashboard.css   # 样式文件
    └── js/
        └── dashboard.js    # 前端脚本
```

## 核心组件

### 1. 引擎（engine.py）

**职责**：
- 配置加载与验证
- 模块动态加载
- 路由注册
- 模板渲染

**关键类**：
```python
DashboardEngine    # 主引擎类
BaseModule        # 模块基类
```

**生命周期**：
1. 加载 YAML 配置
2. 初始化模板和静态文件
3. 动态导入并实例化模块
4. 注册 API 路由
5. 启动服务

### 2. 模块系统

**模块接口**：
```python
class BaseModule:
    async def get_data(self) -> dict[str, Any]: ...
    def get_widget_config(self) -> dict[str, Any]: ...
```

**内置模块**：

| 模块 | 文件 | 功能 | 刷新频率 |
|---|---|---|---|
| 时钟 | clock.py | 显示当前时间 | 1秒 |
| 系统 | system.py | CPU/内存/磁盘监控 | 10秒 |
| 天气 | weather.py | 天气信息 | 5分钟 |
| 新闻 | news.py | RSS 新闻列表 | 1分钟 |

### 3. 配置系统

**配置文件结构**：
```yaml
server:      # 服务器配置
  host: str
  port: int

dashboard:   # 仪表盘配置
  title: str
  theme: str
  layout: str

modules:     # 模块配置
  <module_name>:
    enabled: bool
    position: str
    class_name: str
    settings: Dict
```

**配置优先级**：
1. 命令行参数（最高）
2. 配置文件
3. 默认值（最低）

## API 接口

| 方法 | 路径 | 描述 |
|---|---|---|
| GET | / | 主仪表盘页面 |
| GET | /api/widget/{name} | 获取模块数据 |
| GET | /api/dashboard/status | 仪表盘状态 |

## 前端架构

### Widget 系统

**Widget 类型**：
- `card`：卡片式显示
- `chart`：图表显示
- `list`：列表显示
- `digital`：数字时钟

**数据流**：
1. 页面加载时初始化所有 widget
2. 按配置的频率轮询数据
3. 根据 widget 类型渲染内容

### 布局系统

**支持布局**：
- `grid`：网格布局
- `list`：列表布局
- `masonry`：瀑布流布局

## 部署指南

### 开发环境

```bash
# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
python run.py --reload
```

### 生产环境

```bash
# 使用 gunicorn
gunicorn engine:app -w 4 -k uvicorn.workers.UvicornWorker

# 或使用 uvicorn
uvicorn engine:app --host 0.0.0.0 --port 8000
```

### Docker 部署

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "run.py", "--host", "0.0.0.0"]
```

## 扩展开发

### 添加新模块

1. 创建模块文件 `modules/new_module.py`：
```python
from engine import BaseModule

class NewModule(BaseModule):
    async def get_data(self):
        return {"data": "example"}
    
    def get_widget_config(self):
        return {"type": "card", "title": "新模块"}
```

2. 更新配置：
```yaml
modules:
  new_module:
    enabled: true
    class_name: "NewModule"
    settings: {}
```

### 添加新 Widget 类型

1. 在 `dashboard.js` 中添加渲染函数：
```javascript
renderNewType(data) {
    return `<div class="new-widget">${data.content}</div>`;
}
```

2. 在 `dashboard.css` 中添加样式

## 监控与维护

### 日志配置

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### 健康检查

```bash
# 检查服务状态
curl http://localhost:8000/api/dashboard/status

# 检查特定模块
curl http://localhost:8000/api/widget/system
```

### 性能优化

1. **缓存**：对慢速 API 添加缓存
2. **并发**：使用 asyncio 处理并发请求
3. **压缩**：启用 gzip 压缩
4. **CDN**：静态文件使用 CDN

## 故障排查

### 常见问题

| 问题 | 原因 | 解决方案 |
|---|---|---|
| 模块加载失败 | 类名/路径错误 | 检查配置文件 |
| 数据不更新 | 刷新间隔设置 | 检查模块配置 |
| 样式错乱 | 静态文件未加载 | 检查 static 目录 |
| 端口占用 | 默认 8000 被占 | 修改端口配置 |

### 调试模式

```bash
# 启用调试日志
export LOG_LEVEL=DEBUG
python run.py
```

## 安全考虑

1. **输入验证**：所有用户输入都经过验证
2. **CORS**：配置跨域策略
3. **速率限制**：可添加中间件限制请求频率
4. **认证**：生产环境建议添加认证

## 版本管理

使用语义化版本控制（SemVer）：

- 主版本：不兼容的 API 变更
- 次版本：向下兼容的功能性新增
- 修订号：向下兼容的问题修正

## 更新日志

### v1.0.0 (2024-01-01)
- 初始版本
- 支持模块化架构
- 内置 4 个基础模块