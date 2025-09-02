#!/bin/bash
# 健康检查脚本

echo "🔍 Local MCP Agent 健康检查"
echo "=========================="

# 检查服务器是否运行
if curl -s http://localhost:8000/health >/dev/null; then
    echo "✅ MCP 服务器运行正常"
    
    # 获取服务器信息
    echo ""
    echo "📊 服务器信息:"
    curl -s http://localhost:8000/health | python3 -m json.tool
    
    echo ""
    echo "🛠️ 可用工具:"
    curl -s http://localhost:8000/mcp/tools | python3 -c "
import sys, json
try:
    tools = json.load(sys.stdin)
    for i, tool in enumerate(tools, 1):
        print(f'  {i}. {tool[\"name\"]} - {tool[\"description\"]}')
except:
    print('  无法解析工具列表')
"
    
else
    echo "❌ MCP 服务器未运行"
    echo "请运行: ./scripts/start.sh"
    exit 1
fi

echo ""
echo "🎉 所有检查通过！"
