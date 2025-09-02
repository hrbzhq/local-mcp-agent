# 🚀 开发者指南

## 🎯 开发环境搭建

### 1. 开发工具要求

- **Python**: 3.9+ (推荐 3.11)
- **Node.js**: 16+ (用于 VS Code 扩展开发)
- **Git**: 最新版本
- **IDE**: VS Code + Python Extension
- **Ollama**: 本地AI模型运行环境

### 2. 克隆和设置

```bash
# 克隆仓库
git clone https://github.com/your-org/local-mcp-agent.git
cd local-mcp-agent

# 创建开发环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# 安装开发依赖
pip install -r requirements-dev.txt

# 安装项目为可编辑模式
pip install -e .

# 安装 pre-commit hooks
pre-commit install
```

### 3. 开发配置

```bash
# 复制开发配置
cp config/dev.json config/config.json

# 设置环境变量
export ENVIRONMENT=development
export DEBUG=1
export LOG_LEVEL=DEBUG
```

## 🏗️ 项目结构详解

```
local-mcp-agent/
├── server/                 # 核心服务器代码
│   ├── api_server.py      # FastAPI 应用入口
│   ├── mcp_server.py      # MCP 协议实现
│   ├── model_manager.py   # 模型管理和选择逻辑
│   ├── router.py          # API 路由定义
│   └── auth.py            # 认证和授权
├── tools/                  # MCP 工具实现
│   ├── __init__.py
│   ├── chat_tool.py       # 聊天工具
│   ├── model_tool.py      # 模型管理工具
│   └── collaboration_tool.py  # 协作工具
├── extensions/             # VS Code 扩展
│   ├── src/
│   │   ├── extension.ts   # 扩展主文件
│   │   ├── services/      # 服务层
│   │   └── providers/     # 数据提供者
│   └── package.json
├── config/                 # 配置文件
├── scripts/               # 部署和管理脚本
├── tests/                 # 测试代码
├── docs/                  # 文档
└── examples/              # 使用示例
```

## 🔧 核心组件开发

### 1. MCP 工具开发

创建新的 MCP 工具：

```python
# tools/my_custom_tool.py
from typing import Dict, Any, Optional
from ..server.mcp_server import ToolDefinition

class MyCustomTool:
    """自定义 MCP 工具示例"""
    
    @staticmethod
    def get_definition() -> ToolDefinition:
        """返回工具定义"""
        return ToolDefinition(
            name="my_custom_tool",
            description="我的自定义工具，用于特定任务",
            inputSchema={
                "type": "object",
                "properties": {
                    "input": {
                        "type": "string",
                        "description": "输入参数"
                    },
                    "option": {
                        "type": "string",
                        "description": "可选参数",
                        "enum": ["option1", "option2"],
                        "default": "option1"
                    }
                },
                "required": ["input"]
            }
        )
    
    @staticmethod
    async def execute(arguments: Dict[str, Any]) -> Dict[str, Any]:
        """执行工具逻辑"""
        input_text = arguments.get("input", "")
        option = arguments.get("option", "option1")
        
        # 实现你的逻辑
        result = f"处理 '{input_text}' 使用选项 '{option}'"
        
        return {
            "result": result,
            "input": input_text,
            "option": option,
            "timestamp": time.time(),
            "metadata": {
                "tool_version": "1.0.0",
                "processing_time": 0.1
            }
        }

# 在 server/mcp_server.py 中注册工具
from tools.my_custom_tool import MyCustomTool

class MCPServer:
    def __init__(self):
        # 注册新工具
        self.register_tool(MyCustomTool.get_definition(), MyCustomTool.execute)
```

### 2. 模型适配器开发

添加新的AI模型支持：

```python
# server/adapters/new_model_adapter.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class ModelAdapter(ABC):
    """模型适配器基类"""
    
    @abstractmethod
    async def chat(self, messages: List[Dict], **kwargs) -> str:
        """聊天接口"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """检查模型是否可用"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """获取模型能力"""
        pass

class NewModelAdapter(ModelAdapter):
    """新模型适配器实现"""
    
    def __init__(self, model_name: str, api_endpoint: str):
        self.model_name = model_name
        self.api_endpoint = api_endpoint
    
    async def chat(self, messages: List[Dict], **kwargs) -> str:
        """实现新模型的聊天逻辑"""
        # 调用新模型的API
        # 处理请求和响应格式转换
        # 返回标准化的响应
        pass
    
    def is_available(self) -> bool:
        """检查新模型服务是否可用"""
        try:
            # 实现健康检查逻辑
            return True
        except:
            return False
    
    def get_capabilities(self) -> Dict[str, Any]:
        """返回模型能力描述"""
        return {
            "name": self.model_name,
            "type": "language_model",
            "capabilities": ["chat", "completion"],
            "languages": ["en", "zh"],
            "max_tokens": 4096,
            "supports_streaming": True
        }

# 在 model_manager.py 中注册新适配器
class ModelManager:
    def __init__(self):
        # 注册新模型适配器
        self.adapters["new_model"] = NewModelAdapter(
            model_name="new_model:latest",
            api_endpoint="http://localhost:9000"
        )
```

