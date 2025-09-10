# 多模型智能Agent系统 v2.0

一个功能强大的多模型智能Agent系统，支持Web界面、REST API、插件扩展和实时监控。

## 🚀 主要特性

### 🌐 Web界面
- 现代化的响应式Web界面
- 实时系统监控和状态显示
- 交互式对话界面
- 可视化数据图表
- 多模型切换支持

### 🔌 REST API
- 完整的RESTful API接口
- 模型调用API
- 插件管理API
- 系统监控API
- 任务历史API

### 🧩 插件系统
- **网页抓取插件**: 抓取和分析网页内容
- **文件处理插件**: 支持多种文件格式的读取和处理
- **数据库插件**: SQLite数据库操作
- **通知插件**: 多渠道通知（邮件、Webhook、桌面通知）
- **API网关插件**: 外部API集成和调用

### 🎯 @查询功能
- **智能查询路由**: 通过@前缀明确指定MCP服务查询
- **多样化查询类型**: 支持@web、@code、@api、@data、@train等多种类型
- **缓存机制**: 查询结果自动缓存，提高响应速度
- **兼容性**: 不影响现有数据库查询和其他功能

### 📊 监控和分析
- 实时性能监控
- 系统资源使用情况
- 任务执行统计
- 可视化报告生成

## 🛠️ 安装和设置

### 1. 环境要求
- Python 3.8+
- Ollama (本地安装)
- 已下载的模型文件

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置系统
编辑 `config.json` 文件，根据需要调整配置：
- Web界面设置
- API服务器配置
- 模型配置
- 插件配置

### 4. 启动系统

#### 方式一：使用启动脚本（推荐）
```bash
python start.py
```
然后选择启动模式：
1. Web界面
2. 命令行界面
3. API服务器
4. 启动所有服务

#### 方式二：命令行参数
```bash
# 启动Web界面
python start.py --web --port 5000

# 启动API服务器
python start.py --api --api-port 8000

# 启动命令行界面
python start.py --cli
```

## 📖 使用指南

### Web界面使用
1. 启动Web界面后，访问 `http://localhost:5000`
2. 使用侧边栏导航到不同功能模块
3. 在"对话"页面与AI模型交互
4. 查看"仪表板"了解系统状态
5. 在"插件中心"管理插件

### @查询功能使用
@查询功能允许您明确指定某些查询应该通过MCP服务处理：

#### 基本语法
```
@<查询类型> <查询内容>
```

#### 支持的查询类型
- `@help` - 显示帮助信息
- `@web` - 网页搜索和内容查询
- `@code` - 编程代码示例查询
- `@api` - API相关信息查询
- `@data` - 数据分析相关查询
- `@train` - 列车时刻表查询

#### 使用示例
```
@web python教程          # 网页搜索Python教程
@code 排序算法           # 获取排序算法代码示例
@api GraphQL             # 查询GraphQL API信息
@train G902              # 查询G902次列车时刻表
```

#### 功能特点
- ✅ 智能识别@开头的查询
- ✅ 自动路由到MCP服务
- ✅ 结果缓存机制
- ✅ 不影响普通查询

### API接口使用
系统提供以下主要API端点：

#### 模型相关
- `GET /api/models` - 获取可用模型列表
- `POST /api/tasks` - 执行任务
  ```json
  {
    "task": "你的问题或任务",
    "model": "qwen3"
  }
  ```

#### 系统监控
- `GET /api/status` - 获取系统状态
- `GET /api/performance` - 获取性能指标
- `GET /api/history` - 获取任务历史

#### 插件相关
- `GET /api/plugins` - 获取插件列表
- `POST /api/plugins/{plugin_name}/execute` - 执行插件

### 插件使用

#### 网页抓取插件
```python
from plugins.web_scraper import WebScraperPlugin

plugin = WebScraperPlugin()
plugin.initialize({"timeout": 30})
result = plugin.execute(action="scrape", url="https://example.com")
```

#### 文件处理插件
```python
from plugins.file_processor import FileProcessorPlugin

plugin = FileProcessorPlugin()
plugin.initialize({"max_file_size": 10485760})
result = plugin.execute(action="read", file_path="document.pdf")
```

#### 数据库插件
```python
from plugins.database import DatabasePlugin

plugin = DatabasePlugin()
plugin.initialize({"db_path": "data.db"})
result = plugin.execute(action="query", sql="SELECT * FROM users")
```

#### 通知插件
```python
from plugins.notification import NotificationPlugin

plugin = NotificationPlugin()
plugin.initialize({
    "enable_desktop": True,
    "enable_email": False
})
result = plugin.execute(
    action="send",
    title="系统通知",
    message="任务已完成",
    channels=["desktop"]
)
```

