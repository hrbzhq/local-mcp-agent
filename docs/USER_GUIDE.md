# 📖 用户使用指南

## 🎯 快速开始

### 1. 系统要求

- **操作系统**: Windows 10/11, macOS 10.15+, Ubuntu 18.04+
- **Python**: 3.9 或更高版本
- **Ollama**: 必须预先安装并运行
- **VS Code**: 1.85.0 或更高版本（可选，用于扩展集成）

### 2. 安装步骤

#### 方法一：自动安装脚本

**Windows (PowerShell)**:
```powershell
# 克隆项目
git clone https://github.com/your-org/local-mcp-agent.git
cd local-mcp-agent

# 运行安装脚本
.\scripts\setup.ps1
```

**Linux/macOS**:
```bash
# 克隆项目
git clone https://github.com/your-org/local-mcp-agent.git
cd local-mcp-agent

# 运行安装脚本
chmod +x scripts/setup.sh
./scripts/setup.sh
```

#### 方法二：手动安装

```bash
# 1. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置服务
cp config/basic.json config/config.json

# 4. 启动服务
python server/api_server.py
```

### 3. 验证安装

安装完成后，打开浏览器访问：
- **健康检查**: http://localhost:8000/health
- **服务信息**: http://localhost:8000/info
- **可用模型**: http://localhost:8000/models

看到类似以下响应表示安装成功：
```json
{
  "status": "healthy",
  "server_name": "Local Multi-Model AI Gateway",
  "tools_registered": 3
}
```

## 🎮 基础使用

### 场景一：命令行聊天

```bash
# 直接 API 调用
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "input": "写一个Python的Hello World程序",
    "model": "auto"
  }'
```

### 场景二：Python 脚本集成

```python
import requests

# 连接到本地 MCP 服务
class MCPClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def chat(self, message, model="auto"):
        response = requests.post(f"{self.base_url}/chat", json={
            "input": message,
            "model": model
        })
        return response.json()["output"]
    
    def get_models(self):
        response = requests.get(f"{self.base_url}/models")
        return response.json()["models"]

# 使用示例
client = MCPClient()

# 自动选择模型
answer = client.chat("解释什么是机器学习")
print(answer)

# 指定模型
code = client.chat("写一个快速排序算法", model="deepseek-coder:6.7b")
print(code)

# 查看可用模型
models = client.get_models()
print(f"可用模型: {models}")
```

### 场景三：VS Code 集成

1. **安装扩展**:
   - 打开 VS Code
   - 按 `Ctrl+Shift+P` 打开命令面板
   - 运行 `Extensions: Install from VSIX...`
   - 选择 `extensions/local-mcp-agent.vsix`

2. **使用扩展**:
   - `Ctrl+Shift+P` → `MCP: Ask Tool` - 与 AI 对话
   - `Ctrl+Shift+P` → `MCP: List Tools` - 查看可用工具
   - `Ctrl+Shift+P` → `MCP: List Models` - 查看可用模型

## 🛠️ 高级功能

### 1. 多模型协作

让多个 AI 模型协作解决复杂问题：

```python
import requests

def collaborative_solve(problem, models=None):
    if models is None:
        models = ["qwen:7b", "deepseek-coder:6.7b"]
    
    response = requests.post("http://localhost:8000/mcp", json={
        "name": "collaborative_chat",
        "arguments": {
            "input": problem,
            "models": models,
            "max_rounds": 3,
            "strategy": "sequential"
        }
    })
    
    return response.json()["data"]["collaboration_summary"]

# 使用协作模式解决复杂问题
result = collaborative_solve(
    "设计一个分布式缓存系统，包括架构、关键技术和实现方案",
    models=["qwen:7b", "deepseek-coder:6.7b"]
)

print("协作结果:")
print(result["final_output"])
print("\n各模型贡献:")
for contrib in result["contributions"]:
    print(f"- {contrib['model']}: {contrib['summary']}")
```

### 2. 自定义配置

根据需要调整服务配置：

```bash
# 复制并编辑配置文件
cp config/basic.json config/my-config.json

# 编辑配置
{
  "server": {
    "host": "0.0.0.0",  // 允许外部访问
    "port": 8000,
    "debug": false,
    "cors_enabled": true
  },
  "mcp": {
    "max_tools": 10,    // 增加工具数量
    "tool_timeout": 60,
    "enable_monitoring": true
  },
  "auth": {
    "enabled": true,    // 启用认证
    "api_keys": ["your-secret-key"]
  }
}

# 使用自定义配置启动
CONFIG_FILE=config/my-config.json python server/api_server.py
```

### 3. 智能模型选择

系统可以根据输入内容自动选择最适合的模型：

```python
# 自动模型选择的例子
queries = [
    "写一个Python爬虫程序",           # 会选择 deepseek-coder
    "解释量子物理的基本概念",          # 会选择 qwen
    "翻译这段英文：Hello World",      # 会选择通用模型
    "优化这个SQL查询语句",            # 会选择 deepseek-coder
]

for query in queries:
    response = requests.post("http://localhost:8000/chat", json={
        "input": query,
        "model": "auto"  # 自动选择
    })
    
    result = response.json()
    print(f"查询: {query}")
    print(f"选择的模型: {result['model']}")
    print(f"回答: {result['output'][:100]}...")
    print("-" * 50)
```

## 🎨 实际应用案例

### 案例1：代码审查助手