### 3. API 端点开发

添加新的API端点：

```python
# server/routers/custom_router.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api/v1/custom", tags=["custom"])

class CustomRequest(BaseModel):
    """自定义请求模型"""
    data: str
    options: Optional[dict] = None

class CustomResponse(BaseModel):
    """自定义响应模型"""
    result: str
    processed_at: float

@router.post("/process", response_model=CustomResponse)
async def process_custom_data(request: CustomRequest):
    """处理自定义数据"""
    try:
        # 实现处理逻辑
        result = f"Processed: {request.data}"
        
        return CustomResponse(
            result=result,
            processed_at=time.time()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_custom_status():
    """获取自定义服务状态"""
    return {
        "status": "active",
        "service": "custom",
        "version": "1.0.0"
    }

# 在 api_server.py 中包含路由
from routers.custom_router import router as custom_router

app = FastAPI()
app.include_router(custom_router)
```

## 🧪 测试开发

### 1. 单元测试

```python
# tests/test_tools.py
import pytest
import asyncio
from tools.chat_tool import ChatTool

class TestChatTool:
    """聊天工具测试"""
    
    @pytest.fixture
    def chat_tool(self):
        return ChatTool()
    
    def test_tool_definition(self, chat_tool):
        """测试工具定义"""
        definition = chat_tool.get_definition()
        assert definition.name == "chat_with_model"
        assert "input" in definition.inputSchema["properties"]
    
    @pytest.mark.asyncio
    async def test_execute_basic_chat(self, chat_tool):
        """测试基本聊天功能"""
        arguments = {
            "input": "Hello, AI!",
            "model": "qwen:7b"
        }
        
        result = await chat_tool.execute(arguments)
        
        assert "output" in result
        assert result["model"] == "qwen:7b"
        assert len(result["output"]) > 0
    
    @pytest.mark.asyncio
    async def test_auto_model_selection(self, chat_tool):
        """测试自动模型选择"""
        arguments = {
            "input": "写一个Python函数",
            "model": "auto"
        }
        
        result = await chat_tool.execute(arguments)
        
        # 应该选择编程相关的模型
        assert "deepseek" in result["model"] or "coder" in result["model"]

# 运行测试
# pytest tests/test_tools.py -v
```

### 2. 集成测试

```python
# tests/test_integration.py
import pytest
import requests
import time
from threading import Thread

class TestIntegration:
    """集成测试"""
    
    @pytest.fixture(scope="class")
    def server_url(self):
        """测试服务器URL"""
        return "http://localhost:8000"
    
    def test_server_health(self, server_url):
        """测试服务器健康状态"""
        response = requests.get(f"{server_url}/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["tools_registered"] > 0
    
    def test_chat_endpoint(self, server_url):
        """测试聊天端点"""
        payload = {
            "input": "Hello, how are you?",
            "model": "auto"
        }
        
        response = requests.post(f"{server_url}/chat", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert "output" in data
        assert "model" in data
        assert len(data["output"]) > 0
    
    def test_mcp_tool_call(self, server_url):
        """测试MCP工具调用"""
        payload = {
            "name": "chat_with_model",
            "arguments": {
                "input": "解释Python装饰器",
                "model": "qwen:7b"
            }
        }
        
        response = requests.post(f"{server_url}/mcp", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
```

### 3. 性能测试

```python
# tests/test_performance.py
import pytest
import asyncio
import time
import concurrent.futures
from typing import List

class TestPerformance:
    """性能测试"""
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """测试并发请求性能"""
        num_requests = 10
        
        async def make_request():
            # 模拟并发请求
            start = time.time()
            # 这里调用你的API
            end = time.time()
            return end - start
        
        # 创建并发任务
        tasks = [make_request() for _ in range(num_requests)]
        response_times = await asyncio.gather(*tasks)
        
        # 性能断言
        avg_response_time = sum(response_times) / len(response_times)
        assert avg_response_time < 5.0  # 平均响应时间应小于5秒
        assert max(response_times) < 10.0  # 最大响应时间应小于10秒
    
    def test_memory_usage(self):
        """测试内存使用情况"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 执行一些操作
        # ... 你的测试代码 ...
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # 内存增长不应超过合理范围
        assert memory_increase < 100  # 不超过100MB
```

