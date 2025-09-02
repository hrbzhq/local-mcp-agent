# 🧠 Local MCP Agent · 多模型本地 AI 网关

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MCP Protocol](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)
[![VS Code](https://img.shields.io/badge/VS%20Code-Extension-blue.svg)](https://marketplace.visualstudio.com/vscode)

一个基于 **Model Context Protocol (MCP)** 的本地 AI Agent 系统，支持多模型智能路由、工具调用、VS Code 插件集成。专为**隐私保护**、**高性能响应**和**开发者友好**设计。

## ✨ 核心特性

🔒 **隐私优先** - 所有数据本地处理，无需上传到云端  
🚀 **高性能** - 优化工具数量，避免 128+ 工具性能警告  
🧠 **智能路由** - 自动选择最适合的本地模型  
🔌 **VS Code 集成** - 无缝的开发环境体验  
⚙️ **可配置** - 支持多场景配置切换  
🛠️ **可扩展** - 基于 MCP 标准，易于添加新工具  

---

## 🚀 快速启动

### 1. 环境准备

```bash
git clone https://github.com/yourname/local-mcp-agent.git
cd local-mcp-agent

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或 .venv\Scripts\activate  # Windows

# 安装依赖
pip install -r server/requirements.txt
```

### 2. 启动 MCP 服务器

```bash
# 使用启动脚本（推荐）
bash scripts/start.sh

# 或直接启动
cd server && python main.py
```

### 3. VS Code 集成

1. 安装 VS Code 扩展：`Local Multi-Model AI Gateway`
2. 打开命令面板 (`Ctrl+Shift+P`)
3. 输入 `MCP: Ask Tool` 开始与 AI 对话

### 4. 验证安装

```bash
# 检查服务器健康状态
curl http://localhost:8000/health

# 列出可用工具
curl http://localhost:8000/mcp/tools
```

---

## 🏗️ 项目架构

```
local-mcp-agent/
├── 📁 server/                   # MCP 核心服务
│   ├── 🐍 main.py               # 启动入口
│   ├── 🧠 router.py             # 智能模型路由
│   ├── 🔧 mcp_server.py         # MCP 协议实现
│   ├── 📁 tools/                # 工具模块
│   │   ├── chat_with_model.py
│   │   ├── list_models.py
│   │   └── collaborative_chat.py
│   └── 📁 config/               # 分场景配置
│       ├── basic.json           # 基础配置（2工具）
│       ├── dev.json             # 开发配置（3工具）
│       └── full.json            # 完整配置
├── 📁 extensions/               # VS Code 扩展
│   └── vscode-extension/
├── 📁 scripts/                  # 自动化脚本
│   ├── start.sh                 # 启动脚本
│   ├── health_check.sh          # 健康检查
│   └── install_models.sh        # 模型安装
├── 📁 docs/                     # 文档
│   ├── ARCHITECTURE.md          # 架构设计
│   ├── API.md                   # API 文档
│   └── OPTIMIZATION.md          # 性能优化
└── 📄 README.md
```

## 🛠️ 已实现功能

### 1️⃣ 本地多模型网关 MCP 服务器

- ✅ **智能路由** - 基于输入内容自动选择最佳模型
- ✅ **工具注册** - 3个核心MCP工具（chat_with_model, list_available_models, collaborative_chat）
- ✅ **协议标准** - 完全遵循 MCP 规范
- ✅ **性能优化** - 解决了 128+ 工具性能警告

### 2️⃣ VS Code 插件集成

- ✅ **命令面板** - `MCP: List Tools`, `MCP: Ask Tool`
- ✅ **侧边栏** - 模型管理和状态展示
- ✅ **WebView** - 交互式AI响应界面
- ✅ **配置管理** - 自动连接本地MCP服务器

### 3️⃣ 完整工具调用体系

```
👤 用户输入 (VS Code)
     ↓
🔌 VS Code 扩展 (TypeScript)
     ↓ HTTP
🌐 MCP 服务器 (Python)
     ↓
🧠 智能路由 (router.py)
     ↓
🤖 本地模型 (Ollama/HuggingFace)
     ↓
📤 结构化响应返回
```

## 🤖 支持的模型

当前支持的本地模型（通过 Ollama）：

- **Qwen 2.5** - 阿里巴巴大语言模型
- **Gemma 2** - Google 开源模型
- **DeepSeek Coder** - 专业代码模型
- **Mistral** - 法国 Mistral AI 模型
- **Llama 3.2** - Meta 开源模型

> 💡 **扩展性**: 支持任何兼容 Ollama API 的模型

## ⚙️ 配置管理

### 场景化配置

```bash
# 基础配置（最佳性能）
cp server/config/basic.json .vscode/settings.json

# 开发配置（包含协作工具）
cp server/config/dev.json .vscode/settings.json

# 完整配置（所有功能）
cp server/config/full.json .vscode/settings.json
```

### 配置切换脚本

```bash
# 切换到基础配置
python scripts/switch_config.py basic

# 切换到开发配置  
python scripts/switch_config.py dev
```

## 📊 性能优化

我们解决了常见的 MCP 性能问题：

| 指标 | 优化前 | 优化后 |
|------|--------|--------|
| 工具数量 | 128+ | 3 |
| 启动时间 | ~10s | ~2s |
| 响应延迟 | >3s | <1s |
| 内存占用 | 高 | 低 |
| 稳定性 | 不稳定 | 稳定 |

详见：[docs/OPTIMIZATION.md](docs/OPTIMIZATION.md)

## 🚦 API 文档

### 核心端点

```bash
# 健康检查
GET /health

# 列出MCP工具
GET /mcp/tools

# 调用MCP工具
POST /mcp
{
  "name": "chat_with_model",
  "arguments": {
    "input": "Hello, AI!",
    "model": "qwen:7b"
  }
}

# 直接聊天接口
POST /chat
{
  "input": "Explain quantum computing",
  "model": "auto"
}
```

完整API文档：[docs/API.md](docs/API.md)

## 🧪 开发指南

### 添加新工具

1. 在 `server/tools/` 创建新工具文件
2. 实现工具处理函数
3. 在 `mcp_server.py` 中注册工具

```python
# server/tools/my_tool.py
async def my_tool_handler(arguments):
    # 工具逻辑
    return {"result": "success"}

# 在 mcp_server.py 中注册
self.register_tool(ToolDefinition(
    name="my_tool",
    description="My custom tool",
    input_schema={...},
    handler=my_tool_handler
))
```

### 本地开发

```bash
# 启动开发模式
python server/main.py --dev

# 运行测试
pytest tests/

# 代码格式化
black server/
```

## 📁 示例用法

### 1. 基础对话

```python
import requests

response = requests.post("http://localhost:8000/mcp", json={
    "name": "chat_with_model",
    "arguments": {
        "input": "写一个Python快速排序算法",
        "model": "deepseek-coder:6.7b"
    }
})

print(response.json()["data"]["output"])
```

### 2. 多模型协作

```python
response = requests.post("http://localhost:8000/mcp", json={
    "name": "collaborative_chat",
    "arguments": {
        "input": "设计一个微服务架构",
        "models": ["qwen:7b", "deepseek-coder:6.7b"],
        "max_rounds": 3
    }
})
```

### 3. VS Code 中使用

1. `Ctrl+Shift+P` → `MCP: Ask Tool`
2. 选择 `chat_with_model`
3. 输入问题："解释这段代码的作用"
4. 选择模型或留空自动选择

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 提交问题
- 使用 GitHub Issues 报告 bug
- 提出新功能建议
- 分享使用经验

### 代码贡献
1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

### 开发规范
- 遵循 PEP 8 代码风格
- 添加适当的测试
- 更新相关文档

## 📋 系统要求

- **Python**: 3.8+
- **VS Code**: 1.74.0+
- **内存**: 4GB+ (推荐 8GB+)
- **存储**: 2GB+ (用于模型存储)
- **操作系统**: Windows 10+, macOS 10.15+, Ubuntu 18.04+

## 🔧 故障排除

### 常见问题

**Q: "128+ 工具" 性能警告**
A: 使用基础配置：`cp server/config/basic.json .vscode/settings.json`

**Q: 无法连接到 MCP 服务器**
A: 检查服务器是否在运行：`curl http://localhost:8000/health`

**Q: 模型响应慢**
A: 检查本地模型是否正确安装，使用较小的模型进行测试

更多问题解答：[docs/FAQ.md](docs/FAQ.md)

## 📜 许可证

本项目采用 [MIT 许可证](LICENSE)。

## 🙏 致谢

- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP 协议规范
- [Ollama](https://ollama.ai/) - 本地模型运行时
- [VS Code](https://code.visualstudio.com/) - 开发环境集成
- 所有开源AI模型的贡献者

## 🌟 Star History

如果这个项目对您有帮助，请给我们一个 ⭐️ Star！

[![Star History Chart](https://api.star-history.com/svg?repos=yourname/local-mcp-agent&type=Date)](https://star-history.com/#yourname/local-mcp-agent&Date)

---

<div align="center">

**🚀 让本地 AI 更智能，让开发更高效！**

[开始使用](docs/QUICKSTART.md) · [架构设计](docs/ARCHITECTURE.md) · [API 文档](docs/API.md) · [贡献指南](#-贡献指南)

</div>
