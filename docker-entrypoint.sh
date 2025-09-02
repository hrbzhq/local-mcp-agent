#!/bin/bash
set -e

# Local MCP Agent Docker 启动脚本

echo "🚀 Starting Local MCP Agent..."

# 检查环境变量
echo "📋 Environment Configuration:"
echo "   HOST: ${HOST:-0.0.0.0}"
echo "   PORT: ${PORT:-8000}"
echo "   DEBUG: ${DEBUG:-false}"
echo "   CONFIG_FILE: ${CONFIG_FILE:-config/basic.json}"

# 等待 Ollama 服务 (如果配置了)
if [ ! -z "$OLLAMA_HOST" ]; then
    echo "⏳ Waiting for Ollama service at $OLLAMA_HOST..."
    until curl -f "$OLLAMA_HOST/api/tags" >/dev/null 2>&1; do
        echo "   Ollama not ready, waiting..."
        sleep 2
    done
    echo "✅ Ollama service is ready"
fi

# 检查配置文件
if [ ! -f "$CONFIG_FILE" ]; then
    echo "⚠️  Configuration file not found: $CONFIG_FILE"
    echo "   Using default configuration..."
    CONFIG_FILE="config/basic.json"
fi

echo "📝 Using config: $CONFIG_FILE"

# 创建日志目录
mkdir -p logs

# 启动应用
echo "🎯 Starting MCP Server..."
exec "$@"