## 🚀 VS Code 扩展开发

### 1. 扩展结构

```typescript
// extensions/src/extension.ts
import * as vscode from 'vscode';
import { McpClient } from './services/McpClient';
import { LocalModelsProvider } from './providers/LocalModelsProvider';

export function activate(context: vscode.ExtensionContext) {
    console.log('Local MCP Agent extension is now active!');
    
    // 初始化MCP客户端
    const mcpClient = new McpClient('http://localhost:8000');
    
    // 注册命令
    const askToolCommand = vscode.commands.registerCommand(
        'local-mcp-agent.askTool',
        async () => {
            const input = await vscode.window.showInputBox({
                prompt: '请输入您的问题',
                placeHolder: '例如：写一个Python快速排序算法'
            });
            
            if (input) {
                const result = await mcpClient.chat(input);
                showResultInNewDocument(result);
            }
        }
    );
    
    // 注册数据提供者
    const modelsProvider = new LocalModelsProvider(mcpClient);
    vscode.window.registerTreeDataProvider('localModels', modelsProvider);
    
    context.subscriptions.push(askToolCommand);
}

async function showResultInNewDocument(content: string) {
    const document = await vscode.workspace.openTextDocument({
        content: content,
        language: 'markdown'
    });
    
    await vscode.window.showTextDocument(document);
}
```

### 2. MCP 客户端服务

```typescript
// extensions/src/services/McpClient.ts
import axios, { AxiosInstance } from 'axios';

export interface ChatResponse {
    output: string;
    model: string;
    timestamp: number;
}

export interface McpToolResponse {
    status: string;
    data: any;
    execution_time: number;
}

export class McpClient {
    private client: AxiosInstance;
    
    constructor(baseUrl: string) {
        this.client = axios.create({
            baseURL: baseUrl,
            timeout: 30000,
            headers: {
                'Content-Type': 'application/json'
            }
        });
    }
    
    async chat(input: string, model: string = 'auto'): Promise<string> {
        try {
            const response = await this.client.post<ChatResponse>('/chat', {
                input,
                model
            });
            
            return response.data.output;
        } catch (error) {
            throw new Error(`Chat request failed: ${error}`);
        }
    }
    
    async callTool(name: string, arguments: any): Promise<any> {
        try {
            const response = await this.client.post<McpToolResponse>('/mcp', {
                name,
                arguments
            });
            
            if (response.data.status === 'success') {
                return response.data.data;
            } else {
                throw new Error(`Tool call failed: ${response.data}`);
            }
        } catch (error) {
            throw new Error(`MCP tool call failed: ${error}`);
        }
    }
    
    async getModels(): Promise<string[]> {
        try {
            const response = await this.client.get('/models');
            return response.data.models;
        } catch (error) {
            throw new Error(`Failed to get models: ${error}`);
        }
    }
    
    async getTools(): Promise<any[]> {
        try {
            const response = await this.client.get('/mcp/tools');
            return response.data;
        } catch (error) {
            throw new Error(`Failed to get tools: ${error}`);
        }
    }
}
```

## 📊 监控和日志

### 1. 日志配置

```python
# server/utils/logging_config.py
import logging
import logging.handlers
import os
from pathlib import Path

def setup_logging(
    level: str = "INFO",
    log_file: str = "logs/mcp_server.log",
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
):
    """配置日志系统"""
    
    # 创建日志目录
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 配置根日志器
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, level.upper()))
    
    # 清除现有处理器
    logger.handlers.clear()
    
    # 文件处理器（轮转）
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    
    # 格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# 使用示例
# from utils.logging_config import setup_logging
# logger = setup_logging(level="DEBUG")
```

### 2. 性能监控

