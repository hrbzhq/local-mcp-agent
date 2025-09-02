#!/bin/bash
# Local MCP Agent 启动脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Local MCP Agent 启动器${NC}"
echo "=================================="

# 检查 Python 版本
python_version=$(python3 --version 2>/dev/null | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.8"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3,8) else 1)" 2>/dev/null; then
    echo -e "${RED}❌ 需要 Python 3.8+ (当前: $python_version)${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python 版本检查通过: $python_version${NC}"

# 切换到服务器目录
cd "$(dirname "$0")/../server"

# 检查并创建虚拟环境
if [ ! -d "../.venv" ]; then
    echo -e "${YELLOW}📦 创建虚拟环境...${NC}"
    python3 -m venv ../.venv
fi

# 激活虚拟环境
echo -e "${YELLOW}🔧 激活虚拟环境...${NC}"
source ../.venv/bin/activate

# 安装依赖
if [ ! -f "../.venv/installed" ]; then
    echo -e "${YELLOW}📥 安装依赖包...${NC}"
    pip install -r requirements.txt
    touch ../.venv/installed
fi

# 检查端口是否被占用
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo -e "${YELLOW}⚠️  端口 8000 已被占用，尝试停止现有进程...${NC}"
    pkill -f "python.*main.py" || true
    sleep 2
fi

# 启动服务器
echo -e "${GREEN}🌐 启动 MCP 服务器 (端口 8000)...${NC}"
echo -e "${BLUE}💡 使用 Ctrl+C 停止服务器${NC}"
echo ""

# 启动服务器
python main.py

echo -e "${GREEN}🎉 服务器已启动！${NC}"
echo ""
echo -e "${BLUE}📋 接下来的步骤:${NC}"
echo "1. 打开 VS Code"
echo "2. 按 Ctrl+Shift+P"
echo "3. 输入 'MCP: Ask Tool'"
echo "4. 开始与 AI 对话！"
