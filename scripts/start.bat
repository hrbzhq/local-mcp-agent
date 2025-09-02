@echo off
REM Local MCP Agent 启动脚本 (Windows)

echo 🚀 Local MCP Agent 启动器
echo ==================================

REM 检查 Python 版本
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到 Python，请安装 Python 3.8+
    pause
    exit /b 1
)

echo ✅ Python 版本检查通过

REM 切换到服务器目录
cd /d "%~dp0\..\server"

REM 检查并创建虚拟环境
if not exist "..\\.venv" (
    echo 📦 创建虚拟环境...
    python -m venv ..\.venv
)

REM 激活虚拟环境
echo 🔧 激活虚拟环境...
call ..\\.venv\\Scripts\\activate.bat

REM 安装依赖
if not exist "..\\.venv\\installed" (
    echo 📥 安装依赖包...
    pip install -r requirements.txt
    echo. > ..\\.venv\\installed
)

REM 检查端口是否被占用
netstat -an | find "8000" | find "LISTENING" >nul
if not errorlevel 1 (
    echo ⚠️  端口 8000 已被占用，请手动停止相关进程
)

REM 启动服务器
echo 🌐 启动 MCP 服务器 (端口 8000)...
echo 💡 使用 Ctrl+C 停止服务器
echo.

python main.py

echo 🎉 服务器已启动！
echo.
echo 📋 接下来的步骤:
echo 1. 打开 VS Code
echo 2. 按 Ctrl+Shift+P
echo 3. 输入 'MCP: Ask Tool'
echo 4. 开始与 AI 对话！

pause