#### API网关插件
```python
from plugins.api_gateway import APIGatewayPlugin

plugin = APIGatewayPlugin()
plugin.initialize({
    "apis": {
        "github": {
            "base_url": "https://api.github.com"
        }
    }
})
result = plugin.execute(
    action="call",
    api_name="github",
    endpoint="/user",
    method="GET"
)
```

## 🔧 配置说明

### 模型配置
在 `config.json` 中配置Ollama模型：
```json
{
  "models": {
    "ollama_host": "http://localhost:11434",
    "default_model": "qwen3",
    "available_models": {
      "qwen3": {
        "name": "qwen3:0.6b",
        "description": "通义千问3模型",
        "max_tokens": 2048,
        "temperature": 0.7
      }
    }
  }
}
```

## 变更记录 (Changelog)

- 2025-09-09: 将任务API从 `/api/task` 重命名为 `/api/tasks`，以遵循复数资源风格并统一代码路径。
  - 为保证向后兼容，新增兼容路由: `POST /api/task`（代理到 `/api/tasks`），旧脚本无需立即修改即可继续工作。
  - 已更新的文件（主要改动）:
    - `templates/index.html` - 修复前端对话请求路径并修复模型/性能渲染问题
    - `web_app.py` - 确保 `GET /api/status` 返回模型数组；新增 `/api/task` 兼容路由
    - 测试/示例脚本: `test_system.py`, `test_train_schedule.py`, `test_at_query.py`, `test_system_features.py`, `demo_at_query.py`
    - `README.md` - 更新 API 文档与本次变更说明

### 快速 lint/typecheck 汇总

- 运行: `python -m py_compile web_app.py src/model_manager.py src/performance_monitor.py` — 通过（无语法错误）。
- 运行: `flake8 --max-line-length=120` — 报告了多处样式/未使用导入/长行问题，主要集中在演示脚本、插件与部分 `src/` 文件。已在工作区保留这些警告（非阻塞性），建议逐步修复或在 CI 中加入规则以强制整洁。

如果你想，我可以：
- 进一步清理 lint 警告（逐文件修复），或
- 添加一个轻量级的 CI 配置（GitHub Actions）来在提交时运行 flake8 和 pytests，或
- 保留当前改动并在下次迭代中逐步整改样式问题。

### 插件配置
配置各个插件的参数：
```json
{
  "plugins": {
    "enabled_plugins": ["web_scraper", "file_processor"],
    "plugin_configs": {
      "web_scraper": {
        "timeout": 30,
        "max_retries": 3
      }
    }
  }
}
```

## 📊 监控和日志

### 日志文件
- 主日志：`logs/agent.log`
- 错误日志：`logs/error.log`
- 性能日志：`logs/performance.log`

### 性能监控
系统自动监控：
- CPU使用率
- 内存使用率
- 磁盘使用率
- 网络流量
- 任务执行时间

### 可视化报告
- 任务执行趋势图
- 模型使用分布图
- 性能指标图表
- 系统资源使用图

## 🔒 安全配置

### API安全
- 可选API密钥验证
- CORS配置
- 请求频率限制

### 数据安全
- 敏感信息加密存储
- 数据库自动备份
- 日志轮转

## 🚀 部署选项

### 开发环境
```bash
python start.py --web --debug
```

### 生产环境
```bash
# 使用Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 web_app:app

# 或使用Docker
docker build -t agent-system .
docker run -p 5000:5000 agent-system
```

## 📝 更新日志

### v2.1.0 (2025-09-08)
- 🎯 新增@查询功能，支持通过@前缀明确指定MCP服务查询
- 🔄 优化查询路由逻辑，区分数据库查询和MCP查询
- 📚 添加@help、@web、@code、@api、@data、@train等多种查询类型
- 💾 实现查询结果缓存机制，提高响应速度
- 📖 创建详细的使用指南文档

### v2.0.0 (2025-09-08)
- ✨ 添加Web界面
- 🔌 添加REST API接口
- 🧩 重构插件系统
- 📊 添加实时监控
- 🎨 现代化UI设计
- 📱 响应式布局
- 🔄 WebSocket实时通信

### v1.0.0 (初始版本)
- 🤖 基础多模型支持
- 💻 命令行界面
- 🔧 基础插件框架
- 📈 性能监控

## 🤝 贡献指南

1. Fork项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

## 📄 许可证

本项目采用MIT许可证。

## 📞 支持

如有问题或建议，请提交Issue或Pull Request。

---

**享受使用多模型智能Agent系统！** 🚀