```python
def code_review_assistant(code, language="python"):
    """AI 代码审查助手"""
    
    # 使用编程专用模型
    review_prompt = f"""
请审查以下{language}代码，提供：
1. 代码质量评估
2. 潜在问题和改进建议
3. 最佳实践建议

代码：
{code}
"""
    
    response = requests.post("http://localhost:8000/chat", json={
        "input": review_prompt,
        "model": "deepseek-coder:6.7b",
        "temperature": 0.3  # 更确定的回答
    })
    
    return response.json()["output"]

# 使用示例
code = """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr
"""

review = code_review_assistant(code)
print(review)
```

### 案例2：技术文档生成器

```python
def generate_documentation(code_function, style="detailed"):
    """为代码函数生成技术文档"""
    
    doc_prompt = f"""
为以下函数生成{style}的技术文档，包括：
1. 函数描述
2. 参数说明
3. 返回值说明
4. 使用示例
5. 注意事项

函数代码：
{code_function}
"""
    
    # 使用协作模式：一个模型分析代码，另一个模型美化文档
    response = requests.post("http://localhost:8000/mcp", json={
        "name": "collaborative_chat",
        "arguments": {
            "input": doc_prompt,
            "models": ["deepseek-coder:6.7b", "qwen:7b"],
            "max_rounds": 2,
            "strategy": "sequential"
        }
    })
    
    return response.json()["data"]["collaboration_summary"]["final_output"]

# 使用示例
function_code = """
def calculate_fibonacci(n, memo=None):
    if memo is None:
        memo = {}
    
    if n in memo:
        return memo[n]
    
    if n <= 1:
        return n
    
    memo[n] = calculate_fibonacci(n-1, memo) + calculate_fibonacci(n-2, memo)
    return memo[n]
"""

docs = generate_documentation(function_code)
print(docs)
```

### 案例3：多语言学习助手

```python
def language_learning_chat(text, target_language, difficulty="intermediate"):
    """多语言学习聊天助手"""
    
    learning_prompt = f"""
作为一个{target_language}学习助手，请：

1. 翻译以下文本："{text}"
2. 解释关键词汇和语法点
3. 提供{difficulty}级别的相关练习
4. 给出文化背景说明（如适用）

请使用中文解释，但{target_language}的例句请用原语言。
"""
    
    response = requests.post("http://localhost:8000/chat", json={
        "input": learning_prompt,
        "model": "qwen:7b",  # 使用多语言能力强的模型
        "temperature": 0.8   # 允许更多创造性
    })
    
    return response.json()["output"]

# 使用示例
lesson = language_learning_chat(
    "I love programming and artificial intelligence",
    target_language="French",
    difficulty="beginner"
)
print(lesson)
```

## 🔧 故障排除

### 常见问题及解决方案

#### 1. 服务无法启动

**问题**: `ModuleNotFoundError: No module named 'fastapi'`

**解决方案**:
```bash
# 确保在正确的虚拟环境中
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# 重新安装依赖
pip install -r requirements.txt
```

#### 2. Ollama 连接失败

**问题**: `ConnectionError: Ollama service not available`

**解决方案**:
```bash
# 检查 Ollama 是否运行
ollama list

# 如果未运行，启动 Ollama
ollama serve

# 拉取所需模型（如果尚未安装）
ollama pull qwen:7b
ollama pull deepseek-coder:6.7b
```

#### 3. VS Code 扩展无法工作

**问题**: 扩展已安装但命令不可用

**解决方案**:
1. 重启 VS Code
2. 检查扩展是否启用：`Ctrl+Shift+X` → 搜索 "Local MCP Agent"
3. 查看开发者控制台：`Help` → `Toggle Developer Tools`
4. 重新安装扩展：卸载后从 `.vsix` 文件重新安装

#### 4. 性能问题

**问题**: 响应速度慢或超时

**解决方案**:
```bash
# 检查系统资源
# Windows
tasklist | findstr ollama

# Linux/macOS  
ps aux | grep ollama

# 调整配置以减少超时
# 编辑 config/config.json
{
  "mcp": {
    "tool_timeout": 120,  // 增加超时时间
    "max_concurrent": 2   // 减少并发数
  }
}
```

#### 5. 模型选择错误

**问题**: 自动模型选择不准确

**解决方案**:
```python
# 强制指定模型而非使用 "auto"
response = requests.post("http://localhost:8000/chat", json={
    "input": "写代码",
    "model": "deepseek-coder:6.7b"  # 明确指定
})

# 或者调整模型选择逻辑
# 编辑 server/model_manager.py 中的选择规则
```

### 日志查看

```bash
# 查看服务器日志
tail -f logs/mcp_server.log

# 或者在调试模式下运行
DEBUG=1 python server/api_server.py
```

### 性能监控

```bash
# 获取服务器统计信息
curl http://localhost:8000/stats

# 查看详细性能指标
curl http://localhost:8000/health
```

## 📚 进阶参考

- **[架构文档](ARCHITECTURE.md)** - 了解系统设计和技术细节
- **[API 文档](API.md)** - 完整的 API 接口说明
- **[开发指南](DEVELOPMENT.md)** - 参与项目开发
- **[性能优化](OPTIMIZATION.md)** - 系统性能调优指南

## 💬 社区支持

- **GitHub Issues**: 报告问题和功能请求
- **Discussions**: 技术讨论和使用经验分享
- **Wiki**: 社区维护的使用技巧和最佳实践

---

**提示**: 这个指南涵盖了大部分使用场景。如果遇到特殊需求或问题，请查看其他文档或在 GitHub 上提出 Issue。
