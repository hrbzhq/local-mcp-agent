# API 接口文档

## 🌐 服务器信息

- **基础URL**: `http://localhost:8000`
- **协议**: HTTP/1.1
- **数据格式**: JSON
- **认证**: 可选 (开发模式默认关闭)

## 📋 端点概览

| 端点 | 方法 | 描述 | 认证 |
|------|------|------|------|
| `/health` | GET | 服务器健康检查 | 否 |
| `/info` | GET | 服务器信息 | 否 |
| `/models` | GET | 列出可用模型 | 否 |
| `/chat` | POST | 直接聊天接口 | 可选 |
| `/mcp` | POST | MCP 工具调用 | 可选 |
| `/mcp/tools` | GET | 列出 MCP 工具 | 否 |
| `/stats` | GET | 服务器统计信息 | 否 |

## 🔍 详细接口

### 1. 健康检查

**GET** `/health`

检查服务器运行状态。

**响应示例**:
```json
{
  "status": "healthy",
  "server_name": "Local Multi-Model AI Gateway",
  "version": "2.0.0",
  "tools_registered": 3,
  "uptime": 1693737600.123,
  "total_calls": 42,
  "successful_calls": 40,
  "failed_calls": 2,
  "average_execution_time": 1.25
}
```

### 2. 服务器信息

**GET** `/info`

获取详细的服务器配置信息。

**响应示例**:
```json
{
  "name": "Local Multi-Model AI Gateway",
  "version": "2.0.0",
  "description": "本地多模型AI网关，支持MCP协议",
  "mcp_enabled": true,
  "authentication_enabled": false,
  "models": {
    "count": 4,
    "available": ["qwen:7b", "gemma:7b", "deepseek-coder:6.7b", "mistral:instruct"]
  },
  "tools": {
    "count": 3,
    "registered": ["chat_with_model", "list_available_models", "collaborative_chat"]
  }
}
```

### 3. 模型列表

**GET** `/models`

获取所有可用的本地模型。

**响应示例**:
```json
{
  "models": ["qwen:7b", "gemma:7b", "deepseek-coder:6.7b", "mistral:instruct"],
  "count": 4,
  "models_raw": "NAME                    ID              SIZE    MODIFIED\nqwen:7b                 abc123...       4.1GB   2 hours ago\ngemma:7b               def456...       5.2GB   1 day ago\n...",
  "timestamp": 1693737600.123
}
```

### 4. 直接聊天

**POST** `/chat`

直接与AI模型对话，支持自动模型选择。

**请求体**:
```json
{
  "input": "解释什么是量子计算",
  "model": "auto",  // 可选，默认自动选择
  "user_id": "user123",  // 可选
  "temperature": 0.7  // 可选，0.0-1.0
}
```

**响应示例**:
```json
{
  "model": "qwen:7b",
  "input": "解释什么是量子计算",
  "output": "量子计算是一种基于量子力学原理的计算模式...",
  "meta": {
    "latency_ms": 1245,
    "model_call_ms": 1120,
    "input_tokens": 15,
    "output_tokens": 256,
    "model_selected": "auto"
  },
  "timestamp": 1693737600.123
}
```

### 5. MCP 工具调用

**POST** `/mcp`

调用注册的 MCP 工具。

**请求体**:
```json
{
  "name": "chat_with_model",
  "arguments": {
    "input": "写一个Python快速排序算法",
    "model": "deepseek-coder:6.7b",
    "user_id": "developer",
    "temperature": 0.3
  }
}
```

**响应示例**:
```json
{
  "status": "success",
  "data": {
    "model": "deepseek-coder:6.7b",
    "input": "写一个Python快速排序算法",
    "output": "def quicksort(arr):\n    if len(arr) <= 1:\n        return arr\n    ...",
    "user_id": "developer",
    "temperature": 0.3,
    "timestamp": 1693737600.123,
    "metadata": {
      "model_selected": "manual",
      "input_length": 12,
      "output_length": 234
    }
  },
  "execution_time": 2.15,
  "tool_name": "chat_with_model",
  "timestamp": 1693737600.123
}
```

### 6. 列出 MCP 工具

**GET** `/mcp/tools`

获取所有已注册的 MCP 工具。

