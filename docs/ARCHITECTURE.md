# 架构设计文档

## 🏗️ 整体架构

Local MCP Agent 采用分层架构设计，确保模块化、可扩展性和高性能。

```
┌─────────────────────────────────────┐
│           用户界面层                 │
│  ┌─────────────┐ ┌─────────────────┐ │
│  │ VS Code UI  │ │  Web Interface  │ │
│  └─────────────┘ └─────────────────┘ │
└─────────────────┬───────────────────┘
                  │ HTTP/WebSocket
┌─────────────────┴───────────────────┐
│            API 网关层                │
│  ┌─────────────────────────────────┐ │
│  │      FastAPI Server             │ │
│  │   (main.py, api_server.py)      │ │
│  └─────────────────────────────────┘ │
└─────────────────┬───────────────────┘
                  │ 内部调用
┌─────────────────┴───────────────────┐
│           MCP 协议层                 │
│  ┌─────────────────────────────────┐ │
│  │       MCP Server                │ │
│  │     (mcp_server.py)             │ │
│  │                                 │ │
│  │ ┌─────────┐ ┌─────────────────┐ │ │
│  │ │ Tools   │ │ Tool Registry   │ │ │
│  │ └─────────┘ └─────────────────┘ │ │
│  └─────────────────────────────────┘ │
└─────────────────┬───────────────────┘
                  │
┌─────────────────┴───────────────────┐
│           业务逻辑层                 │
│  ┌─────────────┐ ┌─────────────────┐ │
│  │   Router    │ │ Model Manager   │ │
│  │ (router.py) │ │(model_manager.py)│ │
│  └─────────────┘ └─────────────────┘ │
└─────────────────┬───────────────────┘
                  │
┌─────────────────┴───────────────────┐
│           模型执行层                 │
│  ┌─────────────────────────────────┐ │
│  │         Local Models            │ │
│  │   (Ollama, HuggingFace, etc.)   │ │
│  └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

## 🧩 核心组件

### 1. MCP Server (mcp_server.py)

**职责**: Model Context Protocol 协议实现
- 工具注册与管理
- 请求验证与路由
- 响应格式化
- 性能监控

**核心类**:
```python
class MCPServer:
    def __init__(self, name: str, version: str)
    async def list_tools(self) -> List[Dict[str, Any]]
    async def call_tool(self, name: str, arguments: Dict[str, Any])
    def register_tool(self, tool_def: ToolDefinition)
```

### 2. Smart Router (router.py)

**职责**: 智能模型选择
- 基于输入内容分析
- 模型能力匹配
- 负载均衡
- 性能优化

**核心算法**:
```python
def select_model(input_text: str) -> str:
    # 1. 内容类型检测 (代码、文本、数学等)
    # 2. 模型能力评估
    # 3. 性能权重计算
    # 4. 最优模型选择
```

### 3. Model Manager (model_manager.py)

**职责**: 本地模型管理
- 模型生命周期管理
- API 统一封装
- 错误处理与重试
- 性能监控

### 4. VS Code Extension

**职责**: 开发环境集成
- 命令面板集成
- 用户界面提供
- 配置管理
- 状态同步

## 🔄 数据流

### 典型请求流程

1. **用户输入** (VS Code Command Palette)
   ```
   用户: "MCP: Ask Tool" → 选择工具 → 输入内容
   ```

2. **前端处理** (VS Code Extension)
   ```typescript
   // McpClient.ts
   const result = await this.callTool({
     name: "chat_with_model",
     arguments: { input: userInput }
   });
   ```

3. **API 网关** (FastAPI)
   ```python
   # main.py
   @app.post("/mcp")
   async def handle_mcp_request(request: McpRequest):
       return await mcp_server.call_tool(request.name, request.arguments)
   ```

4. **MCP 协议层** (MCP Server)
   ```python
   # mcp_server.py
   async def call_tool(self, name: str, arguments: Dict[str, Any]):
       tool_def = self._tools[name]
       result = await tool_def.handler(arguments)
       return ToolResult(status=ToolStatus.SUCCESS, data=result)
   ```

5. **智能路由** (Router)
   ```python
   # router.py
   def select_model(input_text: str) -> str:
       if is_code_related(input_text):
           return "deepseek-coder:6.7b"
       elif is_chinese_text(input_text):
           return "qwen:7b"
       else:
           return "gemma:7b"
   ```

6. **模型调用** (Model Manager)
   ```python
   # model_manager.py
   def call_model(model: str, input_text: str) -> Dict[str, Any]:
       response = ollama_client.generate(model=model, prompt=input_text)
       return {"output": response.text, "model": model}
   ```

## 🛠️ 工具系统

### 工具注册机制

```python
@dataclass
class ToolDefinition:
    name: str
    description: str
    input_schema: Dict[str, Any]
    handler: Callable[[Dict[str, Any]], Any]
    timeout: float = 30.0
```

### 内置工具

1. **chat_with_model**
   - 智能模型选择
   - 对话上下文管理
   - 响应格式化

2. **list_available_models**
   - 模型状态检查
   - 性能信息收集
   - 可用性验证

3. **collaborative_chat**
   - 多模型协调
   - 响应聚合
   - 一致性处理

## 🔧 配置系统

### 分层配置

```
配置优先级: 
环境变量 > 用户配置 > 场景配置 > 默认配置
```

### 场景配置

- **basic.json**: 最小工具集，最佳性能
- **dev.json**: 开发调试，包含协作工具
- **full.json**: 完整功能，适合生产环境

## 📊 性能优化

### 1. 工具数量控制
- 默认限制 3-5 个核心工具
- 避免 128+ 工具性能警告
- 按需加载机制

### 2. 响应时间优化
- 模型预热机制
- 连接池管理
- 异步处理管道

### 3. 内存管理
- 模型生命周期管理
- 垃圾回收优化
- 资源监控告警

## 🔒 安全设计

### 1. 输入验证
- JSON Schema 验证
- 参数类型检查
- 长度限制控制

### 2. 执行隔离
- 工具执行超时控制
- 资源使用限制
- 错误边界处理

### 3. 数据隐私
- 本地处理优先
- 无云端数据传输
- 日志脱敏处理

## 🚀 扩展性

### 1. 新工具开发
```python
# 1. 创建工具文件
# server/tools/my_tool.py

async def my_tool_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    # 工具逻辑实现
    return {"result": "success"}

# 2. 注册工具
# 在 mcp_server.py 中添加
self.register_tool(ToolDefinition(
    name="my_tool",
    description="My custom tool",
    input_schema={...},
    handler=my_tool_handler
))
```

### 2. 新模型集成
```python
# model_manager.py 中添加新的模型提供者
class NewModelProvider:
    def __init__(self, config):
        self.config = config
    
    def call_model(self, model: str, input_text: str):
        # 模型调用逻辑
        pass
```

### 3. 新协议支持
- OpenAI API 兼容
- Anthropic Claude API
- Custom REST API

这个架构设计确保了系统的可维护性、可扩展性和高性能，为未来的功能扩展奠定了坚实基础。
