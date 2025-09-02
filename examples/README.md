# 🎯 使用示例

这个目录包含了 Local MCP Agent 的各种使用示例，帮助您快速上手和集成。

## 📁 示例文件结构

```
examples/
├── basic/                  # 基础使用示例
│   ├── simple_chat.py     # 简单聊天示例
│   ├── model_selection.py # 模型选择示例
│   └── error_handling.py  # 错误处理示例
├── advanced/              # 高级功能示例
│   ├── collaborative_ai.py   # 多模型协作
│   ├── tool_chaining.py      # 工具链调用
│   └── performance_monitor.py # 性能监控
├── integrations/          # 集成示例
│   ├── flask_app.py       # Flask 应用集成
│   ├── django_integration.py # Django 集成
│   └── jupyter_notebook.ipynb # Jupyter 笔记本
├── vscode/               # VS Code 扩展示例
│   ├── custom_commands.ts # 自定义命令
│   └── panel_integration.ts # 面板集成
└── scripts/              # 实用脚本
    ├── batch_processing.py # 批量处理
    ├── model_benchmark.py  # 模型性能测试
    └── data_export.py      # 数据导出
```

## 🚀 快速开始

### 1. 基础聊天示例

```python
# basic/simple_chat.py
import requests

# 简单的聊天功能
response = requests.post("http://localhost:8000/chat", json={
    "input": "Hello, how are you?",
    "model": "auto"
})

print(response.json()["output"])
```

### 2. 模型协作示例

```python
# advanced/collaborative_ai.py
import requests

# 多个AI模型协作解决问题
response = requests.post("http://localhost:8000/mcp", json={
    "name": "collaborative_chat",
    "arguments": {
        "input": "设计一个微服务架构",
        "models": ["qwen:7b", "deepseek-coder:6.7b"],
        "max_rounds": 3
    }
})

print(response.json()["data"]["collaboration_summary"]["final_output"])
```

### 3. VS Code 扩展集成

```typescript
// vscode/custom_commands.ts
import * as vscode from 'vscode';

// 注册自定义命令
const command = vscode.commands.registerCommand('myExtension.askAI', async () => {
    const input = await vscode.window.showInputBox({
        prompt: 'Ask AI anything'
    });
    
    if (input) {
        // 调用 MCP API
        // 显示结果
    }
});
```

## 📋 运行示例

1. **确保服务器运行**:
   ```bash
   cd local-mcp-agent
   python server/api_server.py
   ```

2. **安装依赖**:
   ```bash
   pip install requests
   ```

3. **运行示例**:
   ```bash
   python examples/basic/simple_chat.py
   ```

## 🤝 贡献示例

欢迎贡献更多使用示例！请参考 [贡献指南](../docs/DEVELOPMENT.md)。

每个示例都应该包含：
- 清晰的代码注释
- 运行说明
- 期望输出
- 错误处理