**响应示例**:
```json
[
  {
    "name": "chat_with_model",
    "description": "与指定 AI 模型对话，或根据内容自动选择模型",
    "inputSchema": {
      "type": "object",
      "properties": {
        "input": {
          "type": "string",
          "description": "发送给模型的输入文本"
        },
        "model": {
          "type": "string",
          "description": "可选：使用的特定模型（未提供则自动选择）"
        },
        "user_id": {
          "type": "string",
          "description": "可选：用于上下文的用户标识",
          "default": "anonymous"
        },
        "temperature": {
          "type": "number",
          "description": "可选：模型温度 (0.0 到 1.0)",
          "minimum": 0.0,
          "maximum": 1.0,
          "default": 0.7
        }
      },
      "required": ["input"]
    }
  },
  {
    "name": "list_available_models",
    "description": "列出本地网关中所有可用模型及其能力",
    "inputSchema": {
      "type": "object",
      "properties": {
        "include_details": {
          "type": "boolean",
          "description": "是否包含模型的详细信息",
          "default": false
        }
      },
      "required": []
    }
  },
  {
    "name": "collaborative_chat",
    "description": "启动多个模型之间的协作对话",
    "inputSchema": {
      "type": "object",
      "properties": {
        "input": {
          "type": "string",
          "description": "协作的初始输入"
        },
        "models": {
          "type": "array",
          "items": {"type": "string"},
          "description": "参与协作的模型列表",
          "minItems": 1
        },
        "max_rounds": {
          "type": "integer",
          "description": "最大协作轮数",
          "minimum": 1,
          "maximum": 10,
          "default": 3
        },
        "strategy": {
          "type": "string",
          "description": "协作策略",
          "enum": ["sequential", "parallel", "consensus"],
          "default": "sequential"
        }
      },
      "required": ["input", "models"]
    }
  }
]
```

### 7. 服务器统计

**GET** `/stats`

获取服务器运行统计信息。

**响应示例**:
```json
{
  "total_calls": 156,
  "successful_calls": 148,
  "failed_calls": 8,
  "average_execution_time": 1.42,
  "uptime_seconds": 7200,
  "tools_usage": {
    "chat_with_model": 120,
    "list_available_models": 25,
    "collaborative_chat": 11
  },
  "models_usage": {
    "qwen:7b": 45,
    "deepseek-coder:6.7b": 38,
    "gemma:7b": 32,
    "mistral:instruct": 5
  },
  "error_breakdown": {
    "timeout": 3,
    "model_not_available": 2,
    "validation_error": 3
  }
}
```

## 🚨 错误响应

所有错误响应都遵循统一格式：

```json
{
  "status": "error",
  "error": "错误描述信息",
  "error_code": "ERROR_TYPE",
  "execution_time": 0.05,
  "tool_name": "chat_with_model",
  "timestamp": 1693737600.123
}
```

### 常见错误码

| 错误码 | 描述 | HTTP 状态码 |
|--------|------|-------------|
| `TOOL_NOT_FOUND` | 请求的工具不存在 | 404 |
| `VALIDATION_ERROR` | 请求参数验证失败 | 400 |
| `MODEL_NOT_AVAILABLE` | 请求的模型不可用 | 503 |
| `TIMEOUT_ERROR` | 工具执行超时 | 408 |
| `INTERNAL_ERROR` | 服务器内部错误 | 500 |
| `RATE_LIMIT_EXCEEDED` | 请求频率超限 | 429 |

## 📝 使用示例

### curl 示例

```bash
# 健康检查
curl http://localhost:8000/health

# 获取模型列表
curl http://localhost:8000/models

# 直接聊天
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Hello, AI!",
    "model": "auto"
  }'

# MCP 工具调用
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "name": "chat_with_model",
    "arguments": {
      "input": "解释递归算法",
      "model": "qwen:7b"
    }
  }'
```

### Python 示例

```python
import requests

# 基础配置
BASE_URL = "http://localhost:8000"

# 聊天请求
def chat_with_ai(message, model="auto"):
    response = requests.post(f"{BASE_URL}/chat", json={
        "input": message,
        "model": model
    })
    return response.json()

# MCP 工具调用
def call_mcp_tool(tool_name, arguments):
    response = requests.post(f"{BASE_URL}/mcp", json={
        "name": tool_name,
        "arguments": arguments
    })
    return response.json()

# 使用示例
result = chat_with_ai("写一个冒泡排序算法", "deepseek-coder:6.7b")
print(result["output"])

# 协作聊天
collaboration = call_mcp_tool("collaborative_chat", {
    "input": "设计一个微服务架构",
    "models": ["qwen:7b", "deepseek-coder:6.7b"],
    "max_rounds": 3
})
print(collaboration["data"]["collaboration_summary"]["final_output"])
```

### JavaScript 示例

```javascript
// 使用 fetch API
async function chatWithAI(message, model = 'auto') {
  const response = await fetch('http://localhost:8000/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      input: message,
      model: model
    })
  });
  return await response.json();
}

// 使用示例
chatWithAI('解释什么是机器学习', 'qwen:7b')
  .then(result => console.log(result.output))
  .catch(error => console.error('Error:', error));
```

## 🔒 认证 (可选)

当启用认证时，需要在请求头中包含 API 密钥：

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{"name": "chat_with_model", "arguments": {...}}'
```

## 📊 性能建议

1. **批量请求**: 对于多个请求，考虑使用 HTTP/2 或连接复用
2. **超时设置**: 建议设置合理的超时时间 (30-120秒)
3. **重试机制**: 实现指数退避的重试策略
4. **缓存**: 对于重复的模型列表请求可以进行缓存
5. **连接池**: 使用连接池提高并发性能

这个 API 设计遵循 RESTful 原则，提供了完整的错误处理和性能优化建议。