```python
# server/utils/metrics.py
import time
import functools
from typing import Dict, Any
from collections import defaultdict

class MetricsCollector:
    """性能指标收集器"""
    
    def __init__(self):
        self.call_count: Dict[str, int] = defaultdict(int)
        self.execution_times: Dict[str, list] = defaultdict(list)
        self.error_count: Dict[str, int] = defaultdict(int)
        self.start_time = time.time()
    
    def record_call(self, function_name: str, execution_time: float, success: bool = True):
        """记录函数调用"""
        self.call_count[function_name] += 1
        self.execution_times[function_name].append(execution_time)
        
        if not success:
            self.error_count[function_name] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        stats = {
            "uptime_seconds": time.time() - self.start_time,
            "total_calls": sum(self.call_count.values()),
            "successful_calls": sum(self.call_count.values()) - sum(self.error_count.values()),
            "failed_calls": sum(self.error_count.values()),
            "functions": {}
        }
        
        for func_name in self.call_count:
            times = self.execution_times[func_name]
            if times:
                avg_time = sum(times) / len(times)
                max_time = max(times)
                min_time = min(times)
            else:
                avg_time = max_time = min_time = 0
            
            stats["functions"][func_name] = {
                "call_count": self.call_count[func_name],
                "error_count": self.error_count[func_name],
                "avg_execution_time": avg_time,
                "max_execution_time": max_time,
                "min_execution_time": min_time
            }
        
        return stats

# 全局指标收集器
metrics = MetricsCollector()

def monitor_performance(func_name: str = None):
    """性能监控装饰器"""
    def decorator(func):
        name = func_name or f"{func.__module__}.{func.__name__}"
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                raise
            finally:
                execution_time = time.time() - start_time
                metrics.record_call(name, execution_time, success)
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                raise
            finally:
                execution_time = time.time() - start_time
                metrics.record_call(name, execution_time, success)
        
        # 根据函数类型选择包装器
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

# 使用示例
@monitor_performance("chat_tool")
async def chat_with_model(input_text: str) -> str:
    # 你的实现
    pass
```

## 🔄 CI/CD 配置

### 1. GitHub Actions

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements-dev.txt
    
    - name: Lint with flake8
      run: |
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
    
    - name: Type check with mypy
      run: |
        mypy server/ tools/
    
    - name: Test with pytest
      run: |
        pytest tests/ --cov=server --cov=tools --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  build-extension:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
    
    - name: Install dependencies
      run: |
        cd extensions
        npm install
    
    - name: Build extension
      run: |
        cd extensions
        npm run compile
        npm run package
    
    - name: Upload extension artifact
      uses: actions/upload-artifact@v3
      with:
        name: vscode-extension
        path: extensions/*.vsix

  release:
    needs: [test, build-extension]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Create Release
      uses: actions/create-release@v1
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        tag_name: v${{ github.run_number }}
        release_name: Release v${{ github.run_number }}
        draft: false
        prerelease: false
```

## 📖 代码规范

### 1. Python 代码规范

```python
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
        language_version: python3.9
  
  - repo: https://github.com/pycqa/isort
    rev: 5.10.1
    hooks:
      - id: isort
        args: ["--profile", "black"]
  
  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8
        args: [--max-line-length=88, --extend-ignore=E203]
  
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v0.950
    hooks:
      - id: mypy
        additional_dependencies: [types-requests]
```

### 2. TypeScript 代码规范

```json
// extensions/.eslintrc.json
{
  "root": true,
  "parser": "@typescript-eslint/parser",
  "parserOptions": {
    "ecmaVersion": 6,
    "sourceType": "module"
  },
  "plugins": ["@typescript-eslint"],
  "rules": {
    "@typescript-eslint/naming-convention": "warn",
    "@typescript-eslint/semi": "warn",
    "curly": "warn",
    "eqeqeq": "warn",
    "no-throw-literal": "warn",
    "semi": "off"
  },
  "ignorePatterns": ["out", "dist", "**/*.d.ts"]
}
```

## 🤝 贡献指南

### 1. 提交代码

```bash
# 1. Fork 项目
# 2. 创建功能分支
git checkout -b feature/amazing-feature

# 3. 提交更改
git commit -m 'Add some amazing feature'

# 4. 推送到分支
git push origin feature/amazing-feature

# 5. 开启 Pull Request
```

### 2. Pull Request 模板

```markdown
## 变更描述
简要描述这个PR的内容

## 变更类型
- [ ] Bug 修复
- [ ] 新功能
- [ ] 重大变更
- [ ] 文档更新
- [ ] 性能改进

## 测试
- [ ] 单元测试通过
- [ ] 集成测试通过
- [ ] 手动测试完成

## 检查清单
- [ ] 代码遵循项目规范
- [ ] 自测试通过
- [ ] 文档已更新
- [ ] 变更日志已更新
```

---

这个开发者指南为项目贡献者提供了完整的开发环境设置、代码规范、测试策略和部署流程。按照这个指南，开发者可以快速上手并高效地为项目做出贡献。
